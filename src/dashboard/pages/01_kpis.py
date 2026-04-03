"""
Dashboard — Page 1: KPIs Generales
Responsable: Diego Vargas Urzagaste (@temps-code)

Muestra los indicadores clave del proyecto:
  - Tasa de inserción laboral general
  - Tasa de deserción por carrera
  - Comparación con benchmarks CEPALSTAT (ODS 4 y ODS 8)
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import get_kpis, get_cepal_bolivia
from components.charts import line_cepal_bolivia
from components.styles import inject_styles

st.set_page_config(page_title='KPIs — Brecha Digital BI', page_icon=':material/monitoring:', layout='wide')

inject_styles()

st.markdown("""
<div class="page-header">
  <h2><i class="ti ti-chart-dots-3"></i> KPIs Generales</h2>
  <p>Indicadores clave de inserción laboral y benchmark regional CEPALSTAT</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

kpis = get_kpis()

c1, c2, c3, c4 = st.columns(4)
for col, icon, label, value, caption in [
    (c1, 'ti-trending-up', 'Tasa de Empleo Formal',  f"{kpis['tasa_empleo']}%",
         'Egresados con empleo formal registrado'),
    (c2, 'ti-check',       'Empleados en su Área',   f"{kpis['pct_area']}%",
         'De los empleados, trabajan en su área de estudio'),
    (c3, 'ti-coin',        'Salario Promedio',        f"${kpis['salario_prom']} USD",
         'Salario mensual promedio de egresados empleados'),
    (c4, 'ti-users',       'Egresados Analizados',   str(kpis['total_egresados']), ''),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label"><i class="ti {icon}"></i>{label}</div>
      <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
    if caption:
        col.caption(caption)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- CEPALSTAT ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Benchmark Regional — CEPALSTAT</p>', unsafe_allow_html=True)
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

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- ODS ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.75rem">Alineación ODS</p>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    <div class="ods-card">
      <div class="ods-title"><i class="ti ti-school"></i> ODS 4 — Educación de calidad</div>
      <div class="ods-body">
        El porcentaje de egresados empleados en su área refleja la alineación
        entre la oferta educativa y el mercado laboral.
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown("""
    <div class="ods-card">
      <div class="ods-title"><i class="ti ti-building-factory-2"></i> ODS 8 — Trabajo decente y crecimiento</div>
      <div class="ods-body">
        La tasa de empleo formal y el salario promedio miden el acceso
        a trabajo digno para egresados de educación técnica superior.
      </div>
    </div>
    """, unsafe_allow_html=True)
