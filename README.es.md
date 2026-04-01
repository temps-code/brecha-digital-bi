<div align="center">

<h1>Reducción de la Brecha Digital Laboral — Estrategia BI</h1>

<p><strong>Pipeline de Business Intelligence que conecta datos académicos con la demanda real del mercado laboral para reducir la brecha de habilidades digitales en la educación técnica superior.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQL_Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Gemini_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini API">
  <img src="https://img.shields.io/badge/Adzuna_API-FF6600?style=for-the-badge&logo=briefcase&logoColor=white" alt="Adzuna API">
</p>

</div>

---

📄 Leé esto en: [English](README.md) | **Español**

---

**Proyecto Académico**
Universidad Privada Domingo Savio — Ing. de Sistemas
Materia: Inteligencia de Negocios — 2026

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Pipeline de Datos](#pipeline-de-datos)
- [Esquema Copo de Nieve](#esquema-copo-de-nieve)
- [Cronograma de Sprints](#cronograma-de-sprints)
- [Equipo y Forma de Trabajo](#equipo-y-forma-de-trabajo)
- [Instalación](#instalación)
- [Variables de Entorno](#variables-de-entorno)
- [Ejecutar el Dashboard](#ejecutar-el-dashboard)

---

## Descripción

Las instituciones de educación técnica bolivianas generan grandes volúmenes de datos académicos pero carecen de herramientas para conectarlos con la demanda real del mercado laboral. Este proyecto resuelve esa desconexión.

**Antes**: Toma de decisiones basada en intuición, silos de información fragmentados y sin visibilidad sobre la empleabilidad de los egresados.

**Después**: Un pipeline BI unificado que integra registros académicos internos con datos externos del mercado laboral, exponiendo KPIs accionables a través de un dashboard interactivo.

Capacidades principales:

- Pipeline ELT automatizado desde SQL Server (Bronze) pasando por transformación (Silver) hasta un warehouse con esquema copo de nieve (Gold)
- Monitoreo de KPIs: tasa de inserción laboral, predicción de deserción, análisis de brecha de habilidades
- Benchmarking regional usando indicadores CEPALSTAT (ODS 4 y ODS 8)
- Análisis de vacantes laborales en tiempo real desde APIs externas de empleo
- Asistente con IA (Gemini API) para consultas en lenguaje natural sobre los datos

---

## Stack

| Categoría | Tecnología | Versión |
|---|---|---|
| Procesamiento de Datos | Python | 3.11+ |
| Manipulación de Datos | Pandas | 2.0+ |
| Base de Datos Bronze | SQL Server (T-SQL) — `BrechaDigitalDB` | 2019+ |
| Warehouse Gold | SQL Server (T-SQL) — `DW_BrechaDigital` | 2019+ |
| Dashboard | Streamlit | 1.32+ |
| Gráficos | Plotly | 5.20+ |
| Asistente IA | Google Gemini API | 0.5+ |
| Datos Macroeconómicos | CEPALSTAT REST API | — |
| Datos de Empleo | Adzuna REST API | — |
| Conectividad BD | PyODBC + SQLAlchemy | 5.0+ / 2.0+ |
| Entorno | python-dotenv | 1.0+ |

---

## Arquitectura

El proyecto sigue una arquitectura medallón **Bronze → Silver → Gold**:

```
SQL Server BrechaDigitalDB    API CEPALSTAT       Adzuna API
    [Bronze — Fuente]       [Datos Macro]    [Vacantes Laborales]
            │                     │                   │
            └─────────────────────┴───────────────────┘
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
                 [Gold — Esquema Copo de Nieve T-SQL]
                 Fact_InsercionLaboral · tablas DIM_*
                                  │
                       src/dashboard/ (Streamlit)
                  KPIs · Inserción Laboral · Skill Gap · Chatbot
```

---

## Pipeline de Datos

| Paso | Módulo | Entrada | Salida |
|---|---|---|---|
| 1. Extracción | `src/ingestion/sqlserver.py` | `BrechaDigitalDB` (SQL Server) | `data/raw/*.csv` |
| 2. Extracción | `src/ingestion/cepalstat.py` | CEPALSTAT REST API | `data/raw/cepalstat/*.csv` |
| 3. Extracción | `src/ingestion/empleos.py` | Adzuna REST API | `data/raw/empleos/*.csv` |
| 4. Limpieza | `src/transform/clean.py` | `data/raw/*.csv` | `data/processed/*.csv` |
| 5. Normalización | `src/transform/normalize.py` | `data/processed/*.csv` | `data/processed/*.csv` |
| 6. Carga Dimensiones | `src/schema/dimensions.py` | `data/processed/*.csv` | `DW_BrechaDigital` — tablas DIM_* |
| 7. Carga Hechos | `src/schema/facts.py` | `data/processed/*.csv` | `DW_BrechaDigital` — Fact_InsercionLaboral |

---

## Esquema Copo de Nieve

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

Documentación completa del esquema: [`docs/esquema_copo_nieve.md`](docs/esquema_copo_nieve.md)

---

## Cronograma de Sprints

| Día | Fecha | Fase | Capa |
|---|---|---|---|
| Día 1 | Setup | Definición, setup GitHub, extracción Bronze | Bronze |
| Día 2 | 1 de abril | Limpieza, transformación e integración | Silver |
| Día 3 | 2 de abril | Modelado estrella + construcción del Dashboard | Gold + Viz |
| Día 4 | 6 de abril | Pruebas finales, storytelling y documentación | Todas |
| Día 5 | 7 de abril | **DEMO DAY** — presentación final de 10 minutos | — |

El avance se registra en el [Tablero Kanban de GitHub](../../projects).

---

## Equipo y Forma de Trabajo

Todos los integrantes contribuyen en todas las fases del proyecto. Cada persona indicada abajo es el **lead** de su fase — responsable de gestionar, revisar y garantizar la calidad de esa capa.

| Integrante | Fase Lead | GitHub |
|---|---|---|
| Abraham Flores Barrionuevo | Bronze — Ingesta de Datos | [@AFB-9898](https://github.com/AFB-9898) |
| Juan Nicolás Flores Delgado | Silver — Transformación | [@Juan7139nf](https://github.com/Juan7139nf) |
| Micaela Pérez Vásquez | Gold — Diseño del Esquema | — |
| Mayra Villca Méndez | Análisis y KPIs — Notebooks | [@MayVillca](https://github.com/MayVillca) |
| Diego Vargas Urzagaste | Dashboard e Integración | [@temps-code](https://github.com/temps-code) |

---

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/temps-code/brecha-digital-bi.git
   cd brecha-digital-bi
   ```

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux / macOS
   .venv\Scripts\activate           # Windows
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno (ver [Variables de Entorno](#variables-de-entorno)).

5. Poblar la base de datos Bronze — ejecutar `database/seed.sql` en SQL Server Management Studio (SSMS).

6. Ejecutar el pipeline completo:

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

## Variables de Entorno

Crear un archivo `.env` en el directorio raíz:

```env
# SQL Server — Base de Datos Bronze
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=BrechaDigitalDB
DB_USER=sa
DB_PASSWORD=tu_contraseña

# SQL Server — Warehouse Gold
DW_SERVER=localhost\SQLEXPRESS
DW_NAME=DW_BrechaDigital
DW_USER=sa
DW_PASSWORD=tu_contraseña

# Gemini API
GEMINI_API_KEY=tu_api_key_de_gemini

# CEPALSTAT (no requiere clave — API pública)
CEPALSTAT_BASE_URL=https://api-cepalstat.cepal.org/cepalstat/api/v1

# Adzuna Employment API
ADZUNA_APP_ID=tu_app_id
ADZUNA_APP_KEY=tu_app_key
```

> Nunca commitear el archivo `.env`. Ya está incluido en el `.gitignore`.

---

## Ejecutar el Dashboard

```bash
streamlit run src/dashboard/app.py
```

El dashboard estará disponible en `http://localhost:8501`.

| Página | Descripción |
|---|---|
| KPIs | Indicadores generales de empleabilidad y deserción |
| Inserción Laboral | Tasa de inserción por carrera y región |
| Skill Gap | Comparación entre habilidades académicas y demanda del mercado |
| Asistente IA | Consultas en lenguaje natural con Gemini API |

---

<div align="center">
<img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
</div>
