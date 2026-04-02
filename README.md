<div align="center">

<h1>Digital Labor Gap Reduction — BI Strategy</h1>

<p><strong>A Business Intelligence pipeline that connects academic data with real labor market demand to reduce the digital skills gap in technical higher education.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQL_Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Gemini_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini API">
  <img src="https://img.shields.io/badge/Adzuna_API-FF6600?style=for-the-badge&logo=briefcase&logoColor=white" alt="Adzuna API">
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
- [OKRs](#okrs)
- [Stack](#stack)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Snowflake Schema](#snowflake-schema)
- [Sprint Schedule](#sprint-schedule)
- [Team & Workflow](#team--workflow)
- [Kanban Board & Contributing](#kanban-board--contributing)
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

## OKRs

OKRs define project success with measurable key results. Full explanation in [`docs/guia-del-proyecto.md`](docs/guia-del-proyecto.md).

| Objective | Key Result | Metric |
|-----------|------------|--------|
| **O1: Functional end-to-end pipeline** | KR1: All 3 layers implemented without errors | Bronze ✓ Silver ✓ Gold ✓ |
| | KR2: Silver data with 0% nulls or geographic inconsistencies | `df.isnull().sum() == 0` |
| | KR3: DW with fact table and all dimensions loaded with real data | `DW_BrechaDigital` populated |
| **O2: Actionable insights on the digital gap** | KR1: Dashboard shows 4+ KPIs with real data | 4 functional pages |
| | KR2: 3+ skills with gap identified | Skill Gap analyzed |
| | KR3: Analysis covers 2+ Bolivian cities | Regional benchmarking |
| **O3: Demonstrated BI methodology mastery** | KR1: All 4 dashboard sections working | Demo Day ready |
| | KR2: Each team member explains their layer without notes | Individual understanding |
| | KR3: Final report documents key technical decisions | Complete PDF |

---

## Stack

| Category | Technology | Version |
|---|---|---|
| Data Processing | Python | 3.11+ |
| Data Manipulation | Pandas | 2.0+ |
| Bronze Database | SQL Server (T-SQL) — `BrechaDigitalDB` | 2019+ |
| Gold Warehouse | SQL Server (T-SQL) — `DW_BrechaDigital` | 2019+ |
| Dashboard | Streamlit | 1.32+ |
| Charts | Plotly | 5.20+ |
| AI Assistant | Google Gemini API | 0.5+ |
| Macro Data | CEPALSTAT REST API | — |
| Employment Data | Adzuna REST API | — |
| DB Connectivity | PyODBC + SQLAlchemy | 5.0+ / 2.0+ |
| Environment | python-dotenv | 1.0+ |

---

## Architecture

The project follows a **Bronze → Silver → Gold** medallion architecture:

```
SQL Server BrechaDigitalDB     CEPALSTAT API        Adzuna API
      [Bronze — Source]         [Macro Data]     [Employment Data]
             │                       │                   │
             └───────────────────────┴───────────────────┘
                                     │
                          src/ingestion/ (Python)
                          sqlserver.py · cepalstat.py · empleos.py
                                     │
                               data/raw/
                             [Bronze — CSV]
                                     │
                          src/transform/ (Python)
                          clean.py · normalize.py
                                     │
                            data/processed/
                             [Silver — CSV]
                                     │
                           src/schema/ (Python)
                           facts.py · dimensions.py
                                     │
                     SQL Server DW_BrechaDigital
                   [Gold — Snowflake Schema T-SQL]
                    Fact_InsercionLaboral · DIM_* tables
                                     │
                          src/dashboard/ (Streamlit)
                     KPIs · Employability · Skill Gap · Chatbot
```

---

## Data Pipeline

| Step | Module | Input | Output |
|---|---|---|---|
| 1. Extract | `src/ingestion/sqlserver.py` | `BrechaDigitalDB` (SQL Server) | `data/raw/*.csv` |
| 2. Extract | `src/ingestion/cepalstat.py` | CEPALSTAT REST API | `data/raw/cepalstat/*.csv` |
| 3. Extract | `src/ingestion/empleos.py` | Adzuna REST API | `data/raw/empleos/*.csv` |
| 4. Clean | `src/transform/clean.py` | `data/raw/*.csv` | `data/processed/*.csv` |
| 5. Normalize | `src/transform/normalize.py` | `data/processed/*.csv` | `data/processed/*.csv` |
| 6. Load Dimensions | `src/schema/dimensions.py` | `data/processed/*.csv` | `DW_BrechaDigital` — DIM_* tables |
| 7. Load Facts | `src/schema/facts.py` | `data/processed/*.csv` | `DW_BrechaDigital` — Fact_InsercionLaboral |

---

## Snowflake Schema

Normalized dimension model: sub-dimensions reduce data redundancy and improve referential integrity. Chosen over star schema for technical correctness at the cost of additional JOINs.

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

## Sprint Schedule

| Day | Date | Phase | Layer |
|---|---|---|---|
| Day 1 | April 1 | Definition, GitHub setup, Bronze extraction | Bronze |
| Day 2 | April 2 | Cleaning, transformation, integration | Silver |
| Day 3 | April 3 | Star schema modeling + Dashboard construction | Gold + Viz |
| Day 4 | April 6 | Final testing, storytelling polish, documentation | All |
| Day 5 | April 7 | **DEMO DAY** — 10-minute presentation | — |

Progress is tracked on the [GitHub Kanban Board](https://github.com/users/temps-code/projects/3).

---

## Team & Workflow

All members contribute across every phase. Each person listed below is the **lead** for their phase — responsible for managing, reviewing, and ensuring quality of that layer's deliverables.

| Member | Phase Lead | GitHub |
|---|---|---|
| Abraham Flores Barrionuevo | Bronze — Data Ingestion | [@AFB-9898](https://github.com/AFB-9898) |
| Juan Nicolás Flores Delgado | Silver — Transformation | [@Juan7139nf](https://github.com/Juan7139nf) |
| Micaela Pérez Vásquez | Gold — Schema Design | [@Sam24p](https://github.com/Sam24p)|
| Mayra Villca Méndez | Analysis & KPIs — Notebooks | [@MayVillca](https://github.com/MayVillca) |
| Diego Vargas Urzagaste | Dashboard & Integration | [@temps-code](https://github.com/temps-code) |

---

## Kanban Board & Contributing

All team progress is tracked on the [GitHub Kanban Board](https://github.com/users/temps-code/projects/3) — open the **Projects** tab in the repository.

### Board columns

| Column | When to use |
|---|---|
| Todo | Task not yet started |
| In Progress | You are actively working on it |
| Testing/Review | Work done — waiting for the Lead to review |
| Done | Lead approved — task complete |

> The Lead for each phase is the only one who moves a card to **Done**. Never close your own task — wait for review.

### Day-to-day workflow

1. Open your issue from the [Issues tab](https://github.com/temps-code/brecha-digital-bi/issues)
2. Move your card to **In Progress** on the board
3. Create your working branch:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-phase   # e.g. feature/bronze
   ```

4. Commit your progress frequently:

   ```bash
   git add .
   git commit -m "feat: brief description of what you did"
   git push origin feature/your-phase
   ```

5. When finished: move card to **Testing/Review** and notify Diego (@temps-code)
6. Check off completed tasks inside your issue using the checkboxes

### Branch naming

| Phase | Branch |
|---|---|
| Bronze — Data Ingestion | `feature/bronze` |
| Silver — Transformation | `feature/silver` |
| Gold — Schema | `feature/gold` |
| Dashboard | `feature/dashboard` |
| Notebooks & KPIs | `feature/notebooks` |

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
# SQL Server — Bronze Source
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=BrechaDigitalDB
DB_USER=sa
DB_PASSWORD=your_password

# SQL Server — Gold Warehouse
DW_SERVER=localhost\SQLEXPRESS
DW_NAME=DW_BrechaDigital
DW_USER=sa
DW_PASSWORD=your_password

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# CEPALSTAT (no key required — public API)
CEPALSTAT_BASE_URL=https://api-cepalstat.cepal.org/cepalstat/api/v1

# Adzuna Employment API
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
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
