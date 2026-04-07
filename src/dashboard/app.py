import sys
import os
from pathlib import Path
import datetime

import streamlit as st

# Inject Streamlit Cloud secrets into os.environ so os.getenv() calls work
# throughout the codebase (data_loader, chatbot, ingestion scripts).
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)
except Exception:
    pass  # Running locally with .env — dotenv handles it

sys.path.insert(0, str(Path(__file__).resolve().parent))

from components.data_loader import get_kpis, load_df
from components.styles import inject_styles

st.set_page_config(
    page_title='Brecha Digital BI — UPDS',
    page_icon=':material/monitoring:',
    layout='wide',
    initial_sidebar_state='expanded',
)

inject_styles()

# --- Hero ---
st.markdown("""
<div class="page-header">
  <h2><i class="ti ti-chart-dots-3"></i> Brecha Digital Laboral</h2>
  <p>Estrategia para la Reducción de la Brecha Digital en la Educación Técnica Superior &nbsp;·&nbsp; UPDS Bolivia &nbsp;·&nbsp; 2026</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- ODS & Mission Context ---
st.markdown("""
<div style="background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;">
  <div style="display: flex; gap: 1rem; align-items: start;">
    <div style="font-size: 2rem;">🎯</div>
    <div>
      <h3 style="margin: 0 0 0.5rem 0; color: var(--text); font-size: 1rem;">Misión: Reducir la Brecha Digital en Habilidades TIC</h3>
      <p style="margin: 0 0 0.75rem 0; color: var(--muted); font-size: 0.9rem;">
        Este dashboard analiza la alineación entre la oferta educativa en carreras IT y la demanda del mercado laboral boliviano, 
        vinculado directamente a los <strong>ODS 4 (Educación de Calidad)</strong> y <strong>ODS 8 (Trabajo Decente e Innovación)</strong>.
      </p>
      <p style="margin: 0; color: var(--text); font-size: 0.9rem; font-weight: 500;">
        <i class="ti ti-target" style="color: var(--accent); margin-right: 0.25rem;"></i> 
        Objetivo 2026: 85% de egresados IT con empleo formal en su área de estudio
      </p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Data Quality Indicator Card ---
df = load_df()
kpis = get_kpis(df)

col_dq1, col_dq2, col_dq3, col_dq4 = st.columns(4)

with col_dq1:
    st.metric(
        label=':material/school: Carreras IT detectadas',
        value='5',
        delta=None,
        help='Ingeniería de Sistemas, Software, Datos, Telecomunicaciones, Ciberseguridad'
    )

with col_dq2:
    total_students = len(df) if df is not None and not df.empty else 0
    st.metric(
        label=':material/group: Estudiantes cargados',
        value=f'{total_students:,}',
        delta=None,
    )

with col_dq3:
    salary_coverage = kpis.get('salary_coverage_pct', 0)
    st.metric(
        label=':material/bar_chart: Cobertura de salarios',
        value=f'{salary_coverage:.1f}%',
        delta=None,
        help='Porcentaje de registros con datos de salario disponibles'
    )

with col_dq4:
    try:
        _csv_path = Path(__file__).resolve().parents[2] / 'data' / 'processed' / 'estudiantes_cleaned.csv'
        _mtime = _csv_path.stat().st_mtime
        last_updated = datetime.datetime.fromtimestamp(_mtime).strftime('%Y-%m-%d')
    except Exception:
        last_updated = 'N/D'
    st.metric(
        label=':material/calendar_today: Datos al',
        value=last_updated,
        delta=None,
        help='Fecha de última modificación de los archivos CSV procesados'
    )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Data Attribution (Phase 2.5) ---
with st.expander("Fuentes de Datos", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.5rem 0">Procedencia</p>
        <div class="source-item"><i class="ti ti-database"></i><span><b>Primaria</b> — SQL Server DW_BrechaDigital (Gold layer)</span></div>
        <div class="source-item"><i class="ti ti-file-description"></i><span><b>Secundaria</b> — Archivos CSV procesados (fallback)</span></div>
        <div class="source-item"><i class="ti ti-robot"></i><span><b>Skills de mercado</b> — Adzuna API + extracción con IA (Groq)</span></div>
        <br>
        <p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.5rem 0">Datos Incluidos</p>
        <div class="source-item"><i class="ti ti-school"></i><span>5 carreras IT: Sistemas, Software, Ciencia de Datos, Telecomunicaciones, Ciberseguridad</span></div>
        <div class="source-item"><i class="ti ti-calendar"></i><span>Año de graduación estimado desde semestre actual y año de ingreso</span></div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.5rem 0">Cobertura</p>
        <div class="source-item"><i class="ti ti-users"></i><span><b>Estudiantes</b> — registro completo desde ingreso</span></div>
        <div class="source-item"><i class="ti ti-briefcase"></i><span><b>Empleo</b> — seguimiento post-egreso</span></div>
        <div class="source-item"><i class="ti ti-coin"></i><span><b>Salarios</b> — {salary_coverage:.0f}% de empleados con dato reportado</span></div>
        <br>
        <p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.5rem 0">Validación</p>
        <div class="source-item"><i class="ti ti-filter"></i><span>Carreras filtradas a 5 programas IT</span></div>
        <div class="source-item"><i class="ti ti-check"></i><span>Datos de calidad revisados automáticamente</span></div>
        <div class="source-item"><i class="ti ti-shield"></i><span>Valores faltantes preservados (no imputados)</span></div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- KPI cards ---
# Show loader errors if any (Phase 2)
if '_errors' in kpis and kpis['_errors']:
    for error_msg in kpis['_errors']:
        if '❌' in error_msg:
            st.error(error_msg)
        elif '⚠️' in error_msg or 'ℹ️' in error_msg:
            st.warning(error_msg)

c1, c2, c3, c4 = st.columns(4)
for col, icon, label, value in [
    (c1, 'ti-trending-up',  'Tasa de Empleo Formal',  f"{kpis['tasa_empleo']}%"),
    (c2, 'ti-check',        'Empleados en su Área',   f"{kpis['pct_area']}%"),
    (c3, 'ti-coin',         'Salario Promedio',        f"${kpis['salario_prom']} USD"),
    (c4, 'ti-users',        'Egresados Analizados',    str(kpis['total_egresados'])),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label"><i class="ti {icon}"></i>{label}</div>
      <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Navegación visual ---
st.markdown('<p style="font-size:0.8125rem;font-weight:500;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem">Explorá el análisis</p>', unsafe_allow_html=True)

n1, n2, n3, n4 = st.columns(4)
for col, icon, title, desc, href in [
    (n1, 'ti-chart-dots-3', 'KPIs Generales',       'Indicadores clave + benchmark CEPALSTAT ODS 4.4.1', '/kpis'),
    (n2, 'ti-briefcase',    'Inserción Laboral',     'Empleo por carrera, ciudad y nivel salarial',       '/insercion'),
    (n3, 'ti-target',       'Brecha de Habilidades', 'Skills extraídas con IA · Brecha académica vs mercado', '/skill_gap'),
    (n4, 'ti-robot',        'Asistente BI',          'Consultá los datos con lenguaje natural — LLaMA 3.1 (Groq)', '/chatbot'),
]:
    col.markdown(f"""
    <a href="{href}" target="_self" class="nav-link">
      <div class="nav-card">
        <i class="ti {icon} nav-icon"></i>
        <div class="nav-title">{title}</div>
        <div class="nav-desc">{desc}</div>
      </div>
    </a>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Fuentes y alineación ODS ---
left, right = st.columns([3, 2])

with left:
    st.markdown('<p style="font-size:0.8125rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Fuentes de datos</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="source-item"><i class="ti ti-database"></i><span><b>Bronze</b> — SQL Server (BrechaDigitalDB): estudiantes, inscripciones, egresados</span></div>
    <div class="source-item"><i class="ti ti-filter"></i><span><b>Silver</b> — Python/pandas: clean.py + normalize.py</span></div>
    <div class="source-item"><i class="ti ti-award"></i><span><b>Gold</b> — DW_BrechaDigital: esquema copo de nieve</span></div>
    <div class="source-item"><i class="ti ti-world"></i><span><b>CEPALSTAT</b> — Indicador 4.4.1 (Competencias TIC en jóvenes)</span></div>
    <div class="source-item"><i class="ti ti-api"></i><span><b>Adzuna API</b> — Vacantes tecnológicas activas en Bolivia</span></div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<p style="font-size:0.8125rem;font-weight:600;color:#FAFAFA;margin-bottom:0.5rem">Alineación ODS</p>', unsafe_allow_html=True)
    st.markdown("""
    <span class="badge"><i class="ti ti-school"></i> ODS 4</span> Educación de calidad<br><br>
    <span class="badge"><i class="ti ti-building-factory-2"></i> ODS 8</span> Trabajo decente y crecimiento
    """, unsafe_allow_html=True)
