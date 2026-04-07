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

# Habilidades que ofrece cada carrera — basado en planes de estudio reales
# Fuentes verificadas (2024-2026):
#   Ingeniería de Sistemas  → UMSA Informática (pensum oficial), UPB ISC (plan completo),
#                             UMSS (cs.umss.edu.bo), EMI (malla-sistemas-2024-2028)
#   Ingeniería de Software  → UPB ISC (semestres 4-9), UCB Ing. Sistemas (áreas SW),
#                             UMSA Informática (INF-272 Ingeniería de Software)
#   Ciencia de Datos        → UCB EPC "Negocios y Ciencia de Datos" (malla PDF oficial),
#                             UMSS Diplomado Ciencia de Datos, UPB Diplomado ML
#   Telecomunicaciones      → UMSA Electrónica y Telecomunicaciones (plan completo),
#                             UTEPSA Ing. Redes y Telecomunicaciones (plan completo),
#                             UCB Ing. Telecomunicaciones (áreas + CCNA/Cisco)
#   Ciberseguridad          → UTB Ing. Ciberseguridad e Informática (PDF plan oficial)
CARRERA_SKILLS = {
    # ─── Ingeniería de Sistemas ───────────────────────────────────────────────
    # UMSA: Algoritmos y Programación, Estructura de Datos, SO, BD, Telemática,
    #        Ing. Software, Simulación, Taller de Programación, Lenguajes Formales
    # UPB:  Programación I-III, BD Relacionales, BD Avanzadas, SO I, Patrones de
    #        Diseño, IA, Sistemas Distribuidos, Compilación, Teleinformática,
    #        Aplicaciones con Redes, Robótica, Seguridad Informática, Certificación I-III
    # EMI:  Sistemas de Información, Modelado, Simulación, Redes, Gestión
    'Ingeniería de Sistemas': [
        # Programación y lenguajes
        'Java', 'Python', 'C++', 'SQL', 'Assembler', 'Programación Funcional',
        # Estructuras y algoritmos
        'Algoritmos', 'Estructuras de Datos', 'Compiladores', 'Autómatas',
        # Bases de datos
        'Bases de Datos', 'PostgreSQL', 'MySQL', 'SQL Server',
        # Sistemas operativos y arquitectura
        'Sistemas Operativos', 'Linux', 'Arquitectura de Computadoras',
        'Sistemas Distribuidos', 'Virtualización',
        # Redes y comunicaciones
        'Redes', 'TCP/IP', 'Telemática', 'Protocolos de Comunicación',
        # Ingeniería de software
        'Ingeniería de Software', 'Patrones de Diseño', 'UML', 'Git',
        # Inteligencia y datos
        'Inteligencia Artificial', 'Machine Learning', 'Estadística',
        'Investigación de Operaciones', 'Simulación',
        # Gestión y metodología
        'Gestión de Proyectos', 'Scrum', 'Análisis y Diseño de Sistemas',
        # Seguridad
        'Seguridad Informática',
    ],

    # ─── Ingeniería de Software ───────────────────────────────────────────────
    # UPB ISC (sem 4-9): Ingeniería de Software, Patrones de Diseño, Proyecto de
    #   Ing. Software, BD Avanzadas, IA, Sistemas Distribuidos, Compilación,
    #   Aplicaciones con Redes, Tópicos Selectos en IS, Robótica, Seguridad Informática,
    #   Gestión de Proyectos Informáticos, HCI
    # UCB Ing. Sistemas: Software Engineering, Information Systems, AI, Networks, Security
    # UMSA Informática: INF-272 Ing. Software, Especificaciones Formales, Taller IS
    'Ingeniería de Software': [
        # Lenguajes y paradigmas
        'Java', 'Python', 'JavaScript', 'TypeScript', 'C#', '.NET',
        'Programación Funcional', 'Programación Orientada a Objetos',
        # Frameworks y desarrollo web
        'React', 'Node.js', 'Angular', 'Spring Boot', 'Django', 'REST API',
        # Bases de datos
        'SQL', 'Bases de Datos', 'PostgreSQL', 'MySQL', 'MongoDB',
        # Ingeniería y arquitectura
        'Ingeniería de Software', 'Patrones de Diseño', 'UML', 'Microservicios',
        'Sistemas Distribuidos', 'Arquitectura de Software',
        # Testing y calidad
        'Testing', 'Control de Versiones', 'Git', 'GitHub',
        # DevOps y despliegue
        'Docker', 'CI/CD', 'DevOps',
        # Gestión
        'Gestión de Proyectos', 'Scrum', 'Agile', 'JIRA',
        # IA y datos
        'Inteligencia Artificial', 'Machine Learning',
        # Seguridad y redes
        'Seguridad Informática', 'Redes', 'Aplicaciones Web',
    ],

    # ─── Ciencia de Datos ─────────────────────────────────────────────────────
    # UCB EPC "Negocios y Ciencia de Datos" (malla oficial PDF):
    #   Programación I y II, Estructura de Datos, Base de Datos I,
    #   Data Mining I, Machine Learning I y II, Data Warehousing,
    #   Estadística Descriptiva, Probabilidad I y II, Álgebra Lineal,
    #   Cálculo I y II, Cloud Computing, ERP y CRM, Inteligencia de Negocios,
    #   Simulación, Transformación Digital, Big Data & Marketing Predictivo,
    #   Seguridad Informática Empresarial, Procesos de Negocios
    # UMSS Diplomado: Visualización de Datos, Python para Ciencia de Datos
    # UPB Diplomado ML: Estadística aplicada, Pandas, Scikit-learn, Deep Learning
    'Ciencia de Datos': [
        # Programación
        'Python', 'R', 'SQL', 'Programación',
        # Librerías y herramientas DS
        'Pandas', 'NumPy', 'Scikit-learn', 'Matplotlib', 'Jupyter',
        # Machine Learning e IA
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
        'Data Mining', 'Inteligencia Artificial',
        # Bases de datos y almacenamiento
        'Bases de Datos', 'MySQL', 'Data Warehousing', 'Big Data',
        # Estadística y matemáticas
        'Estadística', 'Estadística Descriptiva', 'Probabilidad',
        'Álgebra Lineal', 'Cálculo',
        # Visualización y BI
        'Visualización de Datos', 'Power BI', 'Inteligencia de Negocios',
        # Cloud y plataformas
        'Cloud Computing', 'AWS', 'Spark', 'ERP', 'CRM',
        # Gestión y negocio
        'Gestión de Proyectos', 'Transformación Digital',
        'Seguridad Informática', 'Estructura de Datos',
    ],

    # ─── Telecomunicaciones y Redes ───────────────────────────────────────────
    # UMSA Electrónica y Telecomunicaciones (plan completo):
    #   Telecomunicaciones I y II, Sistemas de Comunicación Móvil, Tráfico Telefónico,
    #   Procesamiento Digital de Señales, Sistemas Digitales, Microprocesadores I y II,
    #   Líneas de Transmisión y Antenas, Fibra Óptica, Televisión, Informática Superior
    # UTEPSA Ing. Redes y Telecomunicaciones (plan completo, 9 semestres):
    #   Redes I-IV, Diseño de Cableado Estructurado, Comunicación Digital,
    #   Telefonía IP y Redes Convergentes, Líneas y Medios de Transmisión,
    #   Comunicación Óptica, Antenas y Sistemas de Radio, Redes Inalámbricas,
    #   Seguridad de la Información, Comunicación Satelital, Tecnologías Móviles,
    #   Seguridad y Gestión de Redes, Gestión de Servicios de TI
    # UCB Telecomunicaciones: Tecnologías Inalámbricas, Ciberseguridad,
    #   Sistemas de Comunicaciones Satelitales, CCNA/Cisco, Huawei HCIA, Mikrotik
    'Telecomunicaciones y Redes': [
        # Redes y protocolos
        'Redes', 'TCP/IP', 'IPv6', 'MPLS', 'VPN', 'Cisco', 'CCNA',
        'Routing', 'Switching', 'BGP', 'OSPF',
        # Telecomunicaciones físicas
        'Telecomunicaciones', 'Antenas', 'Fibra Óptica',
        'Procesamiento de Señales', 'Líneas de Transmisión',
        'Comunicación Satelital', 'Radiofrecuencia',
        # Redes inalámbricas y móviles
        'Redes Inalámbricas', 'WiFi', 'LTE', '5G',
        'Comunicación Móvil', 'Tecnologías Móviles',
        # VoIP y convergencia
        'VoIP', 'Telefonía IP', 'Redes Convergentes',
        # Cableado y diseño
        'Cableado Estructurado', 'Diseño de Redes',
        # Sistemas operativos y servidores
        'Linux', 'Sistemas Operativos',
        # Seguridad en redes
        'Seguridad de Redes', 'Firewalls', 'Seguridad Informática',
        # Gestión
        'Gestión de Servicios TI', 'ITIL',
        # Programación básica (plan de estudios)
        'Algoritmos', 'Programación',
    ],

    # ─── Ciberseguridad ───────────────────────────────────────────────────────
    # UTB Ing. Ciberseguridad e Informática (PDF plan oficial, 8 semestres):
    #   Introducción a la Ciberseguridad, Algoritmos y Programación I y II,
    #   Introducción a Redes de Computación, Derecho Informático (Delitos),
    #   Seguridad en Sistemas Contables, Fundamentos de Sistemas Digitales,
    #   Ingeniería de Software, Sistemas Virtualizados,
    #   Arquitectura de Sistemas, Interconexión de Redes Locales,
    #   Seguridad en Base de Datos I y II, Desarrollo de Aplicaciones y Servicio Web,
    #   Criptografía, Telecomunicaciones Móviles Redes de Datos,
    #   Seguridad de Redes, Seguridad en Sistemas Operativos,
    #   Gestión de la Seguridad Informática, Servidores y Servicios,
    #   Seguridad e Integración de Sistemas, Ciberseguridad,
    #   Auditoría en Seguridad Informática, Análisis y Explotación de Vulnerabilidades,
    #   Evaluación y Gestión de Proyectos Informáticos, Hacker Ético,
    #   Gestión de Incidentes, Ciberseguridad Gubernamental,
    #   Seguridad Informática Bancaria, Negocios y Comercio Electrónico
    'Ciberseguridad': [
        # Fundamentos de ciberseguridad
        'Ciberseguridad', 'Seguridad Informática', 'Criptografía',
        'Hacking Ético', 'Penetration Testing',
        # Redes y sistemas
        'Seguridad de Redes', 'Firewalls', 'VPN', 'Redes',
        'Sistemas Operativos', 'Linux', 'Virtualización',
        # Análisis y respuesta
        'Análisis de Vulnerabilidades', 'Gestión de Incidentes',
        'Auditoría de Seguridad', 'Forense Digital', 'Malware',
        # Bases de datos
        'Seguridad en Bases de Datos', 'SQL', 'Bases de Datos',
        # Marcos legales y gestión
        'Derecho Informático', 'ISO 27001', 'Gestión de Riesgos',
        'Cumplimiento Normativo', 'Gestión de Proyectos',
        # Desarrollo seguro
        'Ingeniería de Software', 'Desarrollo Web Seguro', 'Programación',
        'Algoritmos',
        # Comunicaciones
        'Telecomunicaciones', 'Protocolos de Red', 'Servidores',
        # Cloud y modernos
        'Seguridad Cloud', 'SIEM', 'SOC',
    ],
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


def get_kpis(df: pd.DataFrame) -> dict:
    """
    Retorna KPIs principales con validaciones de calidad de datos.
    
    Args:
        df: Filtered DataFrame to compute KPIs from.
    
    Returns:
        dict with keys: tasa_empleo, pct_area, salario_prom, total_egresados, 
                       graduation_year_range, _errors
    """
    errors = []
    
    if df is None or df.empty:
        return {
            'tasa_empleo': 0.0,
            'pct_area': 0.0,
            'salario_prom': 0.0,
            'total_egresados': 0,
            'graduation_year_range': 'N/D',
            'salary_coverage_pct': 0.0,
            '_errors': ["⚠️ No hay datos disponibles para el filtro seleccionado"],
        }

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


def get_empleo_por_carrera(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['NombreCarrera', 'tasa_empleo'])
        
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


def get_distribucion_ciudad(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['Ciudad', 'total'])
        
    return (
        df.groupby('Ciudad')['EstudianteID']
        .count()
        .reset_index()
        .rename(columns={'EstudianteID': 'total'})
        .sort_values('total', ascending=False)
    )


def get_salario_por_carrera(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['NombreCarrera', 'salario_promedio'])
        
    empleados = df[df['TieneEmpleoFormal'] == True].dropna(subset=['SalarioMensualUSD'])
    return (
        empleados.groupby('NombreCarrera')['SalarioMensualUSD']
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={'SalarioMensualUSD': 'salario_promedio'})
        .sort_values('salario_promedio', ascending=True)
    )


def get_habilidades_demandadas(ciudad_filter: str = 'Todas') -> pd.DataFrame:
    """
    Load demanded skills from extracted skills CSV (Groq LLM).

    Args:
        ciudad_filter: City to filter jobs by ('Todas' for no filter)
    """
    import json
    import os

    conteo = {}
    skills_csv = PROCESSED / 'empleos' / 'skills_extracted.csv'

    # PRIORITY 1: Try loading from extracted skills CSV
    if skills_csv.exists():
        try:
            extracted = pd.read_csv(skills_csv)

            # City filter mapping (Adzuna cities are complex strings)
            if ciudad_filter != 'Todas':
                # Simple containment check for city filter
                extracted = extracted[extracted['location'].str.contains(ciudad_filter, case=False, na=False)]

            # Aggregate skills from JSON column
            for _, row in extracted.iterrows():
                try:
                    skills = json.loads(row['skills_json'])
                    for skill in skills:
                        if skill and len(skill) > 1:
                            conteo[skill] = conteo.get(skill, 0) + 1
                except (json.JSONDecodeError, KeyError):
                    pass
            
            if conteo:
                return (
                    pd.DataFrame(list(conteo.items()), columns=['habilidad', 'demanda'])
                    .sort_values('demanda', ascending=False)
                )
        except Exception as e:
            st.warning(f"⚠️ Error loading extracted skills: {str(e)}, falling back to tokenization")
    
    # PRIORITY 2: Fallback to naive tokenization (comma/semicolon split)
    vac = load_vacantes()
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
        # PRIORITY 3: Static SKILLS_MAP
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


def get_skill_gap(hab_academicas: dict = None, ciudad_filter: str = 'Todas') -> pd.DataFrame:
    """
    Retorna demanda de mercado vs cobertura académica con fuzzy matching.
    """
    errors = []

    try:
        dem = get_habilidades_demandadas(ciudad_filter=ciudad_filter)
        if dem.empty:
            errors.append("⚠️ No se encontraron habilidades demandadas para la selección")
            return pd.DataFrame(
                columns=['habilidad', 'demanda', 'similarity_score', 'cobertura_%', 'carrera', '_errors']
            )
    except Exception as e:
        errors.append(f"❌ Error cargando habilidades demandadas: {str(e)}")
        return pd.DataFrame(
            columns=['habilidad', 'demanda', 'similarity_score', 'cobertura_%', 'carrera', '_errors']
        )    
    if hab_academicas is None:
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
def load_habilidades_academicas() -> dict[str, list[str]]:
    """
    Retorna dict {carrera: [habilidades]} agrupando habilidades académicas por carrera.
    Estrategia Gold: DIM_HABILIDAD JOIN DIM_CARRERA.
    Fallback CSV: processed/competenciasdigitales_cleaned.csv (solo si keys intersectan IT_CAREERS).
    Fallback final → CARRERA_SKILLS.copy() (currículos bolivianos verificados).
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

    # Fallback: CSV processed — solo si las keys coinciden con IT_CAREERS
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
        if set(result.keys()) & set(IT_CAREERS):
            return result
    except Exception:
        pass

    return {k: list(v) for k, v in CARRERA_SKILLS.items()}


def get_tasa_desercion(filtered_ids: list = None) -> dict:
    """
    Retorna dict con tasa_desercion (float), total_estudiantes (int), en_riesgo (int).
    Fuente: data/processed/silver_integrated_data.csv
    Heurística de riesgo: SemestreActual < 8 AND NotaFinal < 51.
    """
    try:
        path = PROCESSED / 'silver_integrated_data.csv'
        df = pd.read_csv(path)
        
        # Apply filtering if ids provided
        if filtered_ids is not None:
            df = df[df['EstudianteID'].isin(filtered_ids)]
            
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


def get_empleo_temporal(df: pd.DataFrame = None) -> pd.DataFrame:
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
    
    # If df provided, we use it for fallback analysis instead of reloading silver
    # But Gold query usually doesn't take the filtered df directly unless we refactor it
    # For now, we'll keep Gold as global and fallback as filtered if df is provided.
    
    engine = _gold_engine()
    if engine is not None and df is None: # Only use Gold for global view
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
            df_gold = pd.read_sql(sql, engine)
            df_gold['fuente'] = 'Gold'
            if errors:
                df_gold['_errors'] = [errors] * len(df_gold)
            else:
                df_gold['_errors'] = [[] for _ in range(len(df_gold))]
            return df_gold[['anio', 'tasa_empleo', 'fuente', '_errors']]
        except Exception as e:
            errors.append(f"ℹ️ Gold layer unavailable: {str(e)}")
    
    # Fallback: use silver or provided df
    try:
        if df is not None:
            # df viene de load_df() que ya fusionó seguimientoegresados — no re-mergear
            merged = df.copy()
        else:
            silver = pd.read_csv(PROCESSED / 'silver_integrated_data.csv')
            seg = pd.read_csv(PROCESSED / 'seguimientoegresados_cleaned.csv')

            if 'EstudianteID' not in seg.columns or 'TieneEmpleoFormal' not in seg.columns:
                errors.append("❌ Columnas requeridas no encontradas en seguimientoegresados_cleaned.csv")
                return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])

            merged = silver.merge(seg, on='EstudianteID', how='inner')

            if merged.empty:
                errors.append("⚠️ No se encontraron registros comunes para análisis temporal")
                return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])

        if 'EstudianteID' not in merged.columns:
            errors.append("❌ Columna EstudianteID no encontrada para análisis temporal")
            return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])

        if 'TieneEmpleoFormal' not in merged.columns:
            errors.append("❌ Columna TieneEmpleoFormal no disponible")
            return pd.DataFrame(columns=['anio', 'tasa_empleo', 'fuente', '_errors'])

        # Calcular graduation_year si no viene ya calculado por load_df()
        if 'graduation_year' not in merged.columns:
            if 'SemestreActual' not in merged.columns or 'anio_y' not in merged.columns:
                errors.append("⚠️ Columnas SemestreActual/anio_y no encontradas, usando anio_x")
                merged = merged.copy()
                merged['graduation_year'] = merged.get('anio_x', 2020) + 4
            else:
                merged = merged.copy()
                merged['graduation_year'] = _validate_graduation_year(merged)

        merged['TieneEmpleoFormal'] = (
            merged['TieneEmpleoFormal']
            .map({True: 1, False: 0, 'True': 1, 'False': 0, 1.0: 1, 0.0: 0})
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
        result_df.loc[0, '_errors'] = [errors]
        return result_df



ANDINOS = ['bol', 'per', 'ecu', 'col']


@st.cache_data
def get_cepal_bolivia(region: str = 'Bolivia') -> pd.DataFrame:
    """Indicador CEPALSTAT — lee desde processed/cepalstat/.

    Args:
        region: 'Bolivia' (solo BOL), 'Región Andina' (BOL+PER+ECU+COL), 'Todas' (sin filtro ISO).
    Returns:
        DataFrame con columnas [anio, value, iso3].
    """
    try:
        cep = pd.read_csv(PROCESSED / 'cepalstat' / 'indicadores_tic_region_cleaned.csv')
        cep['_iso3_lower'] = cep['iso3'].str.lower()
        base = cep[cep['dim_28619'] == 28620].copy()
        if region == 'Bolivia':
            filtered = base[base['_iso3_lower'] == 'bol']
        elif region == 'Región Andina':
            filtered = base[base['_iso3_lower'].isin(ANDINOS)]
        else:
            filtered = base
        # Aggregate by year+country to eliminate duplicate sub-indicator rows
        # (multiple indicator rows per year cause overlapping flat lines in px.line)
        result = (
            filtered
            .groupby(['anio', 'iso3'], as_index=False)['value']
            .mean()
            .sort_values('anio')
            .reset_index(drop=True)
        )
        return result
    except Exception:
        st.warning('No se pudo cargar el indicador CEPALSTAT.')
        return pd.DataFrame(columns=['anio', 'value', 'iso3'])


@st.cache_data
def get_cepal_paises() -> list[str]:
    """Returns sorted list of available ISO3 country codes in the CEPALSTAT dataset."""
    try:
        cep = pd.read_csv(PROCESSED / 'cepalstat' / 'indicadores_tic_region_cleaned.csv')
        base = cep[cep['dim_28619'] == 28620].copy()
        return sorted(base['iso3'].str.lower().unique().tolist())
    except Exception:
        return ['bol']


@st.cache_data
def get_cepal_pais_years(iso3: str) -> pd.DataFrame:
    """Returns CEPALSTAT data for a single country, one row per year (averaged across sub-indicators).

    Args:
        iso3: Country ISO3 code (lowercase), e.g. 'bol'.
    Returns:
        DataFrame with columns [anio, value] sorted by year.
    """
    try:
        cep = pd.read_csv(PROCESSED / 'cepalstat' / 'indicadores_tic_region_cleaned.csv')
        base = cep[cep['dim_28619'] == 28620].copy()
        filtered = base[base['iso3'].str.lower() == iso3.lower()]
        result = (
            filtered
            .groupby('anio', as_index=False)['value']
            .mean()
            .round(1)
            .sort_values('anio')
            .reset_index(drop=True)
        )
        return result
    except Exception:
        return pd.DataFrame(columns=['anio', 'value'])


@st.cache_data
def get_cepal_benchmark(paises: tuple | None = None) -> pd.DataFrame:
    """Returns CEPALSTAT data averaged across all available years, one row per country.

    Args:
        paises: Tuple of ISO3 codes (lowercase) to include, or None for all.
    Returns:
        DataFrame with columns [iso3, value] sorted by value descending.
    """
    try:
        cep = pd.read_csv(PROCESSED / 'cepalstat' / 'indicadores_tic_region_cleaned.csv')
        base = cep[cep['dim_28619'] == 28620].copy()
        base['_iso3_lower'] = base['iso3'].str.lower()
        if paises:
            base = base[base['_iso3_lower'].isin(paises)]
        result = (
            base.groupby('iso3', as_index=False)['value']
            .mean()
            .round(1)
            .sort_values('value', ascending=False)
            .reset_index(drop=True)
        )
        return result
    except Exception:
        return pd.DataFrame(columns=['iso3', 'value'])


def build_groq_context(kpis: dict | None = None, gap_df=None) -> str:
    df = load_df()
    if kpis is None:
        kpis = get_kpis(df)
    if gap_df is None:
        try:
            gap_df = get_skill_gap()
        except Exception:
            gap_df = None

    # Bloque brechas críticas — top 3 por demanda con cobertura < 50%
    brechas_bloque = ''
    try:
        if gap_df is not None and not gap_df.empty:
            criticas = (
                gap_df[gap_df['cobertura_%'] < 50]
                .sort_values('demanda', ascending=False)
                .head(3)
            )
            if not criticas.empty:
                lines = []
                for _, row in criticas.iterrows():
                    skill = str(row['habilidad'])[:30]
                    lines.append(f"  {skill}: {row['demanda']} vacantes, {row['cobertura_%']:.0f}% cobertura")
                brechas_bloque = '\nBRECHAS CRÍTICAS (top 3 por demanda):\n' + '\n'.join(lines)
    except Exception:
        pass

    # Bloque CEPALSTAT — último dato disponible
    cepalstat_bloque = ''
    try:
        cepal = get_cepal_bolivia()
        if not cepal.empty:
            ultimo = cepal.iloc[-1]
            cepalstat_bloque = f'\nCEPALSTAT ODS 4.4.1 ({int(ultimo["anio"])}): {float(ultimo["value"]):.1f}% jóvenes con competencias TIC en Bolivia'
    except Exception:
        pass

    # Bloque deserción
    desercion_bloque = ''
    try:
        des = get_tasa_desercion()
        if des.get('tasa_desercion') is not None:
            desercion_bloque = f'\nDESERCIÓN: {des["tasa_desercion"]}% (heurística: semestre<8 y nota<51)'
    except Exception:
        pass

    return f"""Sos un asistente de BI para "Brecha Digital Laboral en Educación TIC — Bolivia" (UPDS).

SCOPE: 5 carreras IT (Sistemas, Software, Datos, Telecomunicaciones, Ciberseguridad) · cohortes 2024-2028 · fuzzy matching 0.80.

KPIs:
- Empleo formal: {kpis['tasa_empleo']}% · En área: {kpis['pct_area']}% · Salario: ${kpis['salario_prom']} USD/mes
- Egresados: {kpis['total_egresados']} · Cobertura salarios: {kpis.get('salary_coverage_pct', 0):.1f}%{brechas_bloque}{cepalstat_bloque}{desercion_bloque}

METODOLOGÍA: Medallion (Bronze SQL→Silver pandas→Gold DW) + LLaMA 3.1 vía Groq.
Respondé en español, conciso, orientado a insights de negocio."""


def get_skill_gap_filtered(hab_academicas: dict = None, top_n: int = 15, ciudad_filter: str = 'Todas') -> tuple[pd.DataFrame, int]:
    """
    Retorna skill gap pero filtrando solo las top N habilidades demandadas.
    Las demás se agrupan en un contador.

    Returns:
        (filtered_df, count_other_skills): DataFrame con top N + count de otros
    """
    full_gap = get_skill_gap(hab_academicas, ciudad_filter=ciudad_filter)

    if full_gap.empty:
        return full_gap, 0

    filtered = full_gap.head(top_n).copy()
    other_count = len(full_gap) - len(filtered)

    return filtered, other_count


def get_habilidades_demandadas_filtered(top_n: int = 10, ciudad_filter: str = 'Todas') -> tuple[pd.DataFrame, int]:
    """
    Retorna habilidades demandadas filtradas a top N.

    Returns:
        (filtered_df, count_other): DataFrame con top N + count de otros
    """
    full_hab = get_habilidades_demandadas(ciudad_filter=ciudad_filter)

    if full_hab.empty:
        return full_hab, 0

    filtered = full_hab.head(top_n).copy()
    other_count = len(full_hab) - len(filtered)

    return filtered, other_count
