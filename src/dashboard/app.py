"""
Dashboard — Entry Point
Responsable: Diego Vargas Urzagaste (@temps-code)

Aplicación principal de Streamlit. Configura la navegación entre páginas:
  - 01_kpis.py        → Indicadores generales
  - 02_insercion.py   → Tasa de inserción laboral
  - 03_skill_gap.py   → Brecha de habilidades
  - 04_chatbot.py     → Asistente IA (Gemini API)
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from components.data_loader import get_kpis
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

# --- KPI cards ---
kpis = get_kpis()
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
for col, icon, title, desc in [
    (n1, 'ti-chart-dots-3', 'KPIs Generales',       'Indicadores clave + benchmark CEPALSTAT ODS 4.4.1'),
    (n2, 'ti-briefcase',    'Inserción Laboral',     'Empleo por carrera, ciudad y nivel salarial'),
    (n3, 'ti-target',       'Brecha de Habilidades', 'Demanda del mercado vs cobertura académica'),
    (n4, 'ti-robot',        'Asistente BI',          'Consultá los datos con lenguaje natural — Gemini'),
]:
    col.markdown(f"""
    <div class="nav-card">
      <i class="ti {icon} nav-icon"></i>
      <div class="nav-title">{title}</div>
      <div class="nav-desc">{desc}</div>
    </div>
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
