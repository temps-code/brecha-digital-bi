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

from components.data_loader import load_df, get_kpis, get_tasa_desercion, get_cepal_benchmark, get_cepal_paises, get_cepal_pais_years
from components.charts import bar_tasa_desercion, bar_cepal_benchmark, bar_cepal_pais_years
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

df = load_df()

# --- Filtros Interactivos ---
with st.sidebar:
    st.markdown('<p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem">Filtros</p>', unsafe_allow_html=True)
    
    carreras = ['Todas'] + sorted(df['NombreCarrera'].dropna().unique().tolist())
    ciudades = ['Todas'] + sorted(df['Ciudad'].dropna().unique().tolist())

    carrera_sel = st.selectbox('Carrera', carreras)
    ciudad_sel  = st.selectbox('Ciudad', ciudades)

    # Year range filter
    year_range = st.slider(
        'Rango de Años de Egreso',
        min_value=2020,
        max_value=2028,
        value=(2024, 2028),
        step=1,
        help='Filtra KPIs por años de egreso'
    )
    
    # País CEPALSTAT filter — populated dynamically from data
    _ISO3_DISPLAY = {
        'arg': 'Argentina', 'atg': 'Antigua y Barbuda', 'blz': 'Belice',
        'bol': 'Bolivia', 'bra': 'Brasil', 'chl': 'Chile', 'col': 'Colombia',
        'cri': 'Costa Rica', 'cub': 'Cuba', 'dma': 'Dominica', 'dom': 'Rep. Dominicana',
        'ecu': 'Ecuador', 'gtm': 'Guatemala', 'hnd': 'Honduras', 'mex': 'México',
        'pan': 'Panamá', 'per': 'Perú', 'pry': 'Paraguay', 'ven': 'Venezuela',
    }
    _paises_disp = get_cepal_paises()
    _cepal_opciones = ['todos'] + _paises_disp
    cepal_pais_filter = st.selectbox(
        'País CEPALSTAT',
        _cepal_opciones,
        format_func=lambda x: 'Todos los países' if x == 'todos' else _ISO3_DISPLAY.get(x, x.upper()),
        help='Filtra el indicador de competencias TIC por país',
    )

df_f = df.copy()
if carrera_sel != 'Todas':
    df_f = df_f[df_f['NombreCarrera'] == carrera_sel]
if ciudad_sel != 'Todas':
    df_f = df_f[df_f['Ciudad'] == ciudad_sel]

if 'AñoEgreso' in df_f.columns:
    df_f = df_f[
        (df_f['AñoEgreso'] >= year_range[0]) &
        (df_f['AñoEgreso'] <= year_range[1])
    ]
elif 'SemestreActual' in df_f.columns and 'anio_y' in df_f.columns:
    df_f['AñoEgreso_Est'] = df_f['anio_y'] + (df_f['SemestreActual'] / 6).astype(int)
    df_f = df_f[
        (df_f['AñoEgreso_Est'] >= year_range[0]) &
        (df_f['AñoEgreso_Est'] <= year_range[1])
    ]

# ✅ Success Badge: IT Careers Detected
kpis         = get_kpis(df_f)
filtered_ids = df_f['EstudianteID'].tolist() if 'EstudianteID' in df_f.columns else None
desercion    = get_tasa_desercion(filtered_ids)
tasa_deser   = desercion.get('tasa_desercion')
valor_deser  = f"{tasa_deser:.1f}%" if tasa_deser is not None else "N/D"

st.markdown(f"""
<div style="background:#052e16;border:1px solid #166534;border-radius:6px;padding:0.65rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.5rem">
  <i class="ti ti-circle-check" style="color:#22C55E;font-size:1rem"></i>
  <span style="color:#86efac;font-size:0.875rem;font-weight:500">5 IT Carreras &nbsp;·&nbsp; {kpis.get("total_egresados", 0)} Egresados Analizados &nbsp;·&nbsp; Cobertura de salarios: {kpis.get("salary_coverage_pct", 0):.1f}%</span>
</div>
""", unsafe_allow_html=True)
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
st.caption('Este indicador muestra cuántos estudiantes están en riesgo de abandonar su carrera antes de terminar. Se considera "en riesgo" a quienes tienen nota menor a 51 y todavía no terminaron el último semestre. Verde = bajo riesgo, amarillo = moderado, rojo = alto.')

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- CEPALSTAT ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Benchmark Regional — CEPALSTAT</p>', unsafe_allow_html=True)
st.caption('Qué porcentaje de jóvenes en cada país sabe usar tecnología de información y comunicación (TIC). Es un indicador oficial de las Naciones Unidas (ODS 4.4.1) que permite comparar Bolivia con otros países de la región. El valor mostrado es el promedio de todos los años disponibles.')

if cepal_pais_filter == 'todos':
    # General view: one bar per country, averaged across all years
    cepal_bench = get_cepal_benchmark(paises=None)
    if cepal_bench.empty:
        st.warning('No se encontraron datos de CEPALSTAT.')
    else:
        st.plotly_chart(bar_cepal_benchmark(cepal_bench), use_container_width=True)
        with st.expander('Ver tabla de datos CEPALSTAT'):
            cepal_bench_display = cepal_bench.copy()
            cepal_bench_display['País'] = cepal_bench_display['iso3'].str.lower().map(_ISO3_DISPLAY).fillna(cepal_bench_display['iso3'].str.upper())
            st.dataframe(
                cepal_bench_display[['País', 'value']].rename(columns={'value': 'Promedio TIC (%)'}),
                use_container_width=True, hide_index=True,
            )
else:
    # Drill-down: one bar per year for the selected country
    pais_nombre = _ISO3_DISPLAY.get(cepal_pais_filter, cepal_pais_filter.upper())
    cepal_years = get_cepal_pais_years(cepal_pais_filter)
    if cepal_years.empty:
        st.warning(f'No se encontraron datos de CEPALSTAT para {pais_nombre}.')
    else:
        st.plotly_chart(bar_cepal_pais_years(cepal_years, pais_nombre), use_container_width=True)
        with st.expander(f'Ver tabla de datos — {pais_nombre}'):
            st.dataframe(
                cepal_years.rename(columns={'anio': 'Año', 'value': 'Jóvenes con competencias TIC (%)'}),
                use_container_width=True, hide_index=True,
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
