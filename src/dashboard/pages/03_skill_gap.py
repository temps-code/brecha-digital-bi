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

from components.data_loader import get_habilidades_demandadas, get_skill_gap, load_vacantes, load_habilidades_academicas
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
    st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.75rem">Currículo Digital por Nivel</p>', unsafe_allow_html=True)
    habilidades_academicas = load_habilidades_academicas()
    if not habilidades_academicas:
        st.info("Sin datos de currículo disponibles.")
    else:
        nivel_icons = {'Básico': 'ti-circle-1', 'Intermedio': 'ti-circle-2', 'Avanzado': 'ti-circle-3'}
        for nivel, habilidades in habilidades_academicas.items():
            icon = nivel_icons.get(nivel, 'ti-circle')
            tags = ''.join(
                f'<span class="skill-tag"><i class="ti ti-check"></i>{h}</span>'
                for h in habilidades
            ) if habilidades else '<span class="skill-tag" style="color:#71717A">Sin habilidades mapeadas</span>'
            st.markdown(f"""
            <div class="skill-card">
              <div class="skill-name"><i class="ti {icon}"></i> {nivel}</div>
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
    rename_cols = {
        'habilidad': 'Habilidad',
        'demanda':   'Vacantes que la requieren',
        'cobertura': 'Cobertura Académica (%)',
    }
    if 'nivel' in gap_df.columns:
        rename_cols['nivel'] = 'Nivel'
    st.dataframe(
        gap_df.rename(columns=rename_cols),
        use_container_width=True, hide_index=True,
    )
