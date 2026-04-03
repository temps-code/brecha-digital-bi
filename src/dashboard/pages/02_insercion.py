"""
Dashboard — Page 2: Inserción Laboral
Responsable: Diego Vargas Urzagaste (@temps-code)

Visualiza la tasa de inserción laboral de egresados:
  - Por carrera
  - Por región/departamento de Bolivia
  - Evolución temporal
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import load_df, get_empleo_por_carrera, get_salario_por_carrera
from components.charts import bar_empleo_por_carrera, pie_distribucion_ciudad, bar_salario_por_carrera

st.set_page_config(page_title='Inserción Laboral — Brecha Digital BI', page_icon='💼', layout='wide')

st.markdown("""
<style>
  .page-header h2 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
  .page-header p  { color: #9CA3AF; font-size: 0.9rem; margin: 0; }
  .metric-mini { background: #1E2130; border-radius: 10px; padding: 0.9rem 1.1rem;
                 border: 1px solid #2A2D3E; text-align: center; }
  .metric-mini .val { font-size: 1.6rem; font-weight: 700; color: #F9FAFB; }
  .metric-mini .lbl { font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;
                      letter-spacing: 0.07em; margin-top: 0.1rem; }
  hr.thin { border: none; border-top: 1px solid #2A2D3E; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h2>💼 Inserción Laboral</h2>
  <p>Análisis de empleo por carrera, ciudad y nivel salarial</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

df = load_df()

# --- Filtros ---
with st.sidebar:
    st.markdown('### Filtros')
    carreras = ['Todas'] + sorted(df['NombreCarrera'].dropna().unique().tolist())
    ciudades = ['Todas'] + sorted(df['Ciudad'].dropna().unique().tolist())

    carrera_sel = st.selectbox('Carrera', carreras)
    ciudad_sel  = st.selectbox('Ciudad',  ciudades)
    genero_sel  = st.selectbox('Género',  ['Todos', 'F', 'M'])

df_f = df.copy()
if carrera_sel != 'Todas':
    df_f = df_f[df_f['NombreCarrera'] == carrera_sel]
if ciudad_sel != 'Todas':
    df_f = df_f[df_f['Ciudad'] == ciudad_sel]
if genero_sel != 'Todos':
    df_f = df_f[df_f['Genero'] == genero_sel]

# --- Métricas del segmento ---
con_dato  = df_f.dropna(subset=['TieneEmpleoFormal'])
empleados = con_dato[con_dato['TieneEmpleoFormal'] == True]

tasa_seg    = round(con_dato['TieneEmpleoFormal'].mean() * 100, 1) if len(con_dato) else 0
salario_seg = round(empleados['SalarioMensualUSD'].mean(), 1)      if len(empleados) else 0
pct_area    = round(empleados['TrabajaEnAreaDeEstudio'].mean() * 100, 1) if len(empleados) else 0

m1, m2, m3, m4 = st.columns(4)
for col, val, lbl in [
    (m1, f'{tasa_seg}%',       'Tasa de empleo'),
    (m2, f'${salario_seg}',    'Salario promedio'),
    (m3, f'{pct_area}%',       'Empleados en su área'),
    (m4, str(len(con_dato)),   'Egresados en segmento'),
]:
    col.markdown(f"""
    <div class="metric-mini">
      <div class="val">{val}</div>
      <div class="lbl">{lbl}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

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

st.markdown('<hr class="thin">', unsafe_allow_html=True)

with st.expander('Ver tabla de datos del segmento'):
    cols = ['EstudianteID', 'Nombre', 'NombreCarrera', 'Ciudad', 'Genero',
            'TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio', 'SalarioMensualUSD']
    st.dataframe(df_f[cols].reset_index(drop=True), use_container_width=True, hide_index=True)
