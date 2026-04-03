"""
Dashboard — Entry Point
Responsable: Diego Vargas Urzagaste (@temps-code)

Aplicación principal de Streamlit. Configura la navegación entre páginas:
  - 01_kpis.py        → Indicadores generales
  - 02_insercion.py   → Tasa de inserción laboral
  - 03_skill_gap.py   → Brecha de habilidades
  - 04_chatbot.py     → Asistente IA (Gemini API)
"""
import streamlit as st
from components.data_loader import get_kpis

st.set_page_config(
    page_title='Brecha Digital BI',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.title('📊 Brecha Digital Laboral — Educación Técnica Superior')
st.caption('UPDS Bolivia · Proyecto de Business Intelligence · 2026')

st.divider()

kpis = get_kpis()

col1, col2, col3, col4 = st.columns(4)
col1.metric('Tasa de Empleo Formal', f"{kpis['tasa_empleo']}%")
col2.metric('Empleados en su Área', f"{kpis['pct_area']}%")
col3.metric('Salario Promedio', f"${kpis['salario_prom']} USD")
col4.metric('Total Egresados', kpis['total_egresados'])

st.divider()

st.markdown("""
### Navegación

Usá el menú lateral para explorar cada sección del análisis:

| Página | Contenido |
|--------|-----------|
| **KPIs Generales** | Indicadores clave + benchmark CEPALSTAT (ODS 4.4.1) |
| **Inserción Laboral** | Tasa de empleo por carrera, ciudad y salario |
| **Brecha de Habilidades** | Demanda del mercado vs cobertura académica |
| **Asistente BI** | Chatbot con Gemini para consultas en lenguaje natural |

---

**Fuentes de datos:**
- Base de datos institucional UPDS (Bronze → Silver → Gold)
- CEPALSTAT — Indicador 4.4.1 (Competencias TIC en jóvenes)
- Adzuna API — Vacantes tecnológicas activas en Bolivia
""")
