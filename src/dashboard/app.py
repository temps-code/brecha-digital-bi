"""
Dashboard — Entry Point
Responsable: Diego Vargas Urzagaste (@temps-code)

Aplicación principal de Streamlit. Configura la navegación entre páginas:
  - 01_kpis.py        → Indicadores generales
  - 02_insercion.py   → Tasa de inserción laboral
  - 03_skill_gap.py   → Brecha de habilidades
  - 04_chatbot.py     → Asistente IA (Gemini API)
"""
import streamlit as st
from components.data_loader import get_kpis

st.set_page_config(
    page_title='Brecha Digital BI — UPDS',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown("""
<style>
  .hero { padding: 2rem 0 1rem 0; }
  .hero h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.25rem; }
  .hero p  { color: #9CA3AF; font-size: 1rem; margin: 0; }
  .kpi-label { font-size: 0.78rem; color: #9CA3AF; text-transform: uppercase;
               letter-spacing: 0.08em; margin-bottom: 0.15rem; }
  .kpi-value { font-size: 2rem; font-weight: 700; color: #F9FAFB; }
  .kpi-card  { background: #1E2130; border-radius: 12px; padding: 1.2rem 1.4rem;
               border: 1px solid #2A2D3E; }
  .nav-card  { background: #1E2130; border-radius: 10px; padding: 1rem 1.2rem;
               border: 1px solid #2A2D3E; margin-bottom: 0.5rem; }
  .nav-icon  { font-size: 1.4rem; margin-bottom: 0.3rem; }
  .nav-title { font-weight: 600; font-size: 0.95rem; color: #F9FAFB; }
  .nav-desc  { font-size: 0.82rem; color: #6B7280; margin-top: 0.1rem; }
  .badge     { display: inline-block; background: #1D4ED8; color: #BFDBFE;
               font-size: 0.72rem; font-weight: 600; padding: 2px 8px;
               border-radius: 20px; margin-right: 4px; }
  .source-row { font-size: 0.82rem; color: #6B7280; margin-top: 0.25rem; }
  hr.thin { border: none; border-top: 1px solid #2A2D3E; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- Hero ---
st.markdown("""
<div class="hero">
  <h1>📊 Brecha Digital Laboral</h1>
  <p>Estrategia para la Reducción de la Brecha Digital en la Educación Técnica Superior · UPDS Bolivia · 2026</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- KPI cards ---
kpis = get_kpis()
c1, c2, c3, c4 = st.columns(4)
for col, label, value in [
    (c1, 'Tasa de Empleo Formal',   f"{kpis['tasa_empleo']}%"),
    (c2, 'Empleados en su Área',    f"{kpis['pct_area']}%"),
    (c3, 'Salario Promedio',        f"${kpis['salario_prom']} USD"),
    (c4, 'Egresados Analizados',    str(kpis['total_egresados'])),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- Navegación visual ---
st.markdown('### Explorá el análisis')
n1, n2, n3, n4 = st.columns(4)
for col, icon, title, desc in [
    (n1, '📈', 'KPIs Generales',        'Indicadores clave + benchmark CEPALSTAT ODS 4.4.1'),
    (n2, '💼', 'Inserción Laboral',      'Empleo por carrera, ciudad y nivel salarial'),
    (n3, '🎯', 'Brecha de Habilidades',  'Demanda del mercado vs cobertura académica'),
    (n4, '🤖', 'Asistente BI',           'Consultá los datos con lenguaje natural — Gemini'),
]:
    col.markdown(f"""
    <div class="nav-card">
      <div class="nav-icon">{icon}</div>
      <div class="nav-title">{title}</div>
      <div class="nav-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- Fuentes y alineación ODS ---
left, right = st.columns([2, 1])
with left:
    st.markdown('**Fuentes de datos**')
    st.markdown("""
    <div class="source-row">📦 <b>Bronze</b> — SQL Server (BrechaDigitalDB): estudiantes, inscripciones, egresados</div>
    <div class="source-row">🔬 <b>Silver</b> — Python/pandas: clean.py + normalize.py</div>
    <div class="source-row">🏅 <b>Gold</b> — DW_BrechaDigital: esquema copo de nieve</div>
    <div class="source-row">🌐 <b>CEPALSTAT</b> — Indicador 4.4.1 (Competencias TIC en jóvenes)</div>
    <div class="source-row">💻 <b>Adzuna API</b> — Vacantes tecnológicas activas en Bolivia</div>
    """, unsafe_allow_html=True)
with right:
    st.markdown('**Alineación ODS**')
    st.markdown("""
    <span class="badge">ODS 4</span> Educación de calidad<br><br>
    <span class="badge">ODS 8</span> Trabajo decente y crecimiento
    """, unsafe_allow_html=True)
