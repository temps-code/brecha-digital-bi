"""
Dashboard — Page 3: Skill Gap
Responsable: Diego Vargas Urzagaste (@temps-code)

Compara las habilidades del currículo académico con
las habilidades TIC más demandadas en el mercado laboral.
Identifica brechas por categoría de competencia (básica, intermedia, avanzada).
"""
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import (
    get_habilidades_demandadas, get_skill_gap, load_vacantes, load_habilidades_academicas,
    get_skill_gap_filtered, get_habilidades_demandadas_filtered, load_df, get_kpis
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

habilidades_academicas_full = load_habilidades_academicas()
df_context = load_df()

# --- Filtros Interactivos ---
with st.sidebar:
    st.markdown('<p style="font-size:0.75rem;font-weight:600;color:#A1A1AA;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem">Filtros</p>', unsafe_allow_html=True)
    
    carreras = ['Todas'] + sorted(list(habilidades_academicas_full.keys()))
    ciudades = ['Todas'] + sorted(df_context['Ciudad'].dropna().unique().tolist())
    
    carrera_sel = st.selectbox('Carrera', carreras)
    ciudad_sel  = st.selectbox('Sede (Ciudad)', ciudades)

    # Demand range filter
    demand_range = st.slider(
        'Rango de Demanda (vacantes)',
        min_value=0,
        max_value=500,
        value=(0, 500),
        step=10,
        help='Filtra habilidades por número de vacantes'
    )
    
    # Coverage filter
    min_coverage = st.slider(
        'Cobertura Académica Mínima (%)',
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help='Muestra solo habilidades con cobertura >= al valor seleccionado'
    )

# Filtrar diccionario de habilidades académicas (Phase 2.5)
hab_academicas_f = habilidades_academicas_full.copy()
if carrera_sel != 'Todas':
    hab_academicas_f = {carrera_sel: habilidades_academicas_full.get(carrera_sel, [])}

gap_df = get_skill_gap(hab_academicas=hab_academicas_f, ciudad_filter=ciudad_sel)

# Aplicar filtros interactivos de vacantes/cobertura
if not gap_df.empty:
    gap_df = gap_df[
        (gap_df['demanda'] >= demand_range[0]) &
        (gap_df['demanda'] <= demand_range[1]) &
        (gap_df['cobertura_%'] >= min_coverage)
    ]

# KPI cards — derivadas del gap_df ya filtrado
cobertura_promedio = round(gap_df['cobertura_%'].mean(), 1) if not gap_df.empty else 0
brecha_critica_count = int((gap_df['cobertura_%'] < 20).sum()) if not gap_df.empty else 0
cero_cobertura = gap_df[gap_df['cobertura_%'] == 0].sort_values('demanda', ascending=False) if not gap_df.empty else None
top_faltante = cero_cobertura['habilidad'].iloc[0] if cero_cobertura is not None and not cero_cobertura.empty else 'N/D'

kc1, kc2, kc3 = st.columns(3)
for col, icon, label, val in [
    (kc1, 'ti-percentage',      'Cobertura Promedio',   f'{cobertura_promedio}%'),
    (kc2, 'ti-alert-triangle',  'Brechas Críticas (<20%)', str(brecha_critica_count)),
    (kc3, 'ti-list',            'Top Skill Faltante',   top_faltante),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label"><i class="ti {icon}"></i>{label}</div>
      <div class="kpi-value">{val}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="margin-top:0.75rem"></div>', unsafe_allow_html=True)

salary_coverage = get_kpis(df_context).get('salary_coverage_pct', 0)
students_analyzed = gap_df['demanda'].sum() if not gap_df.empty else 0

card_col1, card_col2 = st.columns(2)
with card_col1:
    if salary_coverage < 70:
        st.markdown(f"""
        <div class="kpi-card" style="border-left:3px solid #F59E0B">
          <div class="kpi-label"><i class="ti ti-alert-triangle"></i>Cobertura de datos de salarios</div>
          <div class="kpi-value">{salary_coverage:.1f}%</div>
          <div style="font-size:0.75rem;color:#A1A1AA">Datos limitados para correlación salario-habilidad</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="kpi-card" style="border-left:3px solid #22C55E">
          <div class="kpi-label"><i class="ti ti-circle-check"></i>Cobertura de datos de salarios</div>
          <div class="kpi-value">{salary_coverage:.1f}%</div>
          <div style="font-size:0.75rem;color:#A1A1AA">{students_analyzed} vacantes analizadas</div>
        </div>
        """, unsafe_allow_html=True)
with card_col2:
    st.markdown("""
    <div class="kpi-card" style="border-left:3px solid #6366F1">
      <div class="kpi-label"><i class="ti ti-bulb"></i>Nota técnica</div>
      <div style="font-size:0.8125rem;color:#D4D4D8">Usa <b>fuzzy matching</b> (umbral 0.80) para detectar habilidades con similitud semántica realista</div>
    </div>
    """, unsafe_allow_html=True)

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
    
    with st.expander(f"{total_low_coverage} habilidades con baja cobertura académica (menos del 20%)", expanded=False):
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

gap_filtered, gap_other_count = get_skill_gap_filtered(hab_academicas=hab_academicas_f, top_n=15, ciudad_filter=ciudad_sel)

if not gap_filtered.empty:
    chart_df = gap_filtered.drop(columns=['_errors'], errors='ignore')
    st.plotly_chart(combo_skill_gap(chart_df), use_container_width=True)
    st.caption('Las barras muestran cuántas ofertas de trabajo en Bolivia piden cada habilidad. La zona naranja indica cuántas de esas vacantes ya están cubiertas por lo que se enseña en las universidades. Si la zona naranja llega a la misma altura que la barra, significa que esa habilidad está bien cubierta por los planes de estudio.')

    if gap_other_count > 0:
        st.info(f"+ {gap_other_count} habilidades adicionales disponibles en la tabla detallada, ordenadas por demanda.")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# MOST DEMANDED SKILLS
hab_filtered, hab_other_count = get_habilidades_demandadas_filtered(top_n=10, ciudad_filter=ciudad_sel)

st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Top 10 Habilidades Más Demandadas</p>', unsafe_allow_html=True)

if not hab_filtered.empty:
    st.plotly_chart(bar_habilidades_demandadas(hab_filtered), use_container_width=True)
    st.caption('Las habilidades tecnológicas más pedidas por las empresas en Bolivia, según las ofertas de trabajo analizadas. Datos obtenidos de la plataforma Adzuna usando inteligencia artificial para identificar las competencias mencionadas en cada aviso.')

    if hab_other_count > 0:
        with st.expander(f"Ver {hab_other_count} habilidades adicionales"):
            hab_full = get_habilidades_demandadas(ciudad_filter=ciudad_sel)
            hab_rest = hab_full.iloc[10:].copy()
            st.dataframe(
                hab_rest.rename(columns={'habilidad': 'Habilidad', 'demanda': 'Demanda'}),
                use_container_width=True, hide_index=True,
            )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# --- HABILIDADES POR CARRERA ---
st.markdown('<p style="font-size:0.9375rem;font-weight:600;color:#FAFAFA;margin-bottom:0.25rem">Habilidades Académicas por Carrera</p>', unsafe_allow_html=True)
st.caption('Tocá cada carrera para ver todas las materias y competencias técnicas que se enseñan en los planes de estudio. Basado en los currículos oficiales de universidades bolivianas (UMSA, UPB, UCB, UTEPSA, UTB).')

_hab_tabs = load_habilidades_academicas()
if _hab_tabs:
    _tab_labels = list(_hab_tabs.keys())
    _tabs = st.tabs(_tab_labels)
    for _tab, _carrera in zip(_tabs, _tab_labels):
        with _tab:
            _skills = sorted(_hab_tabs[_carrera])
            st.caption(f'Esta carrera incluye {len(_skills)} habilidades técnicas en su plan de estudios.')
            st.dataframe(
                pd.DataFrame({'Habilidad': _skills}),
                use_container_width=True,
                hide_index=True,
            )

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
    skills_path = Path(__file__).resolve().parents[3] / 'data' / 'processed' / 'empleos' / 'skills_extracted.csv'
    try:
        skills_df = pd.read_csv(skills_path)
        def _parse_skills(raw):
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else []
                return ', '.join(parsed) if parsed else '—'
            except Exception:
                return '—'
        skills_df['skills_str'] = skills_df['skills_json'].apply(_parse_skills)
        vac = vac.merge(
            skills_df[['job_id', 'skills_str']],
            left_on='id', right_on='job_id',
            how='left',
        ).drop(columns=['job_id'], errors='ignore')
        vac['skills_str'] = vac['skills_str'].fillna('—')
        display_cols = {
            'title': 'Título', 'location': 'Ciudad',
            'salary_min': 'Salario Mín. (USD)',
            'skills_str': 'Skills Extraídas (LLM)',
            'description': 'Descripción',
        }
    except Exception:
        display_cols = {
            'title': 'Título', 'location': 'Ciudad',
            'salary_min': 'Salario Mín. (USD)', 'description': 'Descripción',
        }
    st.dataframe(
        vac[[c for c in display_cols if c in vac.columns]].rename(columns=display_cols),
        use_container_width=True, hide_index=True,
    )
