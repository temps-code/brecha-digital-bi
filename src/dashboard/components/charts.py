"""
Dashboard — Reusable Chart Components
Responsable: Diego Vargas Urzagaste (@temps-code)

Funciones reutilizables de Plotly para el dashboard.
Cada función recibe un DataFrame y retorna una figura de Plotly.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

_BG     = 'rgba(0,0,0,0)'
_ACCENT = '#c0c1ff'   # primary — Digital Cartographer
_ORANGE = '#ffb783'   # tertiary — warm contrast
_GRID   = '#353437'   # outline-variant


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
        range_x=[0, 100],
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
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
    max_sal = df['salario_promedio'].max() if not df.empty else 2000
    fig = px.bar(
        df,
        x='salario_promedio',
        y='NombreCarrera',
        orientation='h',
        color='salario_promedio',
        color_continuous_scale='Greens',
        text='salario_promedio',
        labels={'salario_promedio': 'Salario Promedio (USD)', 'NombreCarrera': ''},
        range_x=[0, max_sal * 1.25],
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
    # Scale coverage to the same unit as demand: if a skill has 40 vacantes and
    # 100% coverage, the line sits at 40. 50% → 20. Both axes share the same scale.
    cobertura_scaled = (df['demanda'] * df['cobertura'] / 100).round(1)
    n = len(df)
    x_indices = list(range(n))
    skill_labels = df['habilidad'].tolist()

    fig = go.Figure()

    # Bars: market demand
    fig.add_trace(go.Bar(
        name='Vacantes que la requieren',
        x=x_indices,
        y=df['demanda'],
        marker_color=_ACCENT,
    ))

    # Area line: coverage scaled to vacantes units.
    # Prepend and append a 0 point so the line visually starts and ends at the baseline.
    fig.add_trace(go.Scatter(
        name='Cobertura académica (vacantes equiv.)',
        x=[-0.5] + x_indices + [n - 0.5],
        y=[0] + cobertura_scaled.tolist() + [0],
        mode='lines',
        line=dict(color=_ORANGE, width=2),
        fill='tozeroy',
        fillcolor='rgba(245,158,11,0.18)',
    ))

    # Markers only at actual data points (separate trace, no legend entry)
    fig.add_trace(go.Scatter(
        x=x_indices,
        y=cobertura_scaled,
        mode='markers',
        marker=dict(color=_ORANGE, size=7),
        showlegend=False,
        hovertemplate='%{y:.1f} vacantes equiv.<extra></extra>',
    ))

    fig.update_layout(
        title='Brecha: Demanda del Mercado vs Cobertura Académica',
        xaxis=dict(
            tickvals=x_indices,
            ticktext=skill_labels,
            tickangle=-35,
            gridcolor=_GRID,
            zerolinecolor=_GRID,
        ),
        yaxis=dict(title='Cantidad de vacantes', gridcolor=_GRID, zerolinecolor=_GRID),
        legend=dict(orientation='h', y=1.12),
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font_color='#FAFAFA',
        margin=dict(l=10, r=10, t=70, b=90),
    )
    return fig


def line_empleo_temporal(df: pd.DataFrame) -> go.Figure:
    fuentes = df['fuente'].unique().tolist() if 'fuente' in df.columns else []
    # Ensure all elements in fuentes are strings to avoid TypeError during join
    fuentes_str = [str(f) for f in fuentes if pd.notna(f)]
    subtitle = f" · Fuente: {', '.join(fuentes_str)}" if fuentes_str else ''
    fig = px.line(
        df,
        x='anio',
        y='tasa_empleo',
        markers=True,
        labels={'anio': 'Año', 'tasa_empleo': 'Tasa de Empleo (%)'},
        color_discrete_sequence=[_ACCENT],
    )
    fig.update_traces(line_width=2, marker_size=7)
    return _base_layout(fig, f'Evolución de Inserción Laboral{subtitle}')


def bar_tasa_desercion(data: dict) -> go.Figure:
    tasa       = data.get('tasa_desercion') or 0
    total      = data.get('total_estudiantes') or 0
    en_riesgo  = data.get('en_riesgo') or 0
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=tasa,
        number={'suffix': '%', 'font': {'color': '#FAFAFA'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#c7c4d7'},
            'bar':  {'color': _ORANGE},
            'bgcolor': _GRID,
            'steps': [
                {'range': [0, 20],  'color': 'rgba(34, 197, 94, 0.13)'},
                {'range': [20, 40], 'color': 'rgba(245, 158, 11, 0.13)'},
                {'range': [40, 100],'color': 'rgba(239, 68, 68, 0.13)'},
            ],
            'threshold': {
                'line': {'color': '#EF4444', 'width': 3},
                'thickness': 0.75,
                'value': tasa,
            },
        },
        title={
            'text': f'Tasa de Deserción<br><span style="font-size:0.75rem;color:#c7c4d7">{en_riesgo} en riesgo de {total} estudiantes</span>',
            'font': {'color': '#FAFAFA'},
        },
    ))
    fig.update_layout(
        paper_bgcolor=_BG,
        font_color='#FAFAFA',
        margin=dict(l=10, r=10, t=30, b=10),
        height=280,
    )
    return fig


_ISO3_NAMES = {
    'arg': 'Argentina',
    'atg': 'Antigua y Barbuda',
    'blz': 'Belice',
    'bol': 'Bolivia',
    'bra': 'Brasil',
    'chl': 'Chile',
    'col': 'Colombia',
    'cri': 'Costa Rica',
    'cub': 'Cuba',
    'dma': 'Dominica',
    'dom': 'Rep. Dominicana',
    'ecu': 'Ecuador',
    'gtm': 'Guatemala',
    'hnd': 'Honduras',
    'mex': 'México',
    'pan': 'Panamá',
    'per': 'Perú',
    'pry': 'Paraguay',
    'ven': 'Venezuela',
}


def bar_cepal_benchmark(df: pd.DataFrame) -> go.Figure:
    """Vertical bar chart: one bar per country, value = average TIC indicator across years.
    df must have columns [iso3, value] (already averaged by get_cepal_benchmark).
    """
    df = df.copy()
    df['pais'] = df['iso3'].str.lower().map(_ISO3_NAMES).fillna(df['iso3'].str.upper())
    df = df.sort_values('value', ascending=False)

    fig = px.bar(
        df,
        x='pais',
        y='value',
        text='value',
        labels={'pais': '', 'value': 'Jóvenes con competencias TIC (%)'},
        color_discrete_sequence=[_ACCENT],
    )
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, 105], gridcolor=_GRID, zerolinecolor=_GRID))
    return _base_layout(fig, 'Jóvenes con competencias TIC · CEPALSTAT (ODS 4.4.1)')


def bar_cepal_pais_years(df: pd.DataFrame, pais_nombre: str) -> go.Figure:
    """Vertical bar chart for a single country, one bar per year.
    df must have columns [anio, value] from get_cepal_pais_years.
    """
    df = df.copy()
    df['anio_str'] = df['anio'].astype(str)

    fig = px.bar(
        df,
        x='anio_str',
        y='value',
        text='value',
        labels={'anio_str': 'Año', 'value': 'Jóvenes con competencias TIC (%)'},
        color_discrete_sequence=[_ACCENT],
    )
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, 105], gridcolor=_GRID, zerolinecolor=_GRID))
    return _base_layout(fig, f'Jóvenes con competencias TIC — {pais_nombre} · CEPALSTAT (ODS 4.4.1)')


def line_cepal_bolivia(df: pd.DataFrame) -> go.Figure:
    multi_country = 'iso3' in df.columns and df['iso3'].nunique() > 1
    title = (
        'Indicador TIC — Región Andina · CEPALSTAT (ODS 4.4.1)'
        if multi_country
        else 'Indicador TIC Bolivia — CEPALSTAT (ODS 4.4.1)'
    )
    fig = px.line(
        df,
        x='anio',
        y='value',
        color='iso3' if multi_country else None,
        markers=True,
        labels={'anio': 'Año', 'value': 'Indicador TIC (%)', 'iso3': 'País'},
        color_discrete_sequence=None if multi_country else [_ACCENT],
    )
    fig.update_traces(line_width=2, marker_size=7)
    return _base_layout(fig, title)
