"""
Dashboard — Reusable Chart Components
Responsable: Diego Vargas Urzagaste (@temps-code)

Funciones reutilizables de Plotly para el dashboard.
Cada función recibe un DataFrame y retorna una figura de Plotly.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

_BG = 'rgba(0,0,0,0)'
_BLUE = '#2196F3'
_ORANGE = '#FF9800'
_GRID = '#2A2D3E'


def _base_layout(fig: go.Figure, title: str = '') -> go.Figure:
    fig.update_layout(
        title=title,
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font_color='#FAFAFA',
        margin=dict(l=10, r=10, t=45, b=10),
        xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID),
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID),
    )
    return fig


def bar_empleo_por_carrera(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df,
        x='tasa_empleo',
        y='NombreCarrera',
        orientation='h',
        color='tasa_empleo',
        color_continuous_scale='Blues',
        text='tasa_empleo',
        labels={'tasa_empleo': 'Tasa de Empleo (%)', 'NombreCarrera': ''},
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_coloraxes(showscale=False)
    return _base_layout(fig, 'Tasa de Empleo por Carrera')


def pie_distribucion_ciudad(df: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        df,
        names='Ciudad',
        values='total',
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return _base_layout(fig, 'Distribución de Egresados por Ciudad')


def bar_salario_por_carrera(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df,
        x='salario_promedio',
        y='NombreCarrera',
        orientation='h',
        color='salario_promedio',
        color_continuous_scale='Greens',
        text='salario_promedio',
        labels={'salario_promedio': 'Salario Promedio (USD)', 'NombreCarrera': ''},
    )
    fig.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    fig.update_coloraxes(showscale=False)
    return _base_layout(fig, 'Salario Promedio por Carrera')


def bar_habilidades_demandadas(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df,
        x='demanda',
        y='habilidad',
        orientation='h',
        color='demanda',
        color_continuous_scale='Blues',
        text='demanda',
        labels={'demanda': 'Vacantes que la requieren', 'habilidad': ''},
    )
    fig.update_traces(textposition='outside')
    fig.update_coloraxes(showscale=False)
    return _base_layout(fig, 'Habilidades más Demandadas en el Mercado')


def combo_skill_gap(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Demanda (vacantes)',
        x=df['habilidad'],
        y=df['demanda'],
        marker_color=_BLUE,
        yaxis='y',
    ))
    fig.add_trace(go.Scatter(
        name='Cobertura académica (%)',
        x=df['habilidad'],
        y=df['cobertura'],
        mode='lines+markers',
        marker=dict(color=_ORANGE, size=8),
        line=dict(color=_ORANGE, width=2),
        yaxis='y2',
    ))
    fig.update_layout(
        title='Brecha: Demanda del Mercado vs Cobertura Académica',
        yaxis=dict(title='Vacantes que la requieren', gridcolor=_GRID, zerolinecolor=_GRID),
        yaxis2=dict(
            title='Cobertura académica (%)',
            overlaying='y',
            side='right',
            range=[0, 120],
            gridcolor=_GRID,
        ),
        legend=dict(orientation='h', y=1.12),
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font_color='#FAFAFA',
        margin=dict(l=10, r=10, t=70, b=10),
    )
    return fig


def line_cepal_bolivia(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df,
        x='anio',
        y='value',
        markers=True,
        labels={'anio': 'Año', 'value': 'Indicador TIC (%)'},
        color_discrete_sequence=[_BLUE],
    )
    fig.update_traces(line_width=2, marker_size=7)
    return _base_layout(fig, 'Indicador TIC Bolivia — CEPALSTAT (ODS 4.4.1)')
