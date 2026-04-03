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

st.title('📈 KPIs Generales')
st.caption('Indicadores clave de inserción laboral y benchmark regional CEPALSTAT')

kpis = get_kpis()

st.subheader('Indicadores del Proyecto')
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    label='Tasa de Empleo Formal',
    value=f"{kpis['tasa_empleo']}%",
    help='Porcentaje de egresados con empleo formal registrado',
)
c2.metric(
    label='Empleados en su Área',
    value=f"{kpis['pct_area']}%",
    help='De los empleados, qué % trabaja en su área de estudio',
)
c3.metric(
    label='Salario Promedio',
    value=f"${kpis['salario_prom']} USD",
    help='Salario mensual promedio de egresados empleados',
)
c4.metric(
    label='Total Egresados Analizados',
    value=kpis['total_egresados'],
)

st.divider()

st.subheader('Benchmark Regional — CEPALSTAT')
st.caption('Indicador 4.4.1: Proporción de jóvenes con competencias TIC — Bolivia')

cepal_bol = get_cepal_bolivia()

if cepal_bol.empty:
    st.warning('No se encontraron datos de CEPALSTAT para Bolivia.')
else:
    st.plotly_chart(line_cepal_bolivia(cepal_bol), use_container_width=True)
    with st.expander('Ver datos crudos CEPALSTAT'):
        st.dataframe(cepal_bol.rename(columns={'anio': 'Año', 'value': 'Valor'}), use_container_width=True)

st.divider()

st.subheader('Alineación con ODS')
col_a, col_b = st.columns(2)
with col_a:
    st.info('**ODS 4 — Educación de calidad**\nEl porcentaje de egresados empleados en su área indica la alineación entre la oferta educativa y el mercado laboral.')
with col_b:
    st.info('**ODS 8 — Trabajo decente y crecimiento económico**\nLa tasa de empleo formal y el salario promedio miden el acceso a trabajo digno para egresados de educación técnica superior.')
