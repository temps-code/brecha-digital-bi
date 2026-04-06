"""
Dashboard — Componentes
Responsable: Diego Vargas Urzagaste (@temps-code)

Componentes reutilizables del dashboard:
  - data_loader: Funciones para cargar datos desde la base de datos y CSVs
  - charts: Funciones para crear visualizaciones con Plotly
  - styles: Estilos CSS y Tabler Icons
"""
from .data_loader import get_kpis, get_cepal_bolivia, get_tasa_desercion
from .charts import line_cepal_bolivia, bar_tasa_desercion
from .styles import inject_styles

__all__ = [
    'get_kpis',
    'get_cepal_bolivia',
    'get_tasa_desercion',
    'line_cepal_bolivia',
    'bar_tasa_desercion',
    'inject_styles',
]
