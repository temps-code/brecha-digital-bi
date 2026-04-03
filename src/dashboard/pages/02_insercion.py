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

from components.data_loader import load_df, get_empleo_por_carrera, get_distribucion_ciudad, get_salario_por_carrera
from components.charts import bar_empleo_por_carrera, pie_distribucion_ciudad, bar_salario_por_carrera

st.title('💼 Inserción Laboral')
st.caption('Análisis de empleo por carrera, ciudad y nivel salarial')

df = load_df()

# --- Filtros en sidebar ---
with st.sidebar:
    st.header('Filtros')
    carreras_disponibles = ['Todas'] + sorted(df['NombreCarrera'].dropna().unique().tolist())
    carrera_sel = st.selectbox('Carrera', carreras_disponibles)

    ciudades_disponibles = ['Todas'] + sorted(df['Ciudad'].dropna().unique().tolist())
    ciudad_sel = st.selectbox('Ciudad', ciudades_disponibles)

    generos_disponibles = ['Todos', 'F', 'M']
    genero_sel = st.selectbox('Género', generos_disponibles)

# --- Aplicar filtros ---
df_filtrado = df.copy()
if carrera_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['NombreCarrera'] == carrera_sel]
if ciudad_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Ciudad'] == ciudad_sel]
if genero_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Genero'] == genero_sel]

# --- Métricas del segmento filtrado ---
con_dato = df_filtrado.dropna(subset=['TieneEmpleoFormal'])
if len(con_dato) > 0:
    tasa = round(con_dato['TieneEmpleoFormal'].mean() * 100, 1)
    empleados_seg = con_dato[con_dato['TieneEmpleoFormal'] == True]
    salario_seg = round(empleados_seg['SalarioMensualUSD'].mean(), 1) if len(empleados_seg) > 0 else 0
    pct_area_seg = round(empleados_seg['TrabajaEnAreaDeEstudio'].mean() * 100, 1) if len(empleados_seg) > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric('Tasa de empleo (segmento)', f'{tasa}%')
    c2.metric('Salario promedio (segmento)', f'${salario_seg} USD')
    c3.metric('Empleados en su área (segmento)', f'{pct_area_seg}%')
else:
    st.warning('Sin datos para los filtros seleccionados.')

st.divider()

# --- Gráficos ---
col_izq, col_der = st.columns(2)

with col_izq:
    df_carrera = get_empleo_por_carrera()
    st.plotly_chart(bar_empleo_por_carrera(df_carrera), use_container_width=True)

with col_der:
    df_ciudad = (
        df_filtrado.dropna(subset=['TieneEmpleoFormal'])
        .groupby('Ciudad')['EstudianteID']
        .count()
        .reset_index()
        .rename(columns={'EstudianteID': 'total'})
        .sort_values('total', ascending=False)
    )
    st.plotly_chart(pie_distribucion_ciudad(df_ciudad), use_container_width=True)

df_salario = get_salario_por_carrera()
st.plotly_chart(bar_salario_por_carrera(df_salario), use_container_width=True)

st.divider()

with st.expander('Ver tabla de datos'):
    cols_mostrar = ['EstudianteID', 'Nombre', 'NombreCarrera', 'Ciudad', 'Genero',
                    'TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio', 'SalarioMensualUSD']
    st.dataframe(df_filtrado[cols_mostrar].reset_index(drop=True), use_container_width=True)
