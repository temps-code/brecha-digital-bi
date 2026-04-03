"""
Dashboard — Design System
Sistema de estilos centralizado. Llamar inject_styles() al inicio de cada página.
Paleta zinc-950 + indigo-500, tipografía Inter, iconos Tabler Icons.
"""
import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.34.0/dist/tabler-icons.min.css');
  /* ── Design tokens ─────────────────────────────────── */
  :root {
    --bg:           #09090B;
    --surface:      #18181B;
    --surface-2:    #27272A;
    --border:       #3F3F46;
    --text:         #FAFAFA;
    --muted:        #A1A1AA;
    --accent:       #6366F1;
    --accent-muted: #1E1B4B;
    --success:      #22C55E;
    --warning:      #EAB308;
    --danger:       #EF4444;
  }

  /* ── Base ──────────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
  }
  .block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 2rem !important;
  }

  /* ── Sidebar ───────────────────────────────────────── */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }
  section[data-testid="stSidebar"] label {
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
  }

  /* ── Page header ───────────────────────────────────── */
  .page-header {
    margin-bottom: 1.25rem;
  }
  .page-header h2 {
    font-size: 1.375rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 0.25rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.01em;
  }
  .page-header h2 i {
    color: var(--accent);
    font-size: 1.25rem;
  }
  .page-header p {
    font-size: 0.875rem;
    color: var(--muted);
    margin: 0;
  }

  /* ── Divider ───────────────────────────────────────── */
  hr.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.25rem 0;
  }

  /* ── KPI Card ──────────────────────────────────────── */
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
  }
  .kpi-label {
    font-size: 0.6875rem;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.625rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .kpi-label i {
    font-size: 0.875rem;
    color: var(--accent);
  }
  .kpi-value {
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
    letter-spacing: -0.02em;
  }

  /* ── Nav card (home) ───────────────────────────────── */
  .nav-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
  }
  .nav-icon {
    font-size: 1.375rem;
    color: var(--accent);
    margin-bottom: 0.625rem;
    display: block;
  }
  .nav-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.25rem;
  }
  .nav-desc {
    font-size: 0.8125rem;
    color: var(--muted);
    line-height: 1.5;
  }

  /* ── Badge ─────────────────────────────────────────── */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.6875rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 4px;
    background: var(--accent-muted);
    color: #A5B4FC;
    margin: 2px;
  }

  /* ── Source list (home) ────────────────────────────── */
  .source-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: var(--muted);
    padding: 0.3rem 0;
  }
  .source-item i {
    color: var(--accent);
    flex-shrink: 0;
    margin-top: 1px;
    font-size: 1rem;
  }
  .source-item b {
    color: var(--text);
  }

  /* ── ODS card ──────────────────────────────────────── */
  .ods-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    height: 100%;
  }
  .ods-card .ods-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.375rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .ods-card .ods-title i { color: var(--accent); }
  .ods-card .ods-body {
    font-size: 0.8125rem;
    color: var(--muted);
    line-height: 1.6;
  }

  /* ── Alert card ────────────────────────────────────── */
  .alert-card {
    background: #1C0A0A;
    border-left: 3px solid var(--danger);
    border-radius: 6px;
    padding: 0.875rem 1rem;
    margin-bottom: 1rem;
  }
  .alert-card .alert-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #FCA5A5;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.3rem;
  }
  .alert-card .alert-body {
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.5;
  }

  /* ── Skill card ────────────────────────────────────── */
  .skill-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.875rem 1rem;
    margin-bottom: 0.5rem;
  }
  .skill-card .skill-name {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.375rem;
  }
  .skill-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    color: var(--muted);
    background: var(--surface-2);
    border-radius: 4px;
    padding: 2px 8px;
    margin: 2px 2px 2px 0;
  }
  .skill-tag i { font-size: 0.75rem; color: var(--success); }

  /* ── Suggestion buttons (chatbot) ──────────────────── */
  .sug-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
  }

  /* ── Expander ──────────────────────────────────────── */
  .streamlit-expanderHeader {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
  }

  /* ── Tabler icon sizing ────────────────────────────── */
  .ti { vertical-align: middle; line-height: 1; }
</style>
"""


def inject_styles() -> None:
    # st.html() inyecta HTML arbitrario sin el parser de Markdown (Streamlit ≥1.36)
    st.html(_CSS)
