"""
Dashboard — Data Loader
Carga y cachea los datasets desde los CSVs raw.
Cuando la capa Gold esté disponible, solo hay que cambiar las rutas aquí.
"""
import pandas as pd
from pathlib import Path
import streamlit as st

RAW = Path(__file__).resolve().parents[3] / 'data' / 'raw'

# dim_29117 en CEPALSTAT: 29160 → año 2000
_YEAR_BASE = 29160
_YEAR_OFFSET = 2000

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
}


@st.cache_data
def _load_raw():
    est = pd.read_csv(RAW / 'estudiantes.csv')
    ins = pd.read_csv(RAW / 'inscripciones.csv')
    egr = pd.read_csv(RAW / 'seguimientoegresados.csv')
    car = pd.read_csv(RAW / 'carreras.csv')
    vac = pd.read_csv(RAW / 'empleos' / 'vacantes_tecnologicas.csv')
    cep = pd.read_csv(RAW / 'cepalstat' / 'indicadores_tic_region.csv')
    return est, ins, egr, car, vac, cep


@st.cache_data
def load_df() -> pd.DataFrame:
    """DataFrame principal: estudiantes + inscripciones + egresados + carreras."""
    est, ins, egr, car, _, _ = _load_raw()
    df = (
        est
        .merge(ins, on='EstudianteID', how='left')
        .merge(egr, on='EstudianteID', how='left')
        .merge(car, on='CarreraID', how='left')
    )
    df['TieneEmpleoFormal'] = df['TieneEmpleoFormal'].map({'True': True, 'False': False})
    df['TrabajaEnAreaDeEstudio'] = df['TrabajaEnAreaDeEstudio'].map({'True': True, 'False': False})
    return df


@st.cache_data
def load_vacantes() -> pd.DataFrame:
    _, _, _, _, vac, _ = _load_raw()
    return vac


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
    for _, row in vac.iterrows():
        skills = SKILLS_MAP.get(row['title'], [])
        for s in skills:
            conteo[s] = conteo.get(s, 0) + 1
    return (
        pd.DataFrame(list(conteo.items()), columns=['habilidad', 'demanda'])
        .sort_values('demanda', ascending=True)
    )


@st.cache_data
def get_skill_gap() -> pd.DataFrame:
    """
    Devuelve demanda de mercado vs cobertura académica por habilidad.
    Cobertura = % de carreras que incluyen esa habilidad.
    """
    dem = get_habilidades_demandadas()
    total_carreras = len(CARRERA_SKILLS)
    rows = []
    for _, r in dem.iterrows():
        skill = r['habilidad']
        cubre = sum(skill in skills for skills in CARRERA_SKILLS.values())
        rows.append({
            'habilidad':  skill,
            'demanda':    r['demanda'],
            'cobertura':  round(cubre / total_carreras * 100, 1),
        })
    return pd.DataFrame(rows).sort_values('demanda', ascending=False)


@st.cache_data
def get_cepal_bolivia() -> pd.DataFrame:
    _, _, _, _, _, cep = _load_raw()
    bol = cep[(cep['iso3'] == 'BOL') & (cep['dim_28619'] == 28620)].copy()
    bol['anio'] = bol['dim_29117'] - _YEAR_BASE + _YEAR_OFFSET
    return bol[['anio', 'value']].sort_values('anio').reset_index(drop=True)


def build_gemini_context() -> str:
    kpis = get_kpis()
    return f"""Sos un asistente de Business Intelligence para el proyecto "Estrategia para la Reducción de la Brecha Digital Laboral en la Educación Técnica Superior" (UPDS, Bolivia).

DATOS ACTUALES DEL DASHBOARD:
- Tasa de empleo formal de egresados: {kpis['tasa_empleo']}%
- Egresados empleados en su área de estudio: {kpis['pct_area']}%
- Salario promedio de empleados: ${kpis['salario_prom']} USD/mes
- Total de egresados analizados: {kpis['total_egresados']}

ARQUITECTURA:
- Capa Bronze: SQL Server (BrechaDigitalDB) — datos crudos de estudiantes, carreras, inscripciones
- Capa Silver: Python/pandas — clean.py + normalize.py
- Capa Gold: SQL Server (DW_BrechaDigital) — esquema copo de nieve
- Dashboard: Streamlit + Plotly (esta aplicación)

CARRERAS ANALIZADAS: Ingeniería de Sistemas, Electrónica, Administración de Empresas.
CIUDADES: Tarija, La Paz, Santa Cruz, Cochabamba, Remoto.

Respondé preguntas sobre los datos, KPIs, tendencias y la brecha digital en Bolivia.
Sé conciso y orientado a insights de negocio. Respondé siempre en español."""
