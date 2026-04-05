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

RAW = Path(__file__).resolve().parents[3] / 'data' / 'raw'
PROCESSED = Path(__file__).resolve().parents[3] / 'data' / 'processed'

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


@st.cache_data
def load_df() -> pd.DataFrame:
    """
    DataFrame principal: intenta Gold primero, cae a CSVs si no disponible.
    Columnas garantizadas: EstudianteID, Nombre, NombreCarrera, Ciudad,
    Genero, TieneEmpleoFormal, TrabajaEnAreaDeEstudio, SalarioMensualUSD.
    """
    engine = _gold_engine()
    if engine is not None:
        df = _load_df_from_gold(engine)
        if df is not None:
            return df

    # Fallback: CSVs processed
    est = pd.read_csv(PROCESSED / 'estudiantes_cleaned.csv').drop(columns=['anio'], errors='ignore')
    ins = pd.read_csv(PROCESSED / 'inscripciones_cleaned.csv').drop(columns=['anio'], errors='ignore')
    egr = pd.read_csv(PROCESSED / 'seguimientoegresados_cleaned.csv').drop(columns=['anio'], errors='ignore')
    car = pd.read_csv(PROCESSED / 'carreras_cleaned.csv').drop(columns=['anio'], errors='ignore')
    df = (
        est
        .merge(ins, on='EstudianteID', how='left')
        .merge(egr, on='EstudianteID', how='left')
        .merge(car, on='CarreraID', how='left')
    )
    for col in ['TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio']:
        df[col] = df[col].map({True: True, False: False, 'True': True, 'False': False})
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
    df = load_df()
    con_dato = df.dropna(subset=['TieneEmpleoFormal'])
    empleados = con_dato[con_dato['TieneEmpleoFormal'] == True]
    return {
        'tasa_empleo':     round(con_dato['TieneEmpleoFormal'].mean() * 100, 1),
        'pct_area':        round(empleados['TrabajaEnAreaDeEstudio'].mean() * 100, 1),
        'salario_prom':    round(empleados['SalarioMensualUSD'].mean(), 1),
        'total_egresados': len(con_dato),
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


@st.cache_data
def get_skill_gap() -> pd.DataFrame:
    """
    Devuelve demanda de mercado vs cobertura académica por habilidad.
    Cobertura: 100 si alguna palabra clave de la skill demandada aparece en el currículo académico, 0 si no.
    Columna nivel: nivel académico donde aparece la habilidad (Básico/Intermedio/Avanzado/N/D).
    """
    dem = get_habilidades_demandadas()
    hab_academicas = load_habilidades_academicas()

    # Texto plano del currículo para keyword matching
    all_academic_text = ' '.join(
        h.lower().replace('(', ' ').replace(')', ' ')
        for skills in hab_academicas.values() for h in skills
    )

    # Mapa inverso habilidad → nivel
    habilidad_a_nivel: dict[str, str] = {}
    for nivel, habilidades in hab_academicas.items():
        for h in habilidades:
            habilidad_a_nivel[h.lower()] = nivel

    _stopwords = {'para', 'con', 'los', 'las', 'por', 'del', 'una', 'que', 'and', 'the', 'y', 'de', 'en', 'el', 'su', 'sus'}

    def _covered(skill_str: str) -> float:
        words = [w.strip('.,()') for w in skill_str.lower().split()]
        significant = [w for w in words if len(w) > 3 and w not in _stopwords]
        return 100.0 if any(w in all_academic_text for w in significant) else 0.0

    rows = []
    for _, r in dem.iterrows():
        skill = r['habilidad']
        nivel = habilidad_a_nivel.get(skill.lower(), 'N/D')
        rows.append({
            'habilidad':  skill,
            'demanda':    r['demanda'],
            'cobertura':  _covered(skill),
            'nivel':      nivel,
        })
    return pd.DataFrame(rows).sort_values('demanda', ascending=False)


@st.cache_data
def load_habilidades_academicas() -> dict[str, list[str]]:
    """
    Retorna dict {nivel: [habilidades]} agrupando habilidades académicas por nivel/categoría.
    Estrategia Gold: DIM_HABILIDAD JOIN DIM_CATEGORIA_SKILL.
    Fallback: processed/competenciasdigitales_cleaned.csv, columnas NombreHabilidad + NivelRequerido.
    Si ambos fallan → retorna {}.
    """
    engine = _gold_engine()
    if engine is not None:
        try:
            sql = """
                SELECT h.NombreHabilidad, c.NombreCategoria
                FROM DIM_HABILIDAD h
                JOIN DIM_CATEGORIA_SKILL c ON h.SK_Categoria = c.SK_Categoria
                ORDER BY c.NombreCategoria, h.NombreHabilidad
            """
            df = pd.read_sql(sql, engine)
            result: dict[str, list[str]] = {}
            for categoria, grupo in df.groupby('NombreCategoria'):
                result[str(categoria)] = grupo['NombreHabilidad'].tolist()
            return result
        except Exception:
            pass

    # Fallback: CSV processed
    try:
        path = PROCESSED / 'competenciasdigitales_cleaned.csv'
        df = pd.read_csv(path)
        result = {}
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
    Retorna DataFrame con columnas [anio, tasa_empleo, fuente].
    Estrategia Gold: FACT_INSERCION_LABORAL + DIM_TIEMPO.
    Fallback: silver_integrated_data.csv agrupado por anio_x.
    Si ambos fallan → DataFrame vacío con esas columnas.
    """
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
            return df[['anio', 'tasa_empleo', 'fuente']]
        except Exception:
            pass

    # Fallback: join silver (anio_x) + seguimientoegresados_cleaned (TieneEmpleoFormal)
    try:
        silver = pd.read_csv(PROCESSED / 'silver_integrated_data.csv')[['EstudianteID', 'anio_x']]
        seg    = pd.read_csv(PROCESSED / 'seguimientoegresados_cleaned.csv')[['EstudianteID', 'TieneEmpleoFormal']]
        merged = silver.merge(seg, on='EstudianteID', how='inner')
        merged['TieneEmpleoFormal'] = (
            merged['TieneEmpleoFormal']
            .map({True: 1, False: 0, 'True': 1, 'False': 0})
            .fillna(0)
            .astype(float)
        )
        temporal = (
            merged.groupby('anio_x')['TieneEmpleoFormal']
            .mean()
            .reset_index()
            .rename(columns={'anio_x': 'anio', 'TieneEmpleoFormal': 'tasa_empleo'})
        )
        temporal['tasa_empleo'] = (temporal['tasa_empleo'] * 100).round(1)
        temporal['fuente'] = 'Silver (cohorte de ingreso)'
        return temporal[['anio', 'tasa_empleo', 'fuente']].sort_values('anio').reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente'])


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

DATOS ACTUALES DEL DASHBOARD:
- Tasa de empleo formal de egresados: {kpis['tasa_empleo']}%
- Egresados empleados en su área de estudio: {kpis['pct_area']}%
- Salario promedio de empleados: ${kpis['salario_prom']} USD/mes
- Total de egresados analizados: {kpis['total_egresados']}{top_skills_bloque}

ARQUITECTURA:
- Capa Bronze: SQL Server (BrechaDigitalDB) — datos crudos de estudiantes, carreras, inscripciones
- Capa Silver: Python/pandas — clean.py + normalize.py
- Capa Gold: SQL Server (DW_BrechaDigital) — esquema copo de nieve
- Dashboard: Streamlit + Plotly (esta aplicación)

CARRERAS ANALIZADAS: {", ".join(carreras)}
CIUDADES: {", ".join(ciudades)}.

Respondé preguntas sobre los datos, KPIs, tendencias y la brecha digital en Bolivia.
Sé conciso y orientado a insights de negocio. Respondé siempre en español."""
