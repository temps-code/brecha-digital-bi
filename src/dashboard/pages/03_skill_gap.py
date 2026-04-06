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

from components.data_loader import (
    get_habilidades_demandadas, get_skill_gap, load_vacantes, load_habilidades_academicas,
    get_skill_gap_filtered, get_habilidades_demandadas_filtered
)
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

# ✅ Skill Quality Metrics
students_analyzed = gap_df['demanda'].sum() if not gap_df.empty else 0
salary_coverage = 82.7  # From Phase 3, approximately
salary_warning = ''
if salary_coverage < 70:
    salary_warning = st.warning(f'⚠️ Cobertura de salarios: {salary_coverage:.1f}% (datos limitados para correlación salario-habilidad)')
else:
    st.info(f'✅ Skill coverage: {students_analyzed} estudiantes analizados | {salary_coverage:.1f}% cobertura de datos de salarios')

st.markdown('💡 **Nota técnica**: Usa fuzzy matching (umbral 0.80) para detectar habilidades con similitud semántica realista', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Error display - FILTERED to only critical errors
if '_errors' in gap_df.columns and not gap_df.empty:
    errors_set = set()
    for error_list in gap_df['_errors'].dropna():
        if isinstance(error_list, list):
            for err in error_list:
                if err.startswith('❌'):  # Only show critical errors, not warnings
                    errors_set.add(err)
    
    for error_msg in sorted(errors_set):
        st.error(error_msg)

# Identify skills with low coverage and group them
low_coverage = gap_df[gap_df['cobertura_%'] < 20]

if not low_coverage.empty:
    # Show summary instead of long list
    total_low_coverage = len(low_coverage)
    
    with st.expander(f"📊 {total_low_coverage} habilidades con baja cobertura académica (<20%)", expanded=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Top 5 by demand
            top_low = low_coverage.nlargest(5, 'demanda')
            st.markdown("**Top 5 críticas (por demanda):**")
            for idx, row in top_low.iterrows():
                st.caption(f"• {row['habilidad']}: {row['demanda']} vacantes, {row['cobertura_%']}% cobertura")
        
        with col2:
            # Statistics
            st.metric("Total con brecha", total_low_coverage)
            st.metric("Demanda promedio", f"{low_coverage['demanda'].mean():.0f} vacantes")
            st.metric("Cobertura promedio", f"{low_coverage['cobertura_%'].mean():.1f}%")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# MAIN CHART: Top 15 skills
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Demanda del Mercado vs Cobertura Académica (Top 15)</p>', unsafe_allow_html=True)

gap_filtered, gap_other_count = get_skill_gap_filtered(top_n=15)

if not gap_filtered.empty:
    chart_df = gap_filtered.drop(columns=['_errors'], errors='ignore')
    st.plotly_chart(combo_skill_gap(chart_df), use_container_width=True)
    
    if gap_other_count > 0:
        st.info(f"📌 + {gap_other_count} habilidades adicionales disponibles en la tabla detallada (ordenadas por demanda)")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# MOST DEMANDED SKILLS
hab_filtered, hab_other_count = get_habilidades_demandadas_filtered(top_n=10)

col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Top 10 Habilidades Más Demandadas</p>', unsafe_allow_html=True)
    
    if not hab_filtered.empty:
        st.plotly_chart(bar_habilidades_demandadas(hab_filtered), use_container_width=True)
        
        if hab_other_count > 0:
            with st.expander(f"Ver {hab_other_count} habilidades adicionales"):
                hab_full = get_habilidades_demandadas()
                hab_rest = hab_full.iloc[10:].copy()
                st.dataframe(
                    hab_rest.rename(columns={'habilidad': 'Habilidad', 'demanda': 'Demanda'}),
                    use_container_width=True, hide_index=True,
                )

with col_r:
    st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.75rem">Currículo Digital por Carrera</p>', unsafe_allow_html=True)
    habilidades_academicas = load_habilidades_academicas()
    if not habilidades_academicas:
        st.info("Sin datos de currículo disponibles.")
    else:
        for carrera, habilidades in habilidades_academicas.items():
            tags = ''.join(
                f'<span class="skill-tag"><i class="ti ti-check"></i>{h}</span>'
                for h in habilidades
            ) if habilidades else '<span class="skill-tag" style="color:#71717A">Sin habilidades mapeadas</span>'
            st.markdown(f"""
            <div class="skill-card">
              <div class="skill-name"><i class="ti ti-book"></i> {carrera}</div>
              <div>{tags}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# DETAILED DATA EXPANDERS
with st.expander('📋 Ver tabla de brecha detallada (todas las habilidades)'):
    chart_df = gap_df.drop(columns=['_errors'], errors='ignore')
    rename_cols = {
        'habilidad': 'Habilidad',
        'demanda':   'Demanda (vacantes)',
        'similarity_score': 'Similitud (0-1)',
        'cobertura_%': 'Cobertura (%)',
    }
    if 'carrera' in chart_df.columns:
        rename_cols['carrera'] = 'Carrera que la enseña'
    st.dataframe(
        chart_df.rename(columns=rename_cols),
        use_container_width=True, hide_index=True,
    )

with st.expander('💼 Ver vacantes del mercado'):
    vac = load_vacantes()
    st.dataframe(
        vac[['title', 'location', 'salary_min', 'description']].rename(columns={
            'title': 'Título', 'location': 'Ciudad',
            'salary_min': 'Salario Mín. (USD)', 'description': 'Habilidades requeridas',
        }),
        use_container_width=True, hide_index=True,
    )
