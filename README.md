<div align="center">

<h1>Digital Labor Gap — BI Strategy</h1>

<p><strong>A Business Intelligence pipeline connecting academic data with real labor market demand to measure and reduce the digital skills gap in Bolivian technical higher education.</strong></p>

<p>
  <a href="https://brecha-digital-bolivia-bi.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo">
  </a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQL_Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Groq_API-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq API">
  <img src="https://img.shields.io/badge/Adzuna_API-FF6600?style=for-the-badge&logo=briefcase&logoColor=white" alt="Adzuna API">
  <img src="https://img.shields.io/badge/CEPALSTAT-009DDD?style=for-the-badge&logo=un&logoColor=white" alt="CEPALSTAT">
</p>

</div>

---

📄 Read this in: **English** | [Español](README.es.md)

---

**Academic Project**  
Universidad Privada Domingo Savio — Computer Systems Engineering  
Course: Business Intelligence — 2026

---

## Table of Contents

- [Live Demo](#live-demo)
- [What It Does](#what-it-does)
- [Dashboard Pages](#dashboard-pages)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Data Pipeline](#data-pipeline)
- [Snowflake Schema](#snowflake-schema)
- [Team](#team)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Streamlit Cloud Deployment](#streamlit-cloud-deployment)

---

## Live Demo

**[brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/)**

The application is deployed on Streamlit Cloud and connects live to the Groq API for the AI assistant and uses pre-processed CSV files for academic and labor market data.

---

## What It Does

Bolivian technical education institutions generate large amounts of academic data but lack the tools to connect it with real labor market demand. This project bridges that gap.

**Before:** Decision-making based on intuition, fragmented data silos, no visibility into graduate employability.

**After:** A unified BI pipeline that integrates internal academic records with external labor market data, exposing actionable KPIs through an interactive dashboard — accessible to any academic director without technical knowledge.

**Core capabilities:**

- **End-to-end ELT pipeline:** SQL Server (Bronze) → Python transformation (Silver) → Snowflake schema warehouse (Gold)
- **IT-focused analysis:** Exclusively covers 5 programs — Software Engineering, Systems Engineering, Data Science, Telecommunications, and Cybersecurity
- **Labor market intelligence:** Real job vacancy data from Adzuna API (US, Spain, Mexico, Brazil) with AI-powered skill extraction via Groq LLM
- **KPI monitoring:** Graduate employability rate, dropout risk, skill gap analysis, salary benchmarking
- **Regional benchmark:** CEPALSTAT ODS 4.4.1 indicator — digital skills competency across 17 Latin American countries
- **AI assistant:** Natural language queries over the full dataset, powered by LLaMA 3.1 (Groq API)

---

## Dashboard Pages

| Page | URL | Description |
|---|---|---|
| Overview | `/` | Hero KPIs, navigation, data sources |
| KPIs | `/kpis` | Employment rate, dropout risk gauge, CEPALSTAT regional benchmark |
| Labor Insertion | `/insercion` | Insertion rate by career, salary distribution, temporal trends, city heatmap |
| Skill Gap | `/skill_gap` | Market skills vs academic curriculum, coverage analysis, LLM-extracted skills |
| AI Assistant | `/chatbot` | Natural language BI queries — LLaMA 3.1 8B via Groq API |

---

## Architecture

```
SQL Server BrechaDigitalDB      CEPALSTAT API         Adzuna API
      [Bronze — Source]          [Macro Data]      [Employment Data]
             │                        │                    │
             └────────────────────────┴────────────────────┘
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
                         ┌────────────┴────────────┐
                         │                         │
              src/ingestion/skill_extraction.py   src/schema/ (Python)
              Groq LLM → skills_extracted.csv     facts.py · dimensions.py
                         │                         │
                         └────────────┬────────────┘
                                      │
                        SQL Server DW_BrechaDigital
                      [Gold — Snowflake Schema T-SQL]
                       Fact_InsercionLaboral · DIM_* tables
                                      │
                             src/dashboard/ (Streamlit)
               KPIs · Labor Insertion · Skill Gap · AI Chatbot
```

---

## Tech Stack

| Category | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Data Manipulation | Pandas | 2.0+ |
| Bronze Database | SQL Server (T-SQL) — `BrechaDigitalDB` | 2019+ |
| Gold Warehouse | SQL Server (T-SQL) — `DW_BrechaDigital` | 2019+ |
| Dashboard | Streamlit | 1.32+ |
| Charts | Plotly | 5.20+ |
| AI Skill Extraction | Groq API (LLaMA 3.1 8B) | 0.9+ |
| AI Assistant | Groq API (LLaMA 3.1 8B Instant) | 0.9+ |
| Macro Data | CEPALSTAT REST API | — |
| Employment Data | Adzuna REST API | — |
| DB Connectivity | PyODBC + SQLAlchemy | 5.0+ / 2.0+ |
| Environment | python-dotenv | 1.0+ |

---

## Data Pipeline

| Step | Module | Input | Output |
|---|---|---|---|
| 1. Extract Academic | `src/ingestion/sqlserver.py` | `BrechaDigitalDB` (SQL Server) | `data/raw/*.csv` |
| 2. Extract Macro | `src/ingestion/cepalstat.py` | CEPALSTAT REST API | `data/raw/cepalstat/*.csv` |
| 3. Extract Jobs | `src/ingestion/empleos.py` | Adzuna REST API | `data/raw/empleos/*.csv` |
| 4. Extract Skills | `src/ingestion/skill_extraction.py` | Adzuna job descriptions | `data/processed/empleos/skills_extracted.csv` |
| 5. Clean | `src/transform/clean.py` | `data/raw/*.csv` | `data/processed/*.csv` |
| 6. Normalize | `src/transform/normalize.py` | `data/processed/*.csv` | `data/processed/*.csv` |
| 7. Load Dimensions | `src/schema/dimensions.py` | `data/processed/*.csv` | `DW_BrechaDigital` — DIM_* tables |
| 8. Load Facts | `src/schema/facts.py` | `data/processed/*.csv` | `DW_BrechaDigital` — Fact_InsercionLaboral |

### Skill Extraction Pipeline

Job descriptions from Adzuna are processed by `skill_extraction.py` using a two-stage approach:

1. **Groq LLM (primary):** Sends raw job descriptions to `llama-3.1-8b-instant` and extracts structured skill lists in JSON format
2. **Regex fallback:** If LLM fails or rate-limits, a regex pattern bank covers the most common tech keywords

The output `skills_extracted.csv` is committed to the repository for reproducibility and to avoid runtime LLM costs on every dashboard load.

---

## Snowflake Schema

Normalized dimension model chosen over star schema for technical correctness. Sub-dimensions reduce redundancy and improve referential integrity at the cost of additional JOINs.

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
| Abraham Flores Barrionuevo | Bronze Lead — Data Ingestion | [@AFB-9898](https://github.com/AFB-9898) |
| Juan Nicolás Flores Delgado | Silver Lead — Transformation | [@Juan7139nf](https://github.com/Juan7139nf) |
| Micaela Pérez Vásquez | Gold Lead — Schema Design | [@Sam24p](https://github.com/Sam24p) |
| Mayra Villca Méndez | Analysis Lead — Notebooks & KPIs | [@MayVillca](https://github.com/MayVillca) |
| Diego Vargas Urzagaste | Dashboard Lead — Integration & Deployment | [@temps-code](https://github.com/temps-code) |

Progress tracked on the [GitHub Kanban Board](https://github.com/users/temps-code/projects/3).

---

## Installation

```bash
# 1. Clone
git clone https://github.com/temps-code/brecha-digital-bi.git
cd brecha-digital-bi

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Dependencies
pip install -r requirements.txt

# 4. Configure environment variables (see below)

# 5. Seed the Bronze database
#    Execute database/seed.sql in SQL Server Management Studio

# 6. Run the full pipeline
python src/ingestion/sqlserver.py
python src/ingestion/cepalstat.py
python src/ingestion/empleos.py
python src/ingestion/skill_extraction.py   # LLM skill extraction
python src/transform/clean.py
python src/transform/normalize.py
python src/schema/dimensions.py
python src/schema/facts.py
```

---

## Environment Variables

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

```env
# SQL Server — Bronze Source
DB_SERVER=localhost,1433
DB_NAME=BrechaDigitalDB
DB_USER=sa
DB_PASSWORD=your_password

# SQL Server — Gold Warehouse
DW_SERVER=localhost,1433
DW_NAME=DW_BrechaDigital
DW_USER=sa
DW_PASSWORD=your_password

# Groq API — AI assistant + skill extraction
GROQ_API_KEY=your_groq_api_key

# CEPALSTAT (public API — no key required)
CEPALSTAT_BASE_URL=https://api-cepalstat.cepal.org/cepalstat/api/v1

# Adzuna Employment API
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

> The `.env` file is already in `.gitignore`. Never commit it.  
> The pipeline auto-detects auth mode: SQL Auth when credentials are set, Windows Auth otherwise.

---

## Streamlit Cloud Deployment

The app is deployed at **[brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/)**.

For your own Streamlit Cloud deployment:

1. Fork or push to GitHub
2. Connect the repository in [share.streamlit.io](https://share.streamlit.io)
3. Set **Main file path** to `src/dashboard/app.py`
4. Add secrets in **Settings → Secrets** (TOML format):

```toml
GROQ_API_KEY = "gsk_your_key_here"
ADZUNA_APP_ID = "your_id"
ADZUNA_APP_KEY = "your_key"
DB_SERVER = "your_server"
DB_NAME = "BrechaDigitalDB"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
DW_SERVER = "your_server"
DW_NAME = "DW_BrechaDigital"
DW_USER = "your_user"
DW_PASSWORD = "your_password"
```

> Note: Without SQL Server access, the dashboard automatically falls back to the pre-processed CSV files in `data/processed/` — no data loss for the deployed version.

---

<div align="center">
<img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
<br><br>
<a href="https://brecha-digital-bolivia-bi.streamlit.app/">
  <img src="https://img.shields.io/badge/▶_Open_Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Open Live Demo">
</a>
</div>
