"""
Dashboard — Page 2: Inserción Laboral
Responsable: Diego Vargas Urzagaste (@temps-code)

Visualiza la tasa de inserción laboral de egresados:
  - Por carrera
  - Por región/departamento de Bolivia
  - Evolución temporal
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import load_df, get_empleo_por_carrera, get_salario_por_carrera, get_empleo_temporal
from components.charts import bar_empleo_por_carrera, pie_distribucion_ciudad, bar_salario_por_carrera, line_empleo_temporal
from components.styles import inject_styles

st.set_page_config(page_title='Inserción Laboral — Brecha Digital BI', page_icon=':material/work:', layout='wide')

inject_styles()

st.markdown("""
<div class="page-header">
  <h2><i class="ti ti-briefcase"></i> Inserción Laboral</h2>
  <p>Análisis de empleo por carrera, ciudad y nivel salarial</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

df = load_df()

# ✅ Career Filter Info
st.success('Showing: Ingeniería de Sistemas, Software, Data, Telecomunicaciones, Ciberseguridad')
st.info('📅 Análisis temporal: Muestra la línea de tiempo graduación→empleo (cohortes 2024-2028)')

# --- Filtros ---
with st.sidebar:
    st.markdown('<p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem">Filtros</p>', unsafe_allow_html=True)
    carreras = ['Todas'] + sorted(df['NombreCarrera'].dropna().unique().tolist())
    ciudades = ['Todas'] + sorted(df['Ciudad'].dropna().unique().tolist())

    carrera_sel = st.selectbox('Carrera', carreras)
    ciudad_sel  = st.selectbox('Ciudad',  ciudades)
    genero_sel  = st.selectbox('Género',  ['Todos', 'F', 'M'])
    
    # Temporal filter
    year_range = st.slider(
        'Rango de Años de Egreso',
        min_value=2020,
        max_value=2028,
        value=(2024, 2028),
        step=1,
        help='Filtra por cohorte de egreso estimada'
    )

df_f = df.copy()
if carrera_sel != 'Todas':
    df_f = df_f[df_f['NombreCarrera'] == carrera_sel]
if ciudad_sel != 'Todas':
    df_f = df_f[df_f['Ciudad'] == ciudad_sel]
if genero_sel != 'Todos':
    df_f = df_f[df_f['Genero'] == genero_sel]

# Temporal filtering (estimated graduation year)
# Nota: Si existe columna AñoEgreso, filtrar; si no, usar estimación desde SemestreActual
if 'AñoEgreso' in df_f.columns:
    df_f = df_f[
        (df_f['AñoEgreso'] >= year_range[0]) &
        (df_f['AñoEgreso'] <= year_range[1])
    ]
elif 'SemestreActual' in df_f.columns and 'anio_y' in df_f.columns:
    # Estimación: AñoEgreso ≈ anio_y + (SemestreActual / 6)
    df_f['AñoEgreso_Est'] = df_f['anio_y'] + (df_f['SemestreActual'] / 6).astype(int)
    df_f = df_f[
        (df_f['AñoEgreso_Est'] >= year_range[0]) &
        (df_f['AñoEgreso_Est'] <= year_range[1])
    ]

# --- Métricas del segmento ---
con_dato  = df_f.dropna(subset=['TieneEmpleoFormal'])
empleados = con_dato[con_dato['TieneEmpleoFormal'] == True]

tasa_seg    = round(con_dato['TieneEmpleoFormal'].mean() * 100, 1) if len(con_dato) else 0
salario_seg = round(empleados['SalarioMensualUSD'].mean(), 1)      if len(empleados) else 0
pct_area    = round(empleados['TrabajaEnAreaDeEstudio'].mean() * 100, 1) if len(empleados) else 0

# Sample size badge color
sample_size_color = 'green' if len(con_dato) > 1000 else ('orange' if len(con_dato) < 500 else 'blue')
st.markdown(f'<span style="color: {sample_size_color}; font-weight: 600;">📊 Muestra: {len(con_dato)} egresados</span>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
for col, icon, val, lbl in [
    (m1, 'ti-trending-up', f'{tasa_seg}%',    'Tasa de empleo'),
    (m2, 'ti-coin',        f'${salario_seg}',  'Salario promedio'),
    (m3, 'ti-check',       f'{pct_area}%',     'Empleados en su área'),
    (m4, 'ti-users',       str(len(con_dato)), 'Egresados en segmento'),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label"><i class="ti {icon}"></i>{lbl}</div>
      <div class="kpi-value">{val}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Gráficos fila 1 ---
col_l, col_r = st.columns(2)
with col_l:
    st.plotly_chart(bar_empleo_por_carrera(get_empleo_por_carrera()), use_container_width=True)
with col_r:
    df_ciudad = (
        con_dato.groupby('Ciudad')['EstudianteID']
        .count().reset_index()
        .rename(columns={'EstudianteID': 'total'})
        .sort_values('total', ascending=False)
    )
    st.plotly_chart(pie_distribucion_ciudad(df_ciudad), use_container_width=True)

# --- Gráfico fila 2 ---
st.plotly_chart(bar_salario_por_carrera(get_salario_por_carrera()), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- Evolución Temporal ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Evolución Temporal de la Inserción Laboral (Cohorte de Egreso)</p>', unsafe_allow_html=True)

df_temporal = get_empleo_temporal()

# Display errors from temporal analysis
if not df_temporal.empty and '_errors' in df_temporal.columns:
    errors_set = set()
    for error_list in df_temporal['_errors'].dropna():
        if isinstance(error_list, list):
            for err in error_list:
                errors_set.add(err)
    
    for error_msg in sorted(errors_set):
        if error_msg.startswith('❌'):
            st.error(error_msg)
        elif error_msg.startswith('⚠️'):
            st.warning(error_msg)
        else:
            st.info(error_msg)

if df_temporal.empty:
    st.info("Análisis temporal disponible solo con conexión a Gold.")
else:
    # Remove _errors column for charting
    chart_df = df_temporal.drop(columns=['_errors'], errors='ignore')
    st.plotly_chart(line_empleo_temporal(chart_df), use_container_width=True)
    st.caption("Año basado en cohorte de egreso estimada (SemestreActual + anio_y)")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

with st.expander('Ver tabla de datos del segmento'):
    cols = ['EstudianteID', 'Nombre', 'NombreCarrera', 'Ciudad', 'Genero',
            'TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio', 'SalarioMensualUSD']
    display_cols = [c for c in cols if c in df_f.columns]
    st.dataframe(df_f[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
