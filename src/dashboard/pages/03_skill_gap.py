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

st.set_page_config(page_title='Brecha de Habilidades — Brecha Digital BI', page_icon='🎯', layout='wide')

st.markdown("""
<style>
  .page-header h2 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
  .page-header p  { color: #9CA3AF; font-size: 0.9rem; margin: 0; }
  .alert-card { background: #2D1B1B; border-left: 4px solid #EF4444; border-radius: 8px;
                padding: 0.9rem 1.1rem; margin-bottom: 0.5rem; }
  .alert-card .title { font-weight: 600; color: #FCA5A5; font-size: 0.92rem; }
  .alert-card .body  { color: #D1D5DB; font-size: 0.85rem; margin-top: 0.2rem; }
  .skill-card { background: #1E2130; border-radius: 10px; padding: 0.8rem 1rem;
                border: 1px solid #2A2D3E; margin-bottom: 0.4rem; }
  .skill-item { font-size: 0.85rem; color: #D1D5DB; padding: 2px 0; }
  hr.thin { border: none; border-top: 1px solid #2A2D3E; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h2>🎯 Brecha de Habilidades</h2>
  <p>Habilidades TIC demandadas por el mercado vs cobertura del sistema educativo</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

gap_df = get_skill_gap()
sin_cobertura = gap_df[gap_df['cobertura'] == 0]

if not sin_cobertura.empty:
    skills_str = ' · '.join(sin_cobertura['habilidad'].tolist())
    st.markdown(f"""
    <div class="alert-card">
      <div class="title">⚠️ Brecha detectada — {len(sin_cobertura)} habilidades sin cobertura académica</div>
      <div class="body">{skills_str}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Combo chart ---
st.plotly_chart(combo_skill_gap(gap_df), use_container_width=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown('#### Habilidades más demandadas')
    st.plotly_chart(bar_habilidades_demandadas(get_habilidades_demandadas()), use_container_width=True)

with col_r:
    st.markdown('#### Cobertura por carrera')
    for carrera, skills in CARRERA_SKILLS.items():
        st.markdown(f"""
        <div class="skill-card">
          <div style="font-weight:600;font-size:0.88rem;color:#F9FAFB;margin-bottom:0.3rem">{carrera}</div>
          {''.join(f'<div class="skill-item">✅ {s}</div>' for s in skills) if skills
           else '<div class="skill-item" style="color:#6B7280">Sin habilidades TIC mapeadas</div>'}
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

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
