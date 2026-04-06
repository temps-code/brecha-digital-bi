import sys
from pathlib import Path
import datetime

import streamlit as st

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

# --- Data Quality Indicator Card ---
df = load_df()
kpis_preview = get_kpis()

col_dq1, col_dq2, col_dq3, col_dq4 = st.columns(4)

with col_dq1:
    st.metric(
        label='✅ Carreras IT Detectadas',
        value='5',
        delta=None,
        help='Ingeniería de Sistemas, Software, Datos, Telecomunicaciones, Ciberseguridad'
    )

with col_dq2:
    total_students = len(df) if df is not None and not df.empty else 0
    st.metric(
        label='✅ Estudiantes Cargados',
        value=f'{total_students:,}',
        delta=None,
    )

with col_dq3:
    salary_coverage = kpis_preview.get('salary_coverage_pct', 0)
    delta_color = '✓' if salary_coverage >= 70 else '⚠'
    st.metric(
        label='📊 Cobertura de Salarios',
        value=f'{salary_coverage:.1f}%',
        delta=delta_color,
        help='Porcentaje de registros con datos de salario disponibles'
    )

with col_dq4:
    now = datetime.datetime.now()
    last_updated = now.strftime('%Y-%m-%d %H:%M')
    st.metric(
        label='🔄 Última Actualización',
        value=last_updated,
        delta=None,
    )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Data Attribution (Phase 2.5) ---
with st.expander("📊 Fuentes de Datos", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Procedencia:**
        - 🔵 **Primaria**: SQL Server DW_BrechaDigital (Gold layer) — Cuando está disponible
        - 🟡 **Secundaria**: Local CSVs — Fallback cuando Gold no responde
        - 📅 **Última actualización**: Diaria a las 2 AM UTC
        
        **Datos Incluidos:**
        - Filtro IT: 5 carreras (Ingeniería de Sistemas, Software, Ciencia de Datos, Telecomunicaciones, Ciberseguridad)
        - Año de graduación: Estimado desde semestre actual y año de ingreso
        """)
    with col2:
        st.markdown("""
        **Cobertura:**
        - 📌 Estudiantes: Registro completo desde ingreso
        - 💼 Empleo: Seguimiento post-egreso
        - 💰 Salarios: ~70% de empleados reportados
        
        **Validación:**
        - Carreras filtradas a 5 programas IT
        - Datos de calidad revisados automáticamente
        - Valores faltantes preservados (no imputados)
        """)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- KPI cards ---
kpis = get_kpis()

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
