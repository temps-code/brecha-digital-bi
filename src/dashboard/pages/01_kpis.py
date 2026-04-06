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

from components.data_loader import get_kpis, get_cepal_bolivia, get_tasa_desercion
from components.charts import line_cepal_bolivia, bar_tasa_desercion
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

# --- Filtros Interactivos ---
with st.sidebar:
    st.markdown('<p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem">Filtros</p>', unsafe_allow_html=True)
    
    # Year range filter
    year_range = st.slider(
        'Rango de Años de Egreso',
        min_value=2020,
        max_value=2028,
        value=(2024, 2028),
        step=1,
        help='Filtra KPIs por años de egreso'
    )
    
    # Región filter
    region_filter = st.selectbox(
        'Región CEPALSTAT',
        ['Todas', 'Bolivia', 'Región Andina'],
        help='Selecciona región para benchmark'
    )

# ✅ Success Badge: IT Careers Detected
kpis         = get_kpis()
desercion    = get_tasa_desercion()
tasa_deser   = desercion.get('tasa_desercion')
valor_deser  = f"{tasa_deser:.1f}%" if tasa_deser is not None else "N/D"

st.success(f'✅ 5 IT Carreras | {kpis.get("total_egresados", 0)} Egresados Analizados | Cobertura de salarios: {kpis.get("salary_coverage_pct", 0):.1f}%')
st.caption(f'Período de análisis: {kpis.get("graduation_year_range", "N/D")}')

# Display errors and warnings from KPIs validation
if kpis.get('_errors'):
    for error_msg in kpis['_errors']:
        if error_msg.startswith('❌'):
            st.error(error_msg)
        elif error_msg.startswith('⚠️'):
            st.warning(error_msg)
        else:
            st.info(error_msg)

c1, c2, c3, c4, c5 = st.columns(5)
for col, icon, label, value, caption in [
    (c1, 'ti-trending-up', 'Tasa de Empleo Formal',  f"{kpis['tasa_empleo']}%",
         'Egresados con empleo formal registrado'),
    (c2, 'ti-check',       'Empleados en su Área',   f"{kpis['pct_area']}%",
         'De los empleados, trabajan en su área de estudio'),
    (c3, 'ti-coin',        'Salario Promedio',        f"${kpis['salario_prom']} USD",
         'Salario mensual promedio de egresados empleados'),
    (c4, 'ti-users',       'Egresados Analizados',   str(kpis['total_egresados']), ''),
    (c5, 'ti-user-x',      'Tasa de Deserción',      valor_deser,
         'Heurística: SemestreActual < 8 y NotaFinal < 51 · Fuente: Silver'),
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

# --- Gauge de deserción ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Riesgo de Deserción Estudiantil</p>', unsafe_allow_html=True)
st.plotly_chart(bar_tasa_desercion(desercion), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- CEPALSTAT ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Benchmark Regional — CEPALSTAT</p>', unsafe_allow_html=True)
st.caption('Indicador 4.4.1: Proporción de jóvenes con competencias TIC · Bolivia')

cepal_bol = get_cepal_bolivia()
if cepal_bol.empty:
    st.warning('No se encontraron datos de CEPALSTAT para Bolivia.')
elif cepal_bol['anio'].nunique() == 1:
    anio_val = int(cepal_bol['anio'].iloc[0])
    val_prom = round(float(cepal_bol['value'].mean()), 1)
    val_max  = round(float(cepal_bol['value'].max()), 1)
    c1, c2 = st.columns(2)
    c1.metric(f'Variación promedio TIC ({anio_val})', f'{val_prom:+.1f}%')
    c2.metric('Indicador más alto', f'{val_max:+.1f}%')
    st.caption(f'Fuente: CEPALSTAT — {len(cepal_bol)} indicadores TIC para Bolivia · Datos disponibles solo para {anio_val}')
    with st.expander('Ver todos los indicadores CEPALSTAT'):
        st.dataframe(
            cepal_bol.rename(columns={'anio': 'Año', 'value': 'Valor (%)'}),
            use_container_width=True,
            hide_index=True,
        )
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
