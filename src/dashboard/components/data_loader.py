"""
Dashboard — Data Loader
Carga y cachea los datasets desde la capa Gold (SQL Server DW_BrechaDigital).
Si Gold no está disponible (sin credenciales o servidor offline), cae
silenciosamente a los CSVs processed/raw para que el dashboard siga funcionando.
"""
import os
import pandas as pd
from pathlib import Path
import streamlit as st
from difflib import SequenceMatcher

RAW = Path(__file__).resolve().parents[3] / 'data' / 'raw'
PROCESSED = Path(__file__).resolve().parents[3] / 'data' / 'processed'

# IT Careers: Definición oficial de 5 carreras de tecnología para alineación de dashboard
IT_CAREERS = [
    'Ingeniería de Sistemas',
    'Ingeniería de Software',
    'Ciencia de Datos',
    'Telecomunicaciones y Redes',
    'Ciberseguridad'
]

# Habilidades mapeadas por título de vacante (de empleos.py)
SKILLS_MAP = {
    'Data Engineer':    ['ETL', 'Spark', 'SQL'],
    'Data Analyst':     ['Power BI', 'Excel', 'Estadística'],
    'BI Developer':     ['Modelado Dimensional', 'DAX', 'SSAS'],
    'Python Developer': ['Python', 'pandas', 'scikit-learn'],
    'SQL Specialist':   ['SQL', 'Stored Procedures', 'DW Design'],
}

# Habilidades que ofrece cada carrera (aproximación para el skill gap)
CARRERA_SKILLS = {
    'Ingeniería de Sistemas':     ['Python', 'SQL', 'Estadística', 'ETL'],
    'Electrónica':                ['ETL'],
    'Administración de Empresas': ['Excel', 'Estadística'],
    'Diseño Gráfico':             ['diseño', 'adobe', 'ilustración', 'fotografía', 'video'],
    'Derecho':                    ['derecho', 'legal', 'jurídico', 'contratos', 'compliance'],
}


def _validate_careers(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Filter DataFrame to IT careers only and validate data quality.
    
    Args:
        df: Input DataFrame with 'NombreCarrera' column
    
    Returns:
        Tuple of (filtered_df, errors_list) where filtered_df contains only IT careers
        and errors_list contains validation warnings
    """
    errors = []
    
    if df.empty:
        errors.append('❌ DataFrame vacío recibido en _validate_careers()')
        return df, errors
    
    # Check: any IT careers in data?
    it_mask = df['NombreCarrera'].isin(IT_CAREERS)
    if not it_mask.any():
        found_careers = df['NombreCarrera'].unique().tolist()
        errors.append(f"❌ No se encontraron carreras IT. Carreras disponibles: {found_careers}")
        return df.iloc[0:0], errors
    
    original_count = len(df)
    df_filtered = df[it_mask].copy()
    filtered_count = len(df_filtered)
    pct_retained = (filtered_count / original_count * 100) if original_count > 0 else 0
    
    if pct_retained < 50:
        errors.append(f"⚠️ Solo {pct_retained:.1f}% de registros son carreras IT (filtrado de {original_count} a {filtered_count})")
    
    return df_filtered, errors


def _validate_graduation_year(df: pd.DataFrame) -> pd.Series:
    """
    Extract or estimate graduation year from available fields.
    
    Strategy:
    - If SemestreActual == 8: graduated, use anio_y
    - If SemestreActual < 8: estimate graduation_year = anio_y + (8 - SemestreActual) / 2
    - Fallback: use anio_y + 4 (typical 4-year program)
    
    Args:
        df: DataFrame with SemestreActual and anio_y columns
    
    Returns:
        Series with graduation_year values
    """
    if 'SemestreActual' not in df.columns or 'anio_y' not in df.columns:
        # Fallback: use anio_y + 4
        return df.get('anio_y', pd.Series([2023] * len(df))) + 4
    
    graduation_year = df['anio_y'].copy()
    
    # Adjust based on semester
    semester_col = df['SemestreActual'].fillna(0)
    adjustment = ((8 - semester_col) / 2).clip(lower=0, upper=4)
    graduation_year = graduation_year + adjustment.round().astype(int)
    
    return graduation_year


def _validate_salary_data(df: pd.DataFrame) -> list[str]:
    """
    Validate salary data quality and return warnings.
    
    Args:
        df: DataFrame with SalarioMensualUSD column
    
    Returns:
        List of validation warnings
    """
    errors = []
    
    if 'SalarioMensualUSD' not in df.columns:
        errors.append("⚠️ Columna SalarioMensualUSD no encontrada")
        return errors
    
    total_salary_rows = df['SalarioMensualUSD'].notna().sum()
    total_rows = len(df)
    salary_coverage_pct = (total_salary_rows / total_rows * 100) if total_rows > 0 else 0
    
    if salary_coverage_pct < 50:
        errors.append(f"⚠️ Datos de salario disponibles solo en {salary_coverage_pct:.1f}% de registros (promedio puede estar sesgado)")
    elif salary_coverage_pct < 80:
        errors.append(f"ℹ️ Datos de salario en {salary_coverage_pct:.1f}% de registros")
    
    return errors


def _format_validation_errors(errors: list[str]) -> str:
    """
    Format validation errors for Streamlit display.
    
    Args:
        errors: List of error/warning strings
    
    Returns:
        Formatted string for display
    """
    if not errors:
        return ""
    return "\n".join(f"• {err}" for err in errors)


def _gold_engine():
    """
    Retorna un engine SQLAlchemy apuntando a DW_BrechaDigital (Gold).
    Retorna None si las variables de entorno no están configuradas o
    si la conexión falla (SQL Server no disponible).
    La conexión es lazy — se crea solo cuando se invoca esta función.
    """
    server = os.getenv('DW_SERVER')
    db     = os.getenv('DW_NAME')
    user   = os.getenv('DW_USER')
    pwd    = os.getenv('DW_PASSWORD')

    if not all([server, db, user, pwd]):
        return None

    try:
        from sqlalchemy import create_engine, text
        conn_str = (
            f'mssql+pyodbc://{user}:{pwd}@{server}/{db}'
            '?driver=ODBC+Driver+17+for+SQL+Server'
        )
        engine = create_engine(conn_str, connect_args={'connect_timeout': 5})
        # ping rápido para verificar que el servidor responde
        with engine.connect() as con:
            con.execute(text('SELECT 1'))
        return engine
    except Exception:
        return None


def _load_df_from_gold(engine) -> pd.DataFrame | None:
    """
    Consulta Gold: FACT_INSERCION_LABORAL + DIM_CARRERA + DIM_ESTUDIANTE + DIM_REGION.
    Retorna DataFrame con columnas equivalentes al CSV merge, o None si falla.
    """
    sql = """
        SELECT
            e.EstudianteID,
            e.nombre        AS Nombre,
            c.nombrecarrera AS NombreCarrera,
            r.Ciudad,
            e.Genero,
            f.EstaEmpleado          AS TieneEmpleoFormal,
            f.TrabajaEnAreaDeEstudio,
            f.SalarioMensualUSD
        FROM FACT_INSERCION_LABORAL f
        JOIN DIM_CARRERA    c ON f.SK_Carrera    = c.SK_Carrera
        JOIN DIM_ESTUDIANTE e ON f.SK_Estudiante = e.SK_Estudiante
        JOIN DIM_REGION     r ON f.SK_Region     = r.SK_Region
    """
    try:
        df = pd.read_sql(sql, engine)
        for col in ['TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio']:
            df[col] = df[col].map({
                True: True, False: False,
                1: True, 0: False,
                'True': True, 'False': False,
            })
        return df
    except Exception:
        return None


def _load_df_from_csv() -> pd.DataFrame:
    """
    Load data from processed CSV files with IT career filtering.
    
    Returns:
        Merged DataFrame with only IT careers and enrollment year (anio_y)
    """
    est = pd.read_csv(PROCESSED / 'estudiantes_cleaned.csv').drop(columns=['anio'], errors='ignore')
    ins = pd.read_csv(PROCESSED / 'inscripciones_cleaned.csv').rename(columns={'anio': 'anio_y'})
    egr = pd.read_csv(PROCESSED / 'seguimientoegresados_cleaned.csv').drop(columns=['anio'], errors='ignore')
    car = pd.read_csv(PROCESSED / 'carreras_cleaned.csv').drop(columns=['anio'], errors='ignore')
    
    df = (
        est
        .merge(ins, on='EstudianteID', how='left')
        .merge(egr, on='EstudianteID', how='left')
        .merge(car, on='CarreraID', how='left')
    )
    
    for col in ['TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio']:
        if col in df.columns:
            df[col] = df[col].map({True: True, False: False, 'True': True, 'False': False})
    return df


@st.cache_data
def load_df() -> pd.DataFrame:
    """
    DataFrame principal: carga desde CSV (IT careers only).
    
    Implementa Phase 2 tasks:
    - Carga desde CSV exclusivamente (sin fallback a Gold por ahora)
    - Filtra a carreras IT solamente
    - Agrega columna de año de graduación
    - Valida calidad de datos
    
    Columnas garantizadas: EstudianteID, Nombre, NombreCarrera, Ciudad,
    Genero, TieneEmpleoFormal, TrabajaEnAreaDeEstudio, SalarioMensualUSD, graduation_year.
    """
    # Carga de CSV (fallback seguro, sin SQL Server)
    try:
        df = _load_df_from_csv()
    except Exception as e:
        st.error(f"❌ Error al cargar datos CSV: {str(e)}")
        st.stop()
    
    # Filtro de carreras IT (Phase 2.1)
    df, career_errors = _validate_careers(df)
    
    # Almacena errores en session state para que las páginas puedan mostrarlos
    if '_loader_errors' not in st.session_state:
        st.session_state._loader_errors = []
    st.session_state._loader_errors.extend(career_errors)
    
    if df.empty:
        st.error("❌ No hay datos disponibles después de filtrar carreras IT")
        st.stop()
    
    # Agregar columna de año de graduación (Phase 2.2, 2.3)
    df['graduation_year'] = _validate_graduation_year(df)
    
    # Validar calidad de datos de salario (Phase 2.4)
    salary_errors = _validate_salary_data(df)
    st.session_state._loader_errors.extend(salary_errors)
    
    return df


@st.cache_data
def load_vacantes() -> pd.DataFrame:
    """Vacantes del mercado — lee desde processed/empleos/."""
    path = PROCESSED / 'empleos' / 'vacantes_tecnologicas_cleaned.csv'
    if not path.exists():
        st.error(f'Archivo no encontrado: {path}')
        st.stop()
    return pd.read_csv(path)


@st.cache_data
def get_kpis() -> dict:
    """
    Retorna KPIs principales con validaciones de calidad de datos.
    
    Returns:
        dict with keys: tasa_empleo, pct_area, salario_prom, total_egresados, 
                       graduation_year_range, _errors
    """
    df = load_df()
    errors = []
    
    con_dato = df.dropna(subset=['TieneEmpleoFormal'])
    empleados = con_dato[con_dato['TieneEmpleoFormal'] == True]
    
    if len(con_dato) < 10:
        errors.append("⚠️ Muestra muy pequeña (<10 registros) para KPIs confiables")
    
    # Check salary data coverage
    salary_coverage = (empleados['SalarioMensualUSD'].notna().sum() / len(empleados) * 100) if len(empleados) > 0 else 0
    
    if len(empleados) == 0:
        errors.append("⚠️ No hay registros de empleados para calcular KPIs de empleo")
        return {
            'tasa_empleo': 0.0,
            'pct_area': 0.0,
            'salario_prom': 0.0,
            'total_egresados': len(con_dato),
            'graduation_year_range': 'N/D',
            'salary_coverage_pct': salary_coverage,
            '_errors': errors,
        }
    if salary_coverage < 50:
        errors.append(f"⚠️ Datos de salario en {salary_coverage:.0f}% de empleados (promedio puede estar sesgado)")
    elif salary_coverage < 80:
        errors.append(f"ℹ️ Datos de salario en {salary_coverage:.0f}% de empleados")
    
    # Check graduation year data
    try:
        graduation_years = _validate_graduation_year(df)
        grad_min = graduation_years.min()
        grad_max = graduation_years.max()
        graduation_year_range = f"{int(grad_min)}-{int(grad_max)}"
        
        if grad_max < 2010 or grad_min > 2030:
            errors.append(f"⚠️ Rango de años de egreso inusual: {graduation_year_range}")
    except Exception as e:
        errors.append(f"⚠️ Error calculando años de egreso: {str(e)}")
        graduation_year_range = 'N/D'
    
    # Check employment area alignment
    trabaja_area = empleados['TrabajaEnAreaDeEstudio'].notna().sum()
    if trabaja_area < len(empleados) * 0.5:
        errors.append(f"ℹ️ Solo {(trabaja_area/len(empleados)*100):.0f}% tienen datos de empleo en área")
    
    return {
        'tasa_empleo':     round(con_dato['TieneEmpleoFormal'].mean() * 100, 1),
        'pct_area':        round(empleados['TrabajaEnAreaDeEstudio'].mean() * 100, 1) if len(empleados) > 0 else 0,
        'salario_prom':    round(empleados['SalarioMensualUSD'].mean(), 1) if len(empleados) > 0 else 0,
        'total_egresados': len(con_dato),
        'graduation_year_range': graduation_year_range,
        'salary_coverage_pct': salary_coverage,
        '_errors':         errors,
    }


@st.cache_data
def get_empleo_por_carrera() -> pd.DataFrame:
    df = load_df()
    con_dato = df.dropna(subset=['TieneEmpleoFormal'])
    return (
        con_dato.groupby('NombreCarrera')['TieneEmpleoFormal']
        .mean()
        .mul(100)
        .round(1)
        .reset_index()
        .rename(columns={'TieneEmpleoFormal': 'tasa_empleo'})
        .sort_values('tasa_empleo', ascending=True)
    )


@st.cache_data
def get_distribucion_ciudad() -> pd.DataFrame:
    df = load_df()
    return (
        df.groupby('Ciudad')['EstudianteID']
        .count()
        .reset_index()
        .rename(columns={'EstudianteID': 'total'})
        .sort_values('total', ascending=False)
    )


@st.cache_data
def get_salario_por_carrera() -> pd.DataFrame:
    df = load_df()
    empleados = df[df['TieneEmpleoFormal'] == True].dropna(subset=['SalarioMensualUSD'])
    return (
        empleados.groupby('NombreCarrera')['SalarioMensualUSD']
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={'SalarioMensualUSD': 'salario_promedio'})
        .sort_values('salario_promedio', ascending=True)
    )


@st.cache_data
def get_habilidades_demandadas() -> pd.DataFrame:
    vac = load_vacantes()
    conteo = {}

    if 'description' in vac.columns and vac['description'].notna().any():
        for desc in vac['description'].dropna():
            # Tokenizar por coma y punto y coma
            tokens = []
            for part in str(desc).split(','):
                tokens.extend(part.split(';'))
            for token in tokens:
                skill = token.strip().title()
                if len(skill) > 1:
                    conteo[skill] = conteo.get(skill, 0) + 1
    else:
        st.warning('Columna description ausente o vacía — usando mapa estático de habilidades.')
        for _, row in vac.iterrows():
            skills = SKILLS_MAP.get(row['title'], [])
            for s in skills:
                conteo[s] = conteo.get(s, 0) + 1

    return (
        pd.DataFrame(list(conteo.items()), columns=['habilidad', 'demanda'])
        .sort_values('demanda', ascending=False)
    )


def _fuzzy_match_skill(demand_skill: str, academic_skills: list[str], threshold: float = 0.80) -> float:
    """
    Perform fuzzy matching between demand skill and academic skills using SequenceMatcher.
    
    Args:
        demand_skill: Single skill from market demand (e.g., "Machine Learning")
        academic_skills: List of skills from academic curricula (e.g., ["Python", "ML", "Deep Learning"])
        threshold: Similarity score threshold (0.0-1.0, default 0.80)
    
    Returns:
        float: Maximum similarity score (0.0-1.0) against all academic skills, or 0.0 if below threshold
    """
    if not academic_skills:
        return 0.0
    
    demand_normalized = demand_skill.lower().strip()
    max_ratio = 0.0
    
    for academic_skill in academic_skills:
        academic_normalized = str(academic_skill).lower().strip()
        ratio = SequenceMatcher(None, demand_normalized, academic_normalized).ratio()
        max_ratio = max(max_ratio, ratio)
    
    return max_ratio if max_ratio >= threshold else 0.0


@st.cache_data
def get_skill_gap() -> pd.DataFrame:
    """
    Retorna demanda de mercado vs cobertura académica con fuzzy matching.
    
    Columnas:
    - habilidad: Skill demandada en vacantes
    - demanda: Frecuencia en las vacantes
    - similarity_score: Fuzzy match score (0.0-1.0) contra skills académicas
    - cobertura_%: Porcentaje de cobertura académica (0-100%)
    - carrera: Carrera donde se enseña la habilidad más similar (N/D si no cubierta)
    - _errors: List of validation errors/warnings
    """
    errors = []
    
    try:
        dem = get_habilidades_demandadas()
        if dem.empty:
            errors.append("⚠️ No se encontraron habilidades demandadas (vacantes vacías)")
            return pd.DataFrame(
                columns=['habilidad', 'demanda', 'similarity_score', 'cobertura_%', 'carrera', '_errors']
            )
    except Exception as e:
        errors.append(f"❌ Error cargando habilidades demandadas: {str(e)}")
        return pd.DataFrame(
            columns=['habilidad', 'demanda', 'similarity_score', 'cobertura_%', 'carrera', '_errors']
        )
    
    try:
        hab_academicas = load_habilidades_academicas()
        if not hab_academicas:
            errors.append("⚠️ No se cargaron habilidades académicas (usando valores por defecto)")
            hab_academicas = CARRERA_SKILLS
    except Exception as e:
        errors.append(f"⚠️ Error cargando habilidades académicas: {str(e)}")
        hab_academicas = CARRERA_SKILLS
    
    # Flatten academic skills list for fuzzy matching
    all_academic_skills = []
    for carrera, skills in hab_academicas.items():
        all_academic_skills.extend(skills)
    
    if not all_academic_skills:
        errors.append("⚠️ Lista de habilidades académicas vacía")
    
    # Map skill → first carrera where it appears (for coverage tracking)
    habilidad_a_carrera: dict[str, str] = {}
    for carrera, habilidades in hab_academicas.items():
        for h in habilidades:
            if h.lower() not in habilidad_a_carrera:
                habilidad_a_carrera[h.lower()] = carrera
    
    rows = []
    for _, r in dem.iterrows():
        demand_skill = r['habilidad']
        demand_count = r['demanda']
        
        try:
            # Fuzzy match with threshold 0.80
            similarity_score = _fuzzy_match_skill(demand_skill, all_academic_skills, threshold=0.80)
            cobertura_pct = round(similarity_score * 100, 1)
            
            # Find carrera for matched skill (if covered)
            best_match_carrera = 'N/D'
            if similarity_score > 0.0:
                for academic_skill in all_academic_skills:
                    ratio = SequenceMatcher(None, demand_skill.lower(), academic_skill.lower()).ratio()
                    if ratio >= 0.80:
                        best_match_carrera = habilidad_a_carrera.get(academic_skill.lower(), 'N/D')
                        break
            
            rows.append({
                'habilidad': demand_skill,
                'demanda': demand_count,
                'similarity_score': round(similarity_score, 3),
                'cobertura_%': cobertura_pct,
                'carrera': best_match_carrera,
            })
        except Exception as e:
            errors.append(f"⚠️ Error procesando skill '{demand_skill}': {str(e)}")
            rows.append({
                'habilidad': demand_skill,
                'demanda': demand_count,
                'similarity_score': 0.0,
                'cobertura_%': 0.0,
                'carrera': 'ERROR',
            })
    
    result_df = pd.DataFrame(rows).sort_values('demanda', ascending=False)
    
    # Add 'cobertura' column for backward compatibility with chart functions
    result_df['cobertura'] = result_df['cobertura_%']
    
    # Store errors for each row (for pages to display)
    if errors:
        result_df['_errors'] = [errors] * len(result_df)
    else:
        result_df['_errors'] = [[] for _ in range(len(result_df))]
    
    return result_df


@st.cache_data


@st.cache_data
def load_habilidades_academicas() -> dict[str, list[str]]:
    """
    Retorna dict {carrera: [habilidades]} agrupando habilidades académicas por carrera.
    Estrategia Gold: DIM_HABILIDAD JOIN DIM_CARRERA.
    Fallback: processed/competenciasdigitales_cleaned.csv.
    Si ambos fallan → retorna {}.
    """
    engine = _gold_engine()
    if engine is not None:
        try:
            sql = """
                SELECT h.NombreHabilidad, c.nombrecarrera
                FROM DIM_HABILIDAD h
                JOIN DIM_CARRERA c ON h.SK_Carrera = c.SK_Carrera
                ORDER BY c.nombrecarrera, h.NombreHabilidad
            """
            df = pd.read_sql(sql, engine)
            result: dict[str, list[str]] = {}
            for carrera, grupo in df.groupby('nombrecarrera'):
                result[str(carrera)] = grupo['NombreHabilidad'].tolist()
            return result
        except Exception:
            pass

    # Fallback: CSV processed
    try:
        path = PROCESSED / 'competenciasdigitales_cleaned.csv'
        df = pd.read_csv(path)
        result = {}
        if 'CarreraID' in df.columns:
            for carrera_id, grupo in df.groupby('CarreraID'):
                result[f"Carrera {carrera_id}"] = grupo['NombreHabilidad'].tolist()
        else:
            for nivel, grupo in df.groupby('NivelRequerido'):
                result[str(nivel)] = grupo['NombreHabilidad'].tolist()
        return result
    except Exception:
        return {}


@st.cache_data
def get_tasa_desercion() -> dict:
    """
    Retorna dict con tasa_desercion (float), total_estudiantes (int), en_riesgo (int).
    Fuente: data/processed/silver_integrated_data.csv
    Heurística de riesgo: SemestreActual < 8 AND NotaFinal < 51.
    """
    try:
        path = PROCESSED / 'silver_integrated_data.csv'
        df = pd.read_csv(path)
        total = len(df)
        if total == 0:
            return {'tasa_desercion': None, 'total_estudiantes': 0, 'en_riesgo': 0}
        en_riesgo_df = df[(df['SemestreActual'] < 8) & (df['NotaFinal'] < 51)]
        en_riesgo = len(en_riesgo_df)
        tasa = round(en_riesgo / total * 100, 1)
        return {
            'tasa_desercion':    tasa,
            'total_estudiantes': total,
            'en_riesgo':         en_riesgo,
        }
    except Exception:
        return {'tasa_desercion': None, 'total_estudiantes': 0, 'en_riesgo': 0}


@st.cache_data
def get_empleo_temporal() -> pd.DataFrame:
    """
    Retorna DataFrame con columnas [anio, tasa_empleo, fuente, _errors].
    Usa graduation_year (cohorte de egreso) en lugar de anio_x (cohorte de ingreso).
    
    Estrategia:
    1. Gold: FACT_INSERCION_LABORAL + DIM_TIEMPO con graduation_year
    2. Fallback: silver_integrated_data.csv con graduation_year estimado
    3. Si ambos fallan: DataFrame vacío
    
    Returns:
        DataFrame with temporal employment analysis grouped by graduation year
    """
    errors = []
    
    engine = _gold_engine()
    if engine is not None:
        try:
            sql = """
                SELECT
                    t.anio,
                    AVG(CAST(f.EstaEmpleado AS FLOAT)) * 100 AS tasa_empleo
                FROM FACT_INSERCION_LABORAL f
                JOIN DIM_TIEMPO t ON f.SK_Tiempo = t.SK_Tiempo
                GROUP BY t.anio
                ORDER BY t.anio
            """
            df = pd.read_sql(sql, engine)
            df['fuente'] = 'Gold'
            if errors:
                df['_errors'] = [errors] * len(df)
            else:
                df['_errors'] = [[] for _ in range(len(df))]
            return df[['anio', 'tasa_empleo', 'fuente', '_errors']]
        except Exception as e:
            errors.append(f"ℹ️ Gold layer unavailable: {str(e)}")
    
    # Fallback: use silver with graduation_year estimation
    try:
        silver = pd.read_csv(PROCESSED / 'silver_integrated_data.csv')
        
        # Check required columns
        if 'EstudianteID' not in silver.columns:
            errors.append("❌ Columna EstudianteID no encontrada en silver_integrated_data.csv")
            return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])
        
        # Estimate graduation_year
        if 'SemestreActual' not in silver.columns or 'anio_y' not in silver.columns:
            errors.append("⚠️ Columnas SemestreActual/anio_y no encontradas, usando anio_x")
            silver['graduation_year'] = silver.get('anio_x', 2020) + 4
        else:
            silver['graduation_year'] = _validate_graduation_year(silver)
        
        seg = pd.read_csv(PROCESSED / 'seguimientoegresados_cleaned.csv')
        
        if 'EstudianteID' not in seg.columns or 'TieneEmpleoFormal' not in seg.columns:
            errors.append("❌ Columnas requeridas no encontradas en seguimientoegresados_cleaned.csv")
            return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])
        
        merged = silver.merge(seg, on='EstudianteID', how='inner')
        
        if merged.empty:
            errors.append("⚠️ No se encontraron registros comunes entre silver y seguimiento")
            return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])
        
        merged['TieneEmpleoFormal'] = (
            merged['TieneEmpleoFormal']
            .map({True: 1, False: 0, 'True': 1, 'False': 0})
            .fillna(0)
            .astype(float)
        )
        
        # Group by graduation_year (not anio_x)
        temporal = (
            merged.groupby('graduation_year')['TieneEmpleoFormal']
            .mean()
            .reset_index()
            .rename(columns={'graduation_year': 'anio', 'TieneEmpleoFormal': 'tasa_empleo'})
        )
        temporal['tasa_empleo'] = (temporal['tasa_empleo'] * 100).round(1)
        temporal['fuente'] = 'Silver (cohorte de egreso)'
        if errors:
            temporal['_errors'] = [errors] * len(temporal)
        else:
            temporal['_errors'] = [[] for _ in range(len(temporal))]
        
        return temporal[['anio', 'tasa_empleo', 'fuente', '_errors']].sort_values('anio').reset_index(drop=True)
    except Exception as e:
        errors.append(f"❌ Error procesando temporal analysis: {str(e)}")
        result_df = pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])
        result_df['_errors'] = [errors]
        return result_df


@st.cache_data
def get_cepal_bolivia() -> pd.DataFrame:
    """Indicador CEPALSTAT — lee desde processed/cepalstat/."""
    try:
        cep = pd.read_csv(PROCESSED / 'cepalstat' / 'indicadores_tic_region_cleaned.csv')
        bol = cep[(cep['iso3'].str.lower() == 'bol') & (cep['dim_28619'] == 28620)].copy()
        return bol[['anio', 'value']].sort_values('anio').reset_index(drop=True)
    except Exception:
        st.warning('No se pudo cargar el indicador CEPALSTAT.')
        return pd.DataFrame(columns=['anio', 'value'])


def build_groq_context(kpis: dict | None = None) -> str:
    if kpis is None:
        kpis = get_kpis()

    # Carreras y ciudades dinámicas desde los datos cargados
    df = load_df()
    carreras = df['NombreCarrera'].dropna().unique().tolist() if df is not None and not df.empty else ['Ingeniería de Sistemas', 'Diseño Gráfico', 'Administración de Empresas', 'Derecho', 'Electrónica']
    ciudades = df['Ciudad'].dropna().unique().tolist() if df is not None and not df.empty else ['La Paz', 'Cochabamba', 'Santa Cruz de la Sierra', 'Tarija', 'Sucre', 'Remoto']

    # Top 5 habilidades más demandadas — si falla, se omite el bloque
    top_skills_bloque = ''
    try:
        hab_df = get_habilidades_demandadas()
        if not hab_df.empty:
            top5 = hab_df.sort_values('demanda', ascending=False).head(5)['habilidad'].tolist()
            if top5:
                top_skills_bloque = f'\n- TOP 5 HABILIDADES MÁS DEMANDADAS: {", ".join(top5)}'
    except Exception:
        pass

    return f"""Sos un asistente de Business Intelligence para el proyecto "Estrategia para la Reducción de la Brecha Digital Laboral en la Educación Técnica Superior" (UPDS, Bolivia).

SCOPE:
- 5 carreras IT: Ingeniería de Sistemas, Software, Ciencia de Datos, Telecomunicaciones, Ciberseguridad
- Análisis: Línea de tiempo graduación→empleo (cohortes 2024-2028)
- Metodología: Fuzzy matching (umbral 0.80) para similitud semántica en habilidades

DATOS ACTUALES DEL DASHBOARD:
- Tasa de empleo formal de egresados: {kpis['tasa_empleo']}%
- Egresados empleados en su área de estudio: {kpis['pct_area']}%
- Salario promedio de empleados: ${kpis['salario_prom']} USD/mes
- Total de egresados analizados: {kpis['total_egresados']}
- Cobertura de datos de salarios: {kpis.get('salary_coverage_pct', 0):.1f}%{top_skills_bloque}

ARQUITECTURA:
- Capa Bronze: SQL Server (BrechaDigitalDB) — datos crudos de estudiantes, carreras, inscripciones
- Capa Silver: Python/pandas — clean.py + normalize.py
- Capa Gold: SQL Server (DW_BrechaDigital) — esquema copo de nieve
- Dashboard: Streamlit + Plotly (esta aplicación)

CIUDADES: {", ".join(ciudades)}.

Respondé preguntas sobre inserción laboral, brecha de habilidades y tendencias TIC en Bolivia (carreras IT).
Sé conciso y orientado a insights de negocio. Respondé siempre en español."""


def get_skill_gap_filtered(top_n: int = 15) -> tuple[pd.DataFrame, int]:
    """
    Retorna skill gap pero filtrando solo las top N habilidades demandadas.
    Las demás se agrupan en un contador.
    
    Returns:
        (filtered_df, count_other_skills): DataFrame con top N + count de otros
    """
    full_gap = get_skill_gap()
    
    if full_gap.empty:
        return full_gap, 0
    
    filtered = full_gap.head(top_n).copy()
    other_count = len(full_gap) - len(filtered)
    
    return filtered, other_count


def get_habilidades_demandadas_filtered(top_n: int = 10) -> tuple[pd.DataFrame, int]:
    """
    Retorna habilidades demandadas filtradas a top N.
    
    Returns:
        (filtered_df, count_other): DataFrame con top N + count de otros
    """
    full_hab = get_habilidades_demandadas()
    
    if full_hab.empty:
        return full_hab, 0
    
    filtered = full_hab.head(top_n).copy()
    other_count = len(full_hab) - len(filtered)
    
    return filtered, other_count

