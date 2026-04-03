"""
Dashboard — Page 1: KPIs Generales
Responsable: Diego Vargas Urzagaste (@temps-code)

Muestra los indicadores clave del proyecto:
  - Tasa de inserción laboral general
  - Tasa de deserción por carrera
  - Comparación con benchmarks CEPALSTAT (ODS 4 y ODS 8)
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import get_kpis, get_cepal_bolivia
from components.charts import line_cepal_bolivia

st.set_page_config(page_title='KPIs — Brecha Digital BI', page_icon='📈', layout='wide')

st.markdown("""
<style>
  .page-header h2 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
  .page-header p  { color: #9CA3AF; font-size: 0.9rem; margin: 0; }
  .kpi-card  { background: #1E2130; border-radius: 12px; padding: 1.2rem 1.4rem;
               border: 1px solid #2A2D3E; }
  .kpi-label { font-size: 0.75rem; color: #9CA3AF; text-transform: uppercase;
               letter-spacing: 0.08em; margin-bottom: 0.2rem; }
  .kpi-value { font-size: 1.9rem; font-weight: 700; color: #F9FAFB; }
  .ods-card  { background: #1E2130; border-radius: 10px; padding: 1rem 1.2rem;
               border-left: 3px solid #2196F3; }
  hr.thin { border: none; border-top: 1px solid #2A2D3E; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h2>📈 KPIs Generales</h2>
  <p>Indicadores clave de inserción laboral y benchmark regional CEPALSTAT</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

kpis = get_kpis()

c1, c2, c3, c4 = st.columns(4)
for col, label, value, help_text in [
    (c1, 'Tasa de Empleo Formal',      f"{kpis['tasa_empleo']}%",
         'Porcentaje de egresados con empleo formal registrado'),
    (c2, 'Empleados en su Área',       f"{kpis['pct_area']}%",
         'De los empleados, qué % trabaja en su área de estudio'),
    (c3, 'Salario Promedio',           f"${kpis['salario_prom']} USD",
         'Salario mensual promedio de egresados empleados'),
    (c4, 'Egresados Analizados',       str(kpis['total_egresados']), ''),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
    if help_text:
        col.caption(help_text)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- CEPALSTAT ---
st.markdown('### Benchmark Regional — CEPALSTAT')
st.caption('Indicador 4.4.1: Proporción de jóvenes con competencias TIC · Bolivia')

cepal_bol = get_cepal_bolivia()
if cepal_bol.empty:
    st.warning('No se encontraron datos de CEPALSTAT para Bolivia.')
else:
    st.plotly_chart(line_cepal_bolivia(cepal_bol), use_container_width=True)
    with st.expander('Ver datos crudos CEPALSTAT'):
        st.dataframe(
            cepal_bol.rename(columns={'anio': 'Año', 'value': 'Valor (%)'}),
            use_container_width=True,
            hide_index=True,
        )

st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- ODS ---
st.markdown('### Alineación ODS')
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    <div class="ods-card">
      <b>ODS 4 — Educación de calidad</b><br>
      <span style="color:#9CA3AF;font-size:0.88rem">
        El porcentaje de egresados empleados en su área refleja la alineación
        entre la oferta educativa y el mercado laboral.
      </span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown("""
    <div class="ods-card">
      <b>ODS 8 — Trabajo decente y crecimiento económico</b><br>
      <span style="color:#9CA3AF;font-size:0.88rem">
        La tasa de empleo formal y el salario promedio miden el acceso
        a trabajo digno para egresados de educación técnica superior.
      </span>
    </div>
    """, unsafe_allow_html=True)
