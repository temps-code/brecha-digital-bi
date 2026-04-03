"""
Dashboard — Page 3: Skill Gap
Responsable: Diego Vargas Urzagaste (@temps-code)

Compara las habilidades del currículo académico con
las habilidades TIC más demandadas en el mercado laboral.
Identifica brechas por categoría de competencia (básica, intermedia, avanzada).
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import get_habilidades_demandadas, get_skill_gap, load_vacantes, CARRERA_SKILLS
from components.charts import bar_habilidades_demandadas, combo_skill_gap

st.title('🎯 Brecha de Habilidades')
st.caption('Habilidades TIC demandadas por el mercado vs cobertura del sistema educativo')

# --- Insight principal ---
gap_df = get_skill_gap()
habs_sin_cobertura = gap_df[gap_df['cobertura'] == 0]
n_gap = len(habs_sin_cobertura)

if n_gap > 0:
    skills_faltantes = ', '.join(habs_sin_cobertura['habilidad'].tolist())
    st.error(
        f'**Brecha detectada:** {n_gap} habilidad(es) demandada(s) por el mercado '
        f'sin cobertura académica en ninguna carrera: **{skills_faltantes}**'
    )

st.divider()

# --- Gráfico combo ---
st.plotly_chart(combo_skill_gap(gap_df), use_container_width=True)

st.divider()

col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader('Habilidades más demandadas')
    dem_df = get_habilidades_demandadas()
    st.plotly_chart(bar_habilidades_demandadas(dem_df), use_container_width=True)

with col_der:
    st.subheader('Cobertura académica por carrera')
    for carrera, skills in CARRERA_SKILLS.items():
        with st.expander(carrera):
            if skills:
                for s in skills:
                    st.markdown(f'- ✅ {s}')
            else:
                st.markdown('_Sin habilidades TIC mapeadas_')

st.divider()

st.subheader('Vacantes del Mercado')
vac = load_vacantes()
st.dataframe(
    vac[['title', 'location', 'salary_min', 'description']].rename(columns={
        'title': 'Título',
        'location': 'Ciudad',
        'salary_min': 'Salario Mín. (USD)',
        'description': 'Habilidades Requeridas',
    }),
    use_container_width=True,
)

st.divider()

st.subheader('Tabla de Brecha Detallada')
st.dataframe(
    gap_df.rename(columns={
        'habilidad': 'Habilidad',
        'demanda': 'Vacantes que la requieren',
        'cobertura': 'Cobertura Académica (%)',
    }),
    use_container_width=True,
)
