"""
Dashboard — Design System
"The Digital Cartographer" — high-end editorial intelligence.
Sistema de estilos centralizado. Llamar inject_styles() al inicio de cada página.
Paleta obsidian #131315 + primary #c0c1ff + tertiary #ffb783, tipografía Inter, iconos Tabler Icons.
"""
import streamlit as st

_CSS = """
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.34.0/dist/tabler-icons.min.css"
/>
<link
  rel="preconnect"
  href="https://fonts.googleapis.com"
/>
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
/>
<style>
  /* ── Design tokens — Digital Cartographer ──────────── */
  :root {
    --bg:            #131315;   /* background / surface-dim */
    --surface:       #1c1b1d;   /* surface-container-low   */
    --surface-2:     #2a2a2c;   /* surface-container-high  */
    --surface-3:     #353437;   /* surface-container-highest / glass base */
    --border:        rgba(70,69,84,0.25);  /* outline-variant @25% — ghost border rule */
    --text:          #e5e1e4;   /* on-surface */
    --muted:         #c7c4d7;   /* on-surface-variant */
    --accent:        #c0c1ff;   /* primary */
    --accent-deep:   #8083ff;   /* primary-container */
    --accent-muted:  #42447b;   /* secondary-container */
    --warm:          #ffb783;   /* tertiary */
    --success:       #22C55E;
    --warning:       #EAB308;
    --danger:        #EF4444;
  }

  /* ── Base ──────────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }
  .block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 2rem !important;
  }

  /* ── Sidebar ───────────────────────────────────────── */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
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
    font-weight: 700;
    color: var(--text);
    margin: 0 0 0.25rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.02em;
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

  /* ── Divider — ghost rule (no hard lines) ──────────── */
  hr.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.25rem 0;
  }

  /* ── KPI Card — Digital Cartographer style ─────────── */
  .kpi-card {
    background: var(--surface-2);
    border-radius: 1rem;
    padding: 1.25rem 1.5rem 1rem;
    overflow: hidden;
    position: relative;
    transition: background 0.2s;
  }
  .kpi-card:hover {
    background: var(--surface-3);
  }
  .kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .kpi-label i {
    font-size: 0.9rem;
    color: var(--accent);
  }
  .kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
    letter-spacing: -0.02em;
    margin-bottom: 1rem;
  }
  /* Bottom progress bar — KPI card signature detail */
  .kpi-card::after {
    content: '';
    display: block;
    height: 2px;
    width: 100%;
    margin-top: 0.75rem;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-deep) 100%);
    border-radius: 1px;
    opacity: 0.7;
  }

  /* ── Nav card (home) — editorial bento style ───────── */
  .nav-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 1rem;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s;
  }
  .nav-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(192,193,255,0.04) 0%, rgba(128,131,255,0.02) 100%);
    opacity: 0;
    transition: opacity 0.3s;
  }
  .nav-icon {
    font-size: 1.5rem;
    color: var(--accent);
    margin-bottom: 0.75rem;
    display: block;
  }
  .nav-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.375rem;
    letter-spacing: -0.01em;
  }
  .nav-desc {
    font-size: 0.8125rem;
    color: var(--muted);
    line-height: 1.55;
  }
  a.nav-link { text-decoration: none; color: inherit; display: block; }
  a.nav-link:hover .nav-card {
    border-color: rgba(192,193,255,0.5);
    background: var(--surface-2);
  }
  a.nav-link:hover .nav-card::before { opacity: 1; }

  /* ── Glass card (floating/modal elements) ──────────── */
  .glass-card {
    background: rgba(42, 42, 44, 0.8);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 1rem;
  }

  /* ── Badge ─────────────────────────────────────────── */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 4px;
    background: var(--accent-muted);
    color: var(--accent);
    letter-spacing: 0.04em;
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
    background: var(--surface-2);
    border-top: 2px solid var(--accent);
    border-radius: 1rem;
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
    border-radius: 0.5rem;
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
    background: var(--surface-2);
    border-radius: 0.5rem;
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
    background: var(--surface-3);
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
    """Inyecta CSS en la página. Usa st.html() para mejor compatibilidad con Streamlit."""
    st.html(_CSS)
