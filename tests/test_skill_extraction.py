"""
Tests — Skill Extraction
Responsable: Diego Vargas Urzagaste (@temps-code)

Test coverage para src/ingestion/skill_extraction.py

Includes:
- Unit tests: helpers, normalization, regex patterns
- Integration tests: full pipeline, cache behavior, error handling
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pandas as pd

from src.ingestion.skill_extraction import (
    SkillExtractor,
    parse_groq_response,
    apply_regex_patterns,
    skill_title_case,
    SkillExtractionConfig,
    InputValidationError,
    GroqAPIError,
    OutputValidationError,
    PersistenceError,
)


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "cache"


@pytest.fixture
def sample_vacantes_df():
    """Sample DataFrame with test job data."""
    return pd.DataFrame({
        "job_id": ["job_1", "job_2", "job_3"],
        "title": ["Python Developer", "Frontend Engineer", "DevOps Specialist"],
        "description": [
            "We are hiring a Python developer with experience in Django and PostgreSQL. Required: REST API design, Docker basics.",
            "Looking for React expert with TypeScript background. Must know HTML/CSS, JavaScript, and state management.",
            "Kubernetes and AWS experience required. Docker, CI/CD pipelines, Linux administration.",
        ],
    })


@pytest.fixture
def groq_response_mock():
    """Mock Groq response."""
    return json.dumps({
        "desc_1": ["Python", "Django", "PostgreSQL", "REST API", "Docker"],
        "desc_2": ["React", "TypeScript", "JavaScript", "HTML/CSS"],
        "desc_3": ["Kubernetes", "AWS", "Docker", "Linux"],
    })


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS - parse_groq_response
# ─────────────────────────────────────────────────────────────────────────────

def test_parse_groq_response_valid():
    """Test valid JSON response parsing."""
    response = json.dumps({
        "desc_1": ["Python", "Django"],
        "desc_2": ["React"],
    })
    result = parse_groq_response(response)
    assert result == {"desc_1": ["Python", "Django"], "desc_2": ["React"]}


def test_parse_groq_response_invalid_json():
    """Test invalid JSON raises error."""
    with pytest.raises(json.JSONDecodeError):
        parse_groq_response("invalid json {")


def test_parse_groq_response_empty_arrays():
    """Test response with empty arrays."""
    response = json.dumps({
        "desc_1": [],
        "desc_2": ["Python"],
    })
    result = parse_groq_response(response)
    assert result["desc_1"] == []
    assert result["desc_2"] == ["Python"]


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS - apply_regex_patterns
# ─────────────────────────────────────────────────────────────────────────────

def test_apply_regex_patterns_python():
    """Test regex matching for Python."""
    desc = "We need a Python developer with Django experience"
    skills = apply_regex_patterns(desc)
    assert "python" in skills or "Python" in [s.lower() for s in skills]


def test_apply_regex_patterns_multiple():
    """Test multiple skill matches."""
    desc = "Docker, Kubernetes, AWS, and Python expertise required"
    skills = apply_regex_patterns(desc)
    assert len(skills) >= 3


def test_apply_regex_patterns_empty_description():
    """Test empty description returns empty list."""
    assert apply_regex_patterns("") == []
    assert apply_regex_patterns(None) == []


def test_apply_regex_patterns_no_match():
    """Test description with no tech skills."""
    desc = "Communication skills and teamwork are essential"
    skills = apply_regex_patterns(desc)
    assert len(skills) == 0


def test_apply_regex_patterns_java_not_javascript():
    """Test Java/JavaScript disambiguation."""
    # This is tricky with regex, but we should try
    desc = "Java expert wanted"
    skills = apply_regex_patterns(desc)
    # Regex should match "java" pattern
    matched_skills_lower = [s.lower() for s in skills]
    assert "java" in matched_skills_lower


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS - skill_title_case
# ─────────────────────────────────────────────────────────────────────────────

def test_skill_title_case_standard():
    """Test standard title case normalization."""
    assert skill_title_case("python") == "Python"
    assert skill_title_case("JAVASCRIPT") == "JavaScript"
    assert skill_title_case("DjAnGo") == "Django"


def test_skill_title_case_special_cases():
    """Test special case mappings."""
    assert skill_title_case("nodejs") == "Node.js"
    assert skill_title_case("c++") == "C++"
    assert skill_title_case("c#") == "C#"
    assert skill_title_case(".net") == ".NET"


def test_skill_title_case_already_normalized():
    """Test already normalized skills."""
    assert skill_title_case("Python") == "Python"
    assert skill_title_case("AWS") == "AWS"


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS - SkillExtractor._normalize_skills
# ─────────────────────────────────────────────────────────────────────────────

def test_normalize_skills_empty():
    """Test empty list normalization."""
    extractor = SkillExtractor(use_groq=False)
    assert extractor._normalize_skills([]) == []


def test_normalize_skills_deduplication():
    """Test deduplication."""
    extractor = SkillExtractor(use_groq=False)
    skills = ["python", "PYTHON", "Python"]
    result = extractor._normalize_skills(skills)
    assert result.count("Python") == 1


def test_normalize_skills_max_8():
    """Test limit to 8 skills."""
    extractor = SkillExtractor(use_groq=False)
    skills = ["Python", "Django", "Flask", "FastAPI", "JavaScript", "React", "Vue", "Angular", "Node.js"]
    result = extractor._normalize_skills(skills)
    assert len(result) == 8


def test_normalize_skills_sorted():
    """Test output is sorted."""
    extractor = SkillExtractor(use_groq=False)
    skills = ["Zebra", "Apple", "Banana"]
    result = extractor._normalize_skills(skills)
    assert result == sorted(result)


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS - SkillExtractor._validate_input
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_input_empty_df():
    """Test empty DataFrame raises error."""
    extractor = SkillExtractor(use_groq=False)
    with pytest.raises(InputValidationError):
        extractor._validate_input(pd.DataFrame())


def test_validate_input_missing_columns():
    """Test missing required columns raises error."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({"job_id": ["1"]})  # Missing title, description
    with pytest.raises(InputValidationError):
        extractor._validate_input(df)


def test_validate_input_valid():
    """Test valid input passes."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({
        "job_id": ["1"],
        "title": ["Developer"],
        "description": ["Python and Django experience required"],
    })
    # Should not raise
    extractor._validate_input(df)


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS - SkillExtractor._validate_output
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_output_missing_columns():
    """Test output validation detects missing columns."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({"job_id": ["1"]})  # Missing required columns
    with pytest.raises(OutputValidationError):
        extractor._validate_output(df)


def test_validate_output_invalid_json():
    """Test output validation detects invalid JSON."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({
        "job_id": ["1"],
        "title": ["Dev"],
        "description": ["Desc"],
        "skills_json": ["invalid json {"],
        "extraction_method": ["groq"],
        "extraction_timestamp": ["2024-01-01T00:00:00"],
        "confidence": [0.9],
        "error_message": [""],
    })
    with pytest.raises(OutputValidationError):
        extractor._validate_output(df)


def test_validate_output_invalid_extraction_method():
    """Test output validation detects invalid extraction_method."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({
        "job_id": ["1"],
        "title": ["Dev"],
        "description": ["Desc"],
        "skills_json": ["[]"],
        "extraction_method": ["invalid_method"],
        "extraction_timestamp": ["2024-01-01T00:00:00"],
        "confidence": [0.9],
        "error_message": [""],
    })
    with pytest.raises(OutputValidationError):
        extractor._validate_output(df)


def test_validate_output_confidence_out_of_range():
    """Test confidence validation."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({
        "job_id": ["1"],
        "title": ["Dev"],
        "description": ["Desc"],
        "skills_json": ["[]"],
        "extraction_method": ["groq"],
        "extraction_timestamp": ["2024-01-01T00:00:00"],
        "confidence": [1.5],  # Out of range
        "error_message": [""],
    })
    with pytest.raises(OutputValidationError):
        extractor._validate_output(df)


def test_validate_output_valid():
    """Test valid output passes."""
    extractor = SkillExtractor(use_groq=False)
    df = pd.DataFrame({
        "job_id": ["1"],
        "title": ["Dev"],
        "description": ["Desc"],
        "skills_json": [json.dumps(["Python"])],
        "extraction_method": ["groq"],
        "extraction_timestamp": ["2024-01-01T00:00:00"],
        "confidence": [0.9],
        "error_message": [""],
    })
    # Should not raise
    extractor._validate_output(df)


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS - SkillExtractor
# ─────────────────────────────────────────────────────────────────────────────

def test_extractor_init_without_groq(temp_cache_dir):
    """Test initializing extractor without Groq."""
    extractor = SkillExtractor(use_groq=False, cache_path=str(temp_cache_dir / "cache.csv"))
    assert extractor.use_groq is False
    assert extractor.groq_client is None


def test_extractor_init_with_groq_no_api_key():
    """Test Groq init without API key raises error."""
    # Temporarily unset GROQ_API_KEY
    old_key = os.environ.pop("GROQ_API_KEY", None)
    try:
        with pytest.raises(GroqAPIError):
            SkillExtractor(use_groq=True)
    finally:
        if old_key:
            os.environ["GROQ_API_KEY"] = old_key


@patch("src.ingestion.skill_extraction.Groq")
def test_extractor_init_with_groq(mock_groq_class, temp_cache_dir):
    """Test Groq init with API key."""
    os.environ["GROQ_API_KEY"] = "test_key"
    try:
        extractor = SkillExtractor(use_groq=True, cache_path=str(temp_cache_dir / "cache.csv"))
        assert extractor.use_groq is True
        mock_groq_class.assert_called_once()
    finally:
        del os.environ["GROQ_API_KEY"]


def test_extract_regex_fallback(sample_vacantes_df, temp_cache_dir):
    """Test regex fallback extraction."""
    extractor = SkillExtractor(use_groq=False, cache_path=str(temp_cache_dir / "cache.csv"))
    
    job_ids = sample_vacantes_df["job_id"].tolist()
    descriptions = sample_vacantes_df["description"].tolist()
    
    results = extractor._extract_regex_fallback(job_ids, descriptions)
    
    assert len(results) == 3
    for result in results:
        assert "job_id" in result
        assert "skills_json" in result
        assert result["extraction_method"] == "regex"
        assert 0 <= result["confidence"] <= 1
        assert json.loads(result["skills_json"]) is not None


def test_execute_with_regex_fallback(sample_vacantes_df, temp_cache_dir):
    """Test full execution with regex fallback."""
    cache_path = str(temp_cache_dir / "cache.csv")
    extractor = SkillExtractor(use_groq=False, cache_path=cache_path)
    
    result_df = extractor.execute(sample_vacantes_df)
    
    assert len(result_df) == 3
    assert all(col in result_df.columns for col in [
        "job_id", "title", "description", "skills_json", "extraction_method",
        "extraction_timestamp", "confidence", "error_message"
    ])
    assert Path(cache_path).exists()


def test_execute_cache_reuse(sample_vacantes_df, temp_cache_dir):
    """Test that cache is reused on second execution."""
    cache_path = str(temp_cache_dir / "cache.csv")
    
    # First execution
    extractor1 = SkillExtractor(use_groq=False, cache_path=cache_path)
    result1 = extractor1.execute(sample_vacantes_df)
    
    # Second execution should use cache
    extractor2 = SkillExtractor(use_groq=False, cache_path=cache_path)
    result2 = extractor2.execute(sample_vacantes_df)
    
    # Results should be identical (same cache)
    pd.testing.assert_frame_equal(result1, result2)


# ─────────────────────────────────────────────────────────────────────────────
# ERROR HANDLING TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_execute_with_nan_descriptions(temp_cache_dir):
    """Test handling of NaN descriptions."""
    df = pd.DataFrame({
        "job_id": ["job_1", "job_2"],
        "title": ["Dev", "Dev"],
        "description": ["Python experience", None],  # NaN
    })
    
    extractor = SkillExtractor(use_groq=False, cache_path=str(temp_cache_dir / "cache.csv"))
    # Should handle gracefully
    result = extractor.execute(df)
    assert len(result) == 2


def test_execute_with_very_short_descriptions(temp_cache_dir):
    """Test handling of very short descriptions."""
    df = pd.DataFrame({
        "job_id": ["job_1"],
        "title": ["Dev"],
        "description": ["Short"],  # Too short
    })
    
    extractor = SkillExtractor(use_groq=False, cache_path=str(temp_cache_dir / "cache.csv"))
    # Should still process
    result = extractor.execute(df)
    assert len(result) == 1


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION TESTS
# ─────────────────────────────────────────────────────────────────────────────

def test_skills_extraction_realistic_job_python():
    """Regression: Test realistic Python job description."""
    desc = (
        "We are looking for a Python Developer with at least 3 years of experience. "
        "Required skills: Python, Django, PostgreSQL, REST API design, Docker. "
        "Nice to have: Celery, Redis, AWS."
    )
    skills = apply_regex_patterns(desc)
    expected = {"python", "django", "postgresql", "docker", "redis", "aws"}
    assert all(skill.lower() in [s.lower() for s in skills] for skill in expected)


def test_skills_extraction_realistic_job_frontend():
    """Regression: Test realistic Frontend job description."""
    desc = (
        "Frontend Engineer needed. Must know React, TypeScript, HTML/CSS, JavaScript. "
        "Experience with state management (Redux, MobX) and testing (Jest, Playwright). "
        "Nice to have: Next.js, Tailwind CSS."
    )
    skills = apply_regex_patterns(desc)
    expected = {"react", "typescript", "javascript"}
    assert all(skill.lower() in [s.lower() for s in skills] for skill in expected)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
