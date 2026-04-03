"""
Dashboard — Page 3: Skill Gap
Responsable: Diego Vargas Urzagaste (@temps-code)

Compara las habilidades del currículo académico con
las habilidades TIC más demandadas en el mercado laboral.
Identifica brechas por categoría de competencia (básica, intermedia, avanzada).
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import get_habilidades_demandadas, get_skill_gap, load_vacantes, CARRERA_SKILLS
from components.charts import bar_habilidades_demandadas, combo_skill_gap
from components.styles import inject_styles

st.set_page_config(page_title='Brecha de Habilidades — Brecha Digital BI', page_icon=':material/target:', layout='wide')

inject_styles()

st.markdown("""
<div class="page-header">
  <h2><i class="ti ti-target"></i> Brecha de Habilidades</h2>
  <p>Habilidades TIC demandadas por el mercado vs cobertura del sistema educativo</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

gap_df = get_skill_gap()
sin_cobertura = gap_df[gap_df['cobertura'] == 0]

if not sin_cobertura.empty:
    skills_str = ' &nbsp;·&nbsp; '.join(sin_cobertura['habilidad'].tolist())
    st.markdown(f"""
    <div class="alert-card">
      <div class="alert-title">
        <i class="ti ti-alert-triangle"></i>
        Brecha detectada — {len(sin_cobertura)} habilidades sin cobertura académica
      </div>
      <div class="alert-body">{skills_str}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Combo chart ---
st.plotly_chart(combo_skill_gap(gap_df), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Habilidades más demandadas</p>', unsafe_allow_html=True)
    st.plotly_chart(bar_habilidades_demandadas(get_habilidades_demandadas()), use_container_width=True)

with col_r:
    st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.75rem">Cobertura por carrera</p>', unsafe_allow_html=True)
    for carrera, skills in CARRERA_SKILLS.items():
        tags = ''.join(
            f'<span class="skill-tag"><i class="ti ti-check"></i>{s}</span>'
            for s in skills
        ) if skills else '<span class="skill-tag" style="color:#71717A">Sin habilidades TIC mapeadas</span>'
        st.markdown(f"""
        <div class="skill-card">
          <div class="skill-name">{carrera}</div>
          <div>{tags}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

with st.expander('Ver vacantes del mercado'):
    vac = load_vacantes()
    st.dataframe(
        vac[['title', 'location', 'salary_min', 'description']].rename(columns={
            'title': 'Título', 'location': 'Ciudad',
            'salary_min': 'Salario Mín. (USD)', 'description': 'Habilidades requeridas',
        }),
        use_container_width=True, hide_index=True,
    )

with st.expander('Ver tabla de brecha detallada'):
    st.dataframe(
        gap_df.rename(columns={
            'habilidad': 'Habilidad',
            'demanda':   'Vacantes que la requieren',
            'cobertura': 'Cobertura Académica (%)',
        }),
        use_container_width=True, hide_index=True,
    )
