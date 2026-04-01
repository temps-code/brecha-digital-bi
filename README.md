<div align="center">

<h1>Digital Labor Gap Reduction — BI Strategy</h1>

<p><strong>A Business Intelligence pipeline that connects academic data with real labor market demand to reduce the digital skills gap in technical higher education.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQL_Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Gemini_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini API">
</p>

</div>

---

📄 Read this in: **English** | [Español](README.es.md)

---

**Academic Project**
Universidad Privada Domingo Savio — Ing. de Sistemas
Course: Business Intelligence — 2026

---

## Table of Contents

- [What It Does](#what-it-does)
- [Stack](#stack)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Snowflake Schema](#snowflake-schema)
- [Team](#team)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Dashboard](#running-the-dashboard)

---

## What It Does

Bolivian technical education institutions generate large amounts of academic data but lack the tools to connect it with real labor market demand. This project addresses that disconnect.

**Before**: Decision-making based on intuition, fragmented data silos, and no visibility into graduate employability.

**After**: A unified BI pipeline that integrates internal academic records with external labor market data, exposing actionable KPIs through an interactive dashboard.

Key capabilities:

- Automated ELT pipeline from SQL Server (Bronze) through transformation (Silver) to a snowflake-schema warehouse (Gold)
- KPI monitoring: employability rate, dropout prediction, skill gap analysis
- Regional benchmarking using CEPALSTAT indicators (ODS 4 and ODS 8)
- Real-time job vacancy analysis from external employment APIs
- AI-powered assistant (Gemini API) for natural language queries over the data

---

## Stack

| Category | Technology | Version |
|---|---|---|
| Data Processing | Python | 3.11+ |
| Data Manipulation | Pandas | 2.0+ |
| Source Database | SQL Server (T-SQL) | 2019+ |
| Warehouse | SQLite | 3.x |
| Dashboard | Streamlit | 1.32+ |
| Charts | Plotly | 5.20+ |
| AI Assistant | Google Gemini API | 0.5+ |
| External Data | CEPALSTAT REST API | — |
| DB Connectivity | PyODBC + SQLAlchemy | 5.0+ / 2.0+ |
| Environment | python-dotenv | 1.0+ |

---

## Architecture

The project follows a **Bronze → Silver → Gold** medallion architecture:

```
SQL Server (T-SQL)          CEPALSTAT API       Employment APIs
    [Bronze Source]           [External]           [External]
          │                       │                    │
          └───────────────────────┴────────────────────┘
                                  │
                       src/ingestion/ (Python)
                                  │
                            data/raw/
                          [Bronze — CSV]
                                  │
                       src/transform/ (Python)
                    clean.py + normalize.py
                                  │
                         data/processed/
                          [Silver — CSV]
                                  │
                        src/schema/ (Python)
                     facts.py + dimensions.py
                                  │
                         data/warehouse/
                      [Gold — SQLite, Snowflake Schema]
                                  │
                       src/dashboard/ (Streamlit)
                  KPIs · Employability · Skill Gap · Chatbot
```

---

## Data Pipeline

| Step | Module | Input | Output |
|---|---|---|---|
| 1. Extract | `src/ingestion/sqlserver.py` | SQL Server tables | `data/raw/*.csv` |
| 2. Extract | `src/ingestion/cepalstat.py` | CEPALSTAT API | `data/raw/cepalstat/*.csv` |
| 3. Extract | `src/ingestion/empleos.py` | Employment APIs | `data/raw/empleos/*.csv` |
| 4. Clean | `src/transform/clean.py` | Raw CSV | `data/processed/*.csv` |
| 5. Normalize | `src/transform/normalize.py` | Processed CSV | `data/processed/*.csv` |
| 6. Load | `src/schema/facts.py` | Processed CSV | SQLite warehouse |
| 7. Load | `src/schema/dimensions.py` | Processed CSV | SQLite warehouse |

---

## Snowflake Schema

```
                         DIM_CARRERA
                              ▲
              DIM_CATEGORIA_SKILL   DIM_ESTUDIANTE
                     ▲                    ▲
               DIM_HABILIDAD              │
                     ▲                    │
                     └── FACT_INSERCION_LABORAL ──► DIM_TIEMPO
                                          │
                                          └────────► DIM_MERCADO_LABORAL
                                                              ▲
                                                         DIM_REGION
```

Full schema documentation: [`docs/esquema_copo_nieve.md`](docs/esquema_copo_nieve.md)

---

## Team

| Member | Role | GitHub |
|---|---|---|
| Abraham Flores Barrionuevo | Data Ingestion | [@AFB-9898](https://github.com/AFB-9898) |
| Juan Nicolás Flores Delgado | Data Transformation | [@Juan7139nf](https://github.com/Juan7139nf) |
| Micaela Pérez Vásquez | Schema Design | — |
| Mayra Villca Méndez | Analysis & KPIs | — |
| Diego Vargas Urzagaste | Dashboard & Integration | [@temps-code](https://github.com/temps-code) |

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/temps-code/brecha-digital-bi.git
   cd brecha-digital-bi
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux / macOS
   .venv\Scripts\activate           # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (see [Environment Variables](#environment-variables)).

5. Seed the Bronze database — execute `database/seed.sql` in SQL Server Management Studio (SSMS).

6. Run the full pipeline:

   ```bash
   python src/ingestion/sqlserver.py
   python src/ingestion/cepalstat.py
   python src/ingestion/empleos.py
   python src/transform/clean.py
   python src/transform/normalize.py
   python src/schema/dimensions.py
   python src/schema/facts.py
   ```

---

## Environment Variables

Create a `.env` file in the root directory:

```env
# SQL Server
DB_SERVER=localhost
DB_NAME=BrechаDigitalDB
DB_USER=sa
DB_PASSWORD=your_password

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# External APIs
CEPALSTAT_BASE_URL=https://api-cepalstat.cepal.org/cepalstat/api/v1
EMPLEOS_API_KEY=your_api_key
```

> Never commit the `.env` file. It is already listed in `.gitignore`.

---

## Running the Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard will be available at `http://localhost:8501`.

| Page | Description |
|---|---|
| KPIs | General employability and dropout indicators |
| Labor Insertion | Graduate insertion rate by career and region |
| Skill Gap | Comparison between academic skills and market demand |
| AI Assistant | Natural language queries powered by Gemini API |

---

<div align="center">
<img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
</div>
