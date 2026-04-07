"""
Ingestion — Skill Extraction (Intelligence)
Responsable: Diego Vargas Urzagaste (@temps-code)

Extrae habilidades técnicas desde descripciones de vacantes Adzuna
usando Groq LLM (primary) + regex fallback (resilience).

Output: data/processed/empleos/skills_extracted.csv

Arquitectura:
- SkillExtractor: clase principal, orquestación
- Groq: extracción inteligente (primary, 90%+)
- Regex: fallback robusto cuando Groq falla
- CSV cache: reutilizable entre runs
"""

import logging
import json
import os
import time
import re
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Set

import pandas as pd
from groq import Groq
from groq._exceptions import RateLimitError
from requests.exceptions import Timeout


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
ch.setFormatter(formatter)
logger.addHandler(ch)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

GROQ_MODEL = "llama-3.1-8b-instant"

# 30+ technical skills (extensible)
KNOWN_SKILLS: Set[str] = {
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "PHP", "Ruby", "Kotlin", "Swift", "SQL",
    # Frameworks & Libraries
    "React", "Vue.js", "Angular", "Django", "Flask", "Express.js", "FastAPI",
    "Node.js", ".NET", "Laravel", "Spring Boot", "Next.js",
    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLServer", "Cassandra",
    "DynamoDB", "Elasticsearch",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins",
    "GitHub Actions", "GitLab CI", "Ansible", "CloudFormation",
    # Big Data & Analytics
    "Spark", "Hadoop", "Kafka", "Airflow", "Snowflake", "BigQuery", "Databricks",
    "PySpark",
    # Data Science & ML
    "Machine Learning", "TensorFlow", "PyTorch", "Scikit-learn", "XGBoost",
    "Pandas", "NumPy", "Matplotlib", "Plotly", "Jupyter",
    # APIs & Integration
    "REST API", "GraphQL", "SOAP", "Microservices", "gRPC",
    # Other
    "Git", "GitHub", "GitLab", "Agile", "Scrum", "JIRA", "Stripe", "OAuth",
    "JWT", "SSL/TLS", "Linux", "Windows", "Mac",
}

# Regex patterns for skill matching (precedence matters: java BEFORE javascript)
REGEX_PATTERNS: Dict[str, str] = {
    # Precise patterns first
    "java": r"\bjava\b",  # NOT javascript
    "javascript": r"\b(javascript|js|node\.?js)\b",
    "typescript": r"\btypescript\b",
    "python": r"\bpython\b",
    "sql": r"\bsql\b",
    "mongodb": r"\b(mongodb|mongo)\b",
    "postgresql": r"\bpostgres(ql)?\b",
    "mysql": r"\bmysql\b",
    "redis": r"\bredis\b",
    "sqlserver": r"\b(sqlserver|sql\s+server|mssql)\b",
    "react": r"\breact\b",
    "vue": r"\bvue(\.?js)?\b",
    "angular": r"\bangular\b",
    "django": r"\bdjango\b",
    "flask": r"\bflask\b",
    "express": r"\bexpress(\.js)?\b",
    "node": r"\bnode(\.?js)?\b",
    "fastapi": r"\bfastapi\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\b(kubernetes|k8s)\b",
    "aws": r"\b(aws|amazon\s+web\s+services)\b",
    "azure": r"\b(azure|microsoft\s+azure)\b",
    "gcp": r"\b(gcp|google\s+cloud)\b",
    "git": r"\bgit\b",
    "github": r"\bgithub\b",
    "tensorflow": r"\btensorflow\b",
    "pytorch": r"\bpytorch\b",
    "pandas": r"\bpandas\b",
    "spark": r"\bapache\s+spark|\bspark\b",
    "kafka": r"\bapache\s+kafka|\bkafka\b",
    "rest": r"\brest\s+api\b",
    "graphql": r"\bgraphql\b",
    "microservices": r"\bmicroservices\b",
    "machine learning": r"\b(machine\s+learning|ml)\b",
    "ai": r"\b(artificial\s+intelligence|ai)\b",
    "etl": r"\betl\b",
    "cicd": r"\b(ci[/\-]?cd|continuous\s+(integration|deployment))\b",
}

# Confidence scores by extraction method
CONFIDENCE_MAP: Dict[str, float] = {
    "groq": 0.92,
    "regex": 0.65,
    "fallback_error": 0.0,
}


# ─────────────────────────────────────────────────────────────────────────────
# EXCEPTIONS
# ─────────────────────────────────────────────────────────────────────────────

class SkillExtractionError(Exception):
    """Base exception for skill extraction errors."""
    pass


class InputValidationError(SkillExtractionError):
    """Input DataFrame validation failed."""
    pass


class GroqAPIError(SkillExtractionError):
    """Groq API error (rate limit, timeout, auth, etc)."""
    pass


class OutputValidationError(SkillExtractionError):
    """Output schema or content validation failed."""
    pass


class PersistenceError(SkillExtractionError):
    """File I/O error (read/write CSV)."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SkillExtractionConfig:
    """Configuration for SkillExtractor."""
    use_groq: bool = field(default_factory=lambda: os.getenv("USE_GROQ", "true") == "true")
    batch_size: int = field(default_factory=lambda: int(os.getenv("SKILL_EXTRACTION_BATCH_SIZE", "25")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("SKILL_EXTRACTION_MAX_RETRIES", "3")))
    timeout: int = field(default_factory=lambda: int(os.getenv("SKILL_EXTRACTION_TIMEOUT", "30")))
    cache_path: Path = field(default_factory=lambda: Path(os.getenv("SKILL_EXTRACTION_CACHE_PATH", "data/processed/empleos/skills_extracted.csv")))


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def parse_groq_response(response_text: str) -> Dict[str, List[str]]:
    """
    Parse Groq JSON response.
    
    Expected format:
    {
      "desc_1": ["skill1", "skill2"],
      "desc_2": ["skill3"],
      ...
    }
    
    Returns:
        Dict mapping "desc_N" to list of skills
    
    Raises:
        json.JSONDecodeError if response not valid JSON
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Groq response as JSON: {str(e)}")
        logger.debug(f"Response text: {response_text[:200]}...")
        raise


def apply_regex_patterns(description: str) -> List[str]:
    """
    Apply regex patterns to extract tech skills from description.
    
    Args:
        description: Job description text
    
    Returns:
        List of matched skills (normalized, deduplicated)
    """
    if not description or not isinstance(description, str):
        return []
    
    matched_skills: Set[str] = set()
    desc_lower = description.lower()
    
    for skill_name, pattern in REGEX_PATTERNS.items():
        try:
            if re.search(pattern, desc_lower, re.IGNORECASE):
                matched_skills.add(skill_name)
        except re.error as e:
            logger.warning(f"Regex error for pattern '{skill_name}': {str(e)}")
    
    return sorted(list(matched_skills))


def skill_title_case(skill: str) -> str:
    """Normalize skill name to title case."""
    # Special mappings
    mappings = {
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "sqlserver": "SQL Server",
        "mongodb": "MongoDB",
        "graphql": "GraphQL",
        "rest api": "REST API",
        "machine learning": "Machine Learning",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "scikit-learn": "Scikit-learn",
        "c++": "C++",
        "c#": "C#",
        ".net": ".NET",
        "aws": "AWS",
        "gcp": "GCP",
        "cicd": "CI/CD",
        "jwt": "JWT",
        "ssl/tls": "SSL/TLS",
        "ui/ux": "UI/UX",
    }
    
    skill_lower = skill.lower().strip()
    return mappings.get(skill_lower, skill.title())


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CLASS: SkillExtractor
# ─────────────────────────────────────────────────────────────────────────────

class SkillExtractor:
    """
    Extrae habilidades técnicas desde descripciones Adzuna usando Groq + regex.
    
    Architecture:
    - Primary: Groq LLM (intelligent, contextual, 92% confidence)
    - Fallback: Regex patterns (robust, 65% confidence)
    - Cache: skills_extracted.csv (avoid repetitive Groq calls)
    
    Ejemplo:
        extractor = SkillExtractor(use_groq=True)
        vacantes_df = pd.read_csv("data/raw/empleos/vacantes_tecnologicas.csv")
        result_df = extractor.execute(vacantes_df)
    """
    
    def __init__(
        self,
        use_groq: bool = True,
        cache_path: str = "data/processed/empleos/skills_extracted.csv",
        batch_size: int = 25,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize SkillExtractor.
        
        Args:
            use_groq: Enable Groq LLM extraction
            cache_path: Path to CSV cache
            batch_size: N descriptions per Groq request
            max_retries: Retry attempts on timeout/rate limit
            timeout: Request timeout in seconds
        
        Raises:
            GroqAPIError: If use_groq=True but GROQ_API_KEY not set
        """
        self.use_groq = use_groq
        self.cache_path = Path(cache_path)
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Initialize Groq client (if needed)
        if self.use_groq:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise GroqAPIError("GROQ_API_KEY not found in environment. Set it or use use_groq=False")
            self.groq_client = Groq(api_key=api_key, timeout=timeout)
        else:
            self.groq_client = None
        
        logger.info(f"SkillExtractor initialized (use_groq={use_groq}, batch_size={batch_size})")
    
    def _validate_input(self, vacantes_df: pd.DataFrame) -> None:
        """
        Validate input DataFrame.
        
        Raises:
            InputValidationError: If validation fails
        """
        # Check empty
        if vacantes_df.empty:
            raise InputValidationError("vacantes_df is empty")
        
        # Check required columns
        required_cols = ["job_id", "title", "description"]
        missing_cols = [c for c in required_cols if c not in vacantes_df.columns]
        if missing_cols:
            raise InputValidationError(f"Missing columns: {missing_cols}")
        
        # Check description validity
        invalid_count = vacantes_df["description"].isna().sum()
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} NaN descriptions")
        
        # Validate description length
        for idx, desc in vacantes_df["description"].items():
            if pd.isna(desc):
                continue
            desc_str = str(desc).strip()
            if len(desc_str) < 20:
                logger.warning(f"Job {idx}: Description too short ({len(desc_str)} chars)")
        
        logger.info(f"Input validated: {len(vacantes_df)} jobs")
    
    def _load_cache_if_exists(self) -> Optional[pd.DataFrame]:
        """
        Load cached skills if exists.
        
        Returns:
            DataFrame if cache exists and valid, None otherwise
        """
        if not self.cache_path.exists():
            logger.debug(f"Cache not found: {self.cache_path}")
            return None
        
        try:
            cache_df = pd.read_csv(self.cache_path)
            expected_cols = ["job_id", "title", "description", "skills_json", "extraction_method", 
                           "extraction_timestamp", "confidence", "error_message"]
            if not all(c in cache_df.columns for c in expected_cols):
                logger.warning("Cache schema invalid, regenerating")
                return None
            
            logger.info(f"✅ Cache hit: loaded {len(cache_df)} jobs from {self.cache_path}")
            return cache_df
        
        except Exception as e:
            logger.warning(f"Error loading cache: {str(e)}, regenerating")
            return None
    
    def _build_groq_prompt(self, descriptions: List[str]) -> str:
        """
        Build Groq prompt for batch extraction.
        
        Args:
            descriptions: List of job descriptions (max 25)
        
        Returns:
            Formatted prompt string
        """
        desc_text = "\n".join([
            f'Descripción {idx+1}: "{desc.strip()[:300]}"'  # Truncate to 300 chars
            for idx, desc in enumerate(descriptions)
        ])
        
        prompt = f"""De las siguientes descripciones de puestos de trabajo, extrae SOLO habilidades técnicas y herramientas específicas.
Máximo 8 skills por descripción. NO incluyas skills genéricas (comunicación, trabajo en equipo) ni soft skills.

{desc_text}

Responde en formato JSON exactamente así (sin markdown, sin explicaciones):
{{
  "desc_1": ["skill1", "skill2", ...],
  "desc_2": [...],
  ...
}}

Si no hay skills técnicas identificables en una descripción, usa array vacío: [].
Normaliza nombres: "Python" no "python", "Node.js" no "nodejs", "C++" no "cpp"."""
        
        return prompt
    
    def _retry_groq_call(self, prompt: str, attempt: int = 0) -> Optional[str]:
        """
        Call Groq API with exponential backoff retry.
        
        Args:
            prompt: Prompt text
            attempt: Current attempt number (0-based)
        
        Returns:
            Response text or None if all retries failed
        """
        try:
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Low randomness for deterministic extraction
                max_tokens=1000,
            )
            return response.choices[0].message.content
        
        except RateLimitError as e:
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Rate limited (429), retry {attempt+1}/{self.max_retries} in {wait_time}s...")
                time.sleep(wait_time)
                return self._retry_groq_call(prompt, attempt + 1)
            else:
                logger.error(f"Rate limit exhausted after {self.max_retries} retries")
                return None
        
        except Timeout:
            if attempt < self.max_retries - 1:
                logger.warning(f"Timeout, retry {attempt+1}/{self.max_retries}...")
                return self._retry_groq_call(prompt, attempt + 1)
            else:
                logger.error(f"Timeout exhausted after {self.max_retries} retries")
                return None
        
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return None
    
    def _extract_groq_batch(self, job_ids: List[str], descriptions: List[str]) -> Optional[List[Dict]]:
        """
        Extract skills using Groq LLM (batch).
        
        Args:
            job_ids: List of job IDs (max 25)
            descriptions: List of descriptions (max 25)
        
        Returns:
            List of result dicts or None if error
        """
        try:
            # Build prompt
            prompt = self._build_groq_prompt(descriptions)
            
            # Call Groq with retry
            response_text = self._retry_groq_call(prompt)
            if not response_text:
                return None
            
            # Parse response
            skills_dict = parse_groq_response(response_text)
            
            # Build rows
            rows = []
            for idx, job_id in enumerate(job_ids):
                key = f"desc_{idx+1}"
                skills = skills_dict.get(key, [])
                skills = self._normalize_skills(skills)
                
                rows.append({
                    "job_id": job_id,
                    "skills_json": json.dumps(skills),
                    "extraction_method": "groq",
                    "confidence": CONFIDENCE_MAP["groq"],
                    "error_message": "",
                    "extraction_timestamp": datetime.now().isoformat(),
                })
            
            return rows
        
        except Exception as e:
            logger.warning(f"Groq batch extraction failed: {str(e)}")
            return None
    
    def _extract_regex_fallback(self, job_ids: List[str], descriptions: List[str]) -> List[Dict]:
        """
        Extract skills using regex fallback.
        
        Args:
            job_ids: List of job IDs
            descriptions: List of descriptions
        
        Returns:
            List of result dicts
        """
        rows = []
        for job_id, desc in zip(job_ids, descriptions):
            skills = apply_regex_patterns(desc)
            skills = self._normalize_skills(skills)
            confidence = min(len(skills) / 10, 0.80) if skills else CONFIDENCE_MAP["regex"]
            
            rows.append({
                "job_id": job_id,
                "skills_json": json.dumps(skills),
                "extraction_method": "regex",
                "confidence": confidence,
                "error_message": "Groq extraction failed, fallback to regex",
                "extraction_timestamp": datetime.now().isoformat(),
            })
        
        return rows
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skill names.
        
        Args:
            skills: List of skills
        
        Returns:
            Normalized list (title case, deduplicated, max 8)
        """
        if not skills:
            return []
        
        # Title case + deduplicate
        normalized: Set[str] = set()
        for skill in skills:
            if isinstance(skill, str):
                normalized.add(skill_title_case(skill))
        
        # Sort and limit to 8
        return sorted(list(normalized))[:8]
    
    def _validate_output(self, result_df: pd.DataFrame) -> None:
        """
        Validate output schema and content.
        
        Raises:
            OutputValidationError: If validation fails
        """
        expected_cols = [
            "job_id", "title", "description", "skills_json", "extraction_method",
            "extraction_timestamp", "confidence", "error_message"
        ]
        
        # Check columns
        missing = [c for c in expected_cols if c not in result_df.columns]
        if missing:
            raise OutputValidationError(f"Missing columns: {missing}")
        
        # Validate each row
        for idx, row in result_df.iterrows():
            # Check JSON parseable
            try:
                json.loads(row["skills_json"])
            except json.JSONDecodeError as e:
                raise OutputValidationError(f"Row {idx}: skills_json not valid JSON: {str(e)}")
            
            # Check extraction_method
            if row["extraction_method"] not in ["groq", "regex", "fallback_error"]:
                raise OutputValidationError(f"Row {idx}: invalid extraction_method={row['extraction_method']}")
            
            # Check confidence
            if not (0.0 <= row["confidence"] <= 1.0):
                raise OutputValidationError(f"Row {idx}: confidence out of range: {row['confidence']}")
        
        logger.info(f"Output validated: {len(result_df)} rows, all JSON parseable, schema OK")
    
    def _save_csv(self, result_df: pd.DataFrame) -> None:
        """
        Save result DataFrame to CSV.
        
        Args:
            result_df: Result DataFrame
        
        Raises:
            PersistenceError: If save fails
        """
        try:
            # Validate first
            self._validate_output(result_df)
            
            # Create parent directory
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write CSV
            result_df.to_csv(self.cache_path, index=False, encoding="utf-8")
            
            logger.info(f"✅ Output saved: {self.cache_path} ({len(result_df)} rows)")
        
        except Exception as e:
            raise PersistenceError(f"Failed to save CSV: {str(e)}")
    
    def execute(self, vacantes_df: pd.DataFrame) -> pd.DataFrame:
        """
        Main execution pipeline.
        
        Args:
            vacantes_df: DataFrame with columns [job_id, title, description, ...]
        
        Returns:
            Result DataFrame with skills extracted
        
        Raises:
            SkillExtractionError: If critical error occurs
        """
        start_time = time.time()
        
        try:
            # 1. VALIDATE INPUT
            logger.info("Starting skill extraction...")
            self._validate_input(vacantes_df)
            
            # 2. CHECK CACHE
            cached = self._load_cache_if_exists()
            if cached is not None:
                elapsed = time.time() - start_time
                logger.info(f"✅ Extraction complete (cache reuse): {elapsed:.1f}s")
                return cached
            
            # 3. BATCH & EXTRACT
            all_results = []
            total_batches = (len(vacantes_df) + self.batch_size - 1) // self.batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(vacantes_df))
                
                batch_df = vacantes_df.iloc[start_idx:end_idx]
                job_ids = batch_df["job_id"].tolist()
                descriptions = batch_df["description"].tolist()
                
                logger.debug(f"Batch {batch_idx+1}/{total_batches}: {len(job_ids)} jobs")
                
                # Try Groq first
                if self.use_groq:
                    groq_results = self._extract_groq_batch(job_ids, descriptions)
                    if groq_results:
                        all_results.extend(groq_results)
                        continue
                
                # Fallback: Regex
                logger.debug(f"Batch {batch_idx+1}: Groq failed, using regex")
                regex_results = self._extract_regex_fallback(job_ids, descriptions)
                all_results.extend(regex_results)
            
            # 4. CREATE DATAFRAME
            result_df = pd.DataFrame(all_results)
            
            # Merge back title and description
            result_df = result_df.merge(
                vacantes_df[["job_id", "title", "description"]], 
                on="job_id", 
                how="left"
            )
            
            # 5. VALIDATE OUTPUT
            self._validate_output(result_df)
            
            # 6. SAVE CSV
            self._save_csv(result_df)
            
            # 7. LOG SUMMARY
            elapsed = time.time() - start_time
            groq_count = (result_df["extraction_method"] == "groq").sum()
            regex_count = (result_df["extraction_method"] == "regex").sum()
            groq_pct = (groq_count / len(result_df) * 100) if len(result_df) > 0 else 0
            
            logger.info(
                f"✅ Extraction complete:\n"
                f"  Total: {len(result_df)} jobs\n"
                f"  Groq: {groq_count} ({groq_pct:.1f}%)\n"
                f"  Regex: {regex_count}\n"
                f"  Time: {elapsed:.1f}s"
            )
            
            return result_df
        
        except Exception as e:
            logger.error(f"Critical error in execute(): {str(e)}", exc_info=True)
            raise


# ─────────────────────────────────────────────────────────────────────────────
# CONVENIENCE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def execute_extraction(
    vacantes_df: Optional[pd.DataFrame] = None,
    use_groq: bool = True,
    cache_path: str = "data/processed/empleos/skills_extracted.csv",
) -> pd.DataFrame:
    """
    Convenience function to run skill extraction.
    
    If vacantes_df is None, loads from data/raw/empleos/vacantes_tecnologicas.csv
    
    Args:
        vacantes_df: Input DataFrame or None (loads from raw)
        use_groq: Enable Groq extraction
        cache_path: Cache CSV path
    
    Returns:
        Result DataFrame with extracted skills
    """
    if vacantes_df is None:
        vacantes_path = Path("data/raw/empleos/vacantes_tecnologicas.csv")
        if not vacantes_path.exists():
            raise FileNotFoundError(f"vacantes file not found: {vacantes_path}")
        vacantes_df = pd.read_csv(vacantes_path)
    
    extractor = SkillExtractor(use_groq=use_groq, cache_path=cache_path)
    return extractor.execute(vacantes_df)


if __name__ == "__main__":
    # Example usage
    try:
        result = execute_extraction()
        print(result.head())
    except Exception as e:
        logger.error(f"Failed to extract skills: {str(e)}")
        exit(1)
