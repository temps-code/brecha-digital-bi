<div align="center">

<h1>Brecha Digital Laboral — Estrategia BI</h1>

<p><strong>Pipeline de Business Intelligence que conecta datos académicos con demanda real del mercado laboral para medir y reducir la brecha digital en la educación técnica superior boliviana.</strong></p>

<p>
  <a href="https://brecha-digital-bolivia-bi.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/Demo_en_Vivo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Demo en Vivo">
  </a>
  &nbsp;
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/Licencia-MIT-blue.svg?style=for-the-badge" alt="Licencia: MIT">
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

📄 Leer en: [English](README.md) | **Español**

---

**Proyecto Académico**  
Universidad Privada Domingo Savio — Ingeniería de Sistemas  
Materia: Inteligencia de Negocios — 2026

---

## Tabla de Contenidos

- [Demo en Vivo](#demo-en-vivo)
- [Propósito y Resultados](#propósito-y-resultados)
- [Qué Hace](#qué-hace)
- [Páginas del Dashboard](#páginas-del-dashboard)
- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Pipeline de Datos](#pipeline-de-datos)
- [Diagramas ER de las Bases de Datos](#diagramas-er-de-las-bases-de-datos)
- [Esquema Copo de Nieve](#esquema-copo-de-nieve)
- [Equipo](#equipo)
- [Instalación](#instalación)
- [Variables de Entorno](#variables-de-entorno)
- [Despliegue en Streamlit Cloud](#despliegue-en-streamlit-cloud)

---

## Propósito y Resultados

**Objetivo:** Construir un sistema BI que haga visible y medible la brecha de habilidades digitales en la educación IT boliviana — dándole a los directores académicos una herramienta basada en evidencia para alinear los planes de estudio con la demanda real del mercado laboral, contribuyendo directamente al ODS 4 (Educación de Calidad) y ODS 8 (Trabajo Decente).

**¿Se cumplió?**

| Objetivo | Resultado |
|----------|-----------|
| Pipeline de datos de punta a punta (Bronze → Silver → Gold) | Implementado y operacional |
| 4+ KPIs calculados con datos reales | 9 KPIs en 4 páginas del dashboard |
| Brecha de habilidades identificada entre academia y mercado | Medida en las 5 carreras IT con fuzzy matching |
| Benchmark regional contra América Latina | 17 países via CEPALSTAT ODS 4.4.1 |
| Asistente IA para consultas en lenguaje natural | En vivo via API de Groq (LLaMA 3.1 8B) |
| Despliegue público accesible para evaluadores | Desplegado en `brecha-digital-bolivia-bi.streamlit.app` |

**Hallazgo concreto:** El análisis de brecha — usando vacantes reales extraídas por LLM — muestra que las habilidades más demandadas (Docker, plataformas cloud, frameworks modernos de CI/CD) tienen cobertura académica significativamente baja en las 5 carreras IT analizadas. Esto confirma la hipótesis de que la brecha digital es real y medible — exactamente el tipo de evidencia que puede impulsar una reforma curricular.

---

## Demo en Vivo

**[brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/)**

La aplicación está desplegada en Streamlit Cloud y se conecta en tiempo real a la API de Groq para el asistente IA. Usa archivos CSV pre-procesados para los datos académicos y del mercado laboral.

---

## Qué Hace

Las instituciones de educación técnica en Bolivia generan grandes volúmenes de datos académicos pero no tienen las herramientas para conectarlos con la demanda real del mercado laboral. Este proyecto construye ese puente.

**Antes:** Decisiones basadas en intuición, silos de datos fragmentados, sin visibilidad sobre la empleabilidad de los egresados.

**Después:** Un pipeline BI unificado que integra registros académicos internos con datos externos del mercado laboral, exponiendo KPIs accionables a través de un dashboard interactivo accesible para cualquier director académico.

**Capacidades principales:**

- **Pipeline ELT de punta a punta:** SQL Server (Bronze) → transformación Python (Silver) → almacén en esquema copo de nieve (Gold)
- **Análisis enfocado en IT:** Cubre exclusivamente 5 carreras — Ingeniería de Software, Ingeniería de Sistemas, Ciencia de Datos, Telecomunicaciones y Ciberseguridad
- **Inteligencia del mercado laboral:** Datos reales de vacantes desde la API de Adzuna (EE.UU., España, México, Brasil) con extracción de habilidades mediante LLM de Groq
- **Monitoreo de KPIs:** Tasa de empleabilidad, predicción de deserción, análisis de brecha de habilidades, benchmarking salarial
- **Benchmark regional:** Indicador ODS 4.4.1 de CEPALSTAT — competencias digitales en 17 países de América Latina
- **Asistente IA:** Consultas en lenguaje natural sobre el dataset completo, impulsado por LLaMA 3.1 (API de Groq)

---

## Páginas del Dashboard

| Página | URL | Descripción |
|---|---|---|
| Inicio | `/` | KPIs principales, navegación, fuentes de datos |
| KPIs | `/kpis` | Tasa de empleo, gauge de deserción, benchmark CEPALSTAT regional |
| Inserción Laboral | `/insercion` | Tasa de inserción por carrera, distribución salarial, tendencias temporales, mapa de calor por ciudad |
| Brecha de Habilidades | `/skill_gap` | Habilidades del mercado vs currículo académico, análisis de cobertura, habilidades extraídas con LLM |
| Asistente IA | `/chatbot` | Consultas BI en lenguaje natural — LLaMA 3.1 8B via API de Groq |

---

## Arquitectura

```
SQL Server BrechaDigitalDB      API CEPALSTAT         API Adzuna
      [Bronze — Fuente]          [Macro Data]      [Datos de Empleo]
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
              LLM Groq → skills_extracted.csv     facts.py · dimensions.py
                         │                         │
                         └────────────┬────────────┘
                                      │
                        SQL Server DW_BrechaDigital
                      [Gold — Esquema Copo de Nieve T-SQL]
                       Fact_InsercionLaboral · Tablas DIM_*
                                      │
                             src/dashboard/ (Streamlit)
               KPIs · Inserción Laboral · Skill Gap · Chatbot IA
```

---

## Stack Tecnológico

| Categoría | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.11+ |
| Procesamiento de Datos | Pandas | 2.0+ |
| Base de Datos Bronze | SQL Server (T-SQL) — `BrechaDigitalDB` | 2019+ |
| Almacén Gold | SQL Server (T-SQL) — `DW_BrechaDigital` | 2019+ |
| Dashboard | Streamlit | 1.32+ |
| Gráficos | Plotly | 5.20+ |
| Extracción de Skills con IA | API de Groq (LLaMA 3.1 8B) | 0.9+ |
| Asistente IA | API de Groq (LLaMA 3.1 8B Instant) | 0.9+ |
| Datos Macroeconómicos | API REST de CEPALSTAT | — |
| Datos de Empleo | API REST de Adzuna | — |
| Conectividad BD | PyODBC + SQLAlchemy | 5.0+ / 2.0+ |
| Variables de Entorno | python-dotenv | 1.0+ |

---

## Pipeline de Datos

| Paso | Módulo | Entrada | Salida |
|---|---|---|---|
| 1. Extracción Académica | `src/ingestion/sqlserver.py` | `BrechaDigitalDB` (SQL Server) | `data/raw/*.csv` |
| 2. Extracción Macro | `src/ingestion/cepalstat.py` | API REST de CEPALSTAT | `data/raw/cepalstat/*.csv` |
| 3. Extracción de Empleos | `src/ingestion/empleos.py` | API de Adzuna | `data/raw/empleos/*.csv` |
| 4. Extracción de Habilidades | `src/ingestion/skill_extraction.py` | Descripciones de vacantes Adzuna | `data/processed/empleos/skills_extracted.csv` |
| 5. Limpieza | `src/transform/clean.py` | `data/raw/*.csv` | `data/processed/*.csv` |
| 6. Normalización | `src/transform/normalize.py` | `data/processed/*.csv` | `data/processed/*.csv` |
| 7. Carga de Dimensiones | `src/schema/dimensions.py` | `data/processed/*.csv` | `DW_BrechaDigital` — tablas DIM_* |
| 8. Carga de Hechos | `src/schema/facts.py` | `data/processed/*.csv` | `DW_BrechaDigital` — Fact_InsercionLaboral |

### Pipeline de Extracción de Habilidades con IA

Las descripciones de vacantes de Adzuna son procesadas por `skill_extraction.py` en dos etapas:

1. **LLM de Groq (primario):** Envía descripciones crudas a `llama-3.1-8b-instant` y extrae listas de habilidades estructuradas en formato JSON
2. **Fallback con regex:** Si el LLM falla o alcanza el límite de tasa, un banco de patrones regex cubre los keywords tecnológicos más comunes

El `skills_extracted.csv` resultante está commiteado al repositorio para reproducibilidad y para evitar costos de LLM en cada carga del dashboard.

---

## Diagramas ER de las Bases de Datos

### Bronze — `BrechaDigitalDB` (Base de datos fuente)

Base de datos operacional con registros académicos crudos. Modelo relacional normalizado.

```
┌─────────────────┐         ┌──────────────────────┐
│    Carreras     │         │  CompetenciasDigitales│
├─────────────────┤         ├──────────────────────┤
│ PK CarreraID    │◄────────│ FK CarreraID          │
│    NombreCarrera│         │ PK CompetenciaID      │
│    Facultad     │         │    NombreHabilidad    │
└────────┬────────┘         │    NivelRequerido     │
         │                  └──────────────────────┘
         │
         │   ┌──────────────────┐
         │   │   Estudiantes    │
         │   ├──────────────────┤
         └──►│ PK EstudianteID  │
             │    Nombre        │◄──────────────┐
             │    FechaIngreso  │               │
             │    Genero        │               │
             │    Ciudad        │               │
             └──────────────────┘               │
                                                │
┌──────────────────────────┐    ┌───────────────┴──────────┐
│     Inscripciones        │    │   SeguimientoEgresados   │
├──────────────────────────┤    ├──────────────────────────┤
│ PK InscripcionID         │    │ PK EgresadoID            │
│ FK EstudianteID ─────────┼───►│ FK EstudianteID          │
│ FK CarreraID    ─────────┼───►│    TieneEmpleoFormal     │
│    NotaFinal             │    │    SalarioMensualUSD     │
│    SemestreActual        │    │    TrabajaEnAreaDeEstudio│
└──────────────────────────┘    └──────────────────────────┘
```

**5 tablas — 4 relaciones de clave foránea**  
`SeguimientoEgresados` es la tabla clave: registra si cada estudiante obtuvo empleo formal post-egreso y si trabaja en su área de estudio.

---

### Gold — `DW_BrechaDigital` (Almacén en Esquema Copo de Nieve)

Almacén analítico optimizado para consultas BI. Cada fila en la tabla de hechos es el evento de empleo de un egresado.

```
                    ┌───────────────────┐
                    │   DIM_CARRERA     │
                    ├───────────────────┤
                    │ PK SK_Carrera     │
                    │    CarreraID (BK) │
                    │    nombrecarrera  │
                    │    area           │
                    └────────┬──────────┘
                             │
┌──────────────────┐         │         ┌──────────────────────┐
│  DIM_ESTUDIANTE  │         │         │    DIM_HABILIDAD      │
├──────────────────┤         │         ├──────────────────────┤
│ PK SK_Estudiante │         │         │ PK SK_Habilidad       │
│    EstudianteID  │         │         │    NombreHabilidad    │
│    nombre        │         │         │ FK SK_Categoria ──►┐  │
│    Genero        │         │         └──────────┬──────────┘  │
│    ciudad_       │         │                    │              │
│    residencia    │         │         ┌──────────▼──────────┐  │
└────────┬─────────┘         │         │ DIM_CATEGORIA_SKILL │  │
         │                   │         ├─────────────────────┤  │
         │         ┌─────────▼──────────────────────────┐    │  │
         └────────►│       FACT_INSERCION_LABORAL        │    │  │
                   ├────────────────────────────────────┤    │  │
                   │ FK SK_Estudiante                    │    │  │
                   │ FK SK_Carrera                       │    │  │
                   │ FK SK_Tiempo                        │    │  │
                   │ FK SK_Region                        │    │  │
                   │ FK SK_MercadoLaboral                │    │  │
                   │    EstaEmpleado         (INT)       │    │  │
                   │    SalarioMensualUSD    (DECIMAL)   │    │  │
                   │    TrabajaEnAreaEstudio (BIT)       │    │  │
                   └──────┬──────────────┬───────────────┘    │  │
                          │              │          SK_Categoria│  │
                          ▼              ▼          PK──────────┘  │
              ┌───────────────┐  ┌──────────────────────┐         │
              │  DIM_TIEMPO   │  │  DIM_MERCADO_LABORAL  │         │
              ├───────────────┤  ├──────────────────────┤         │
              │ PK SK_Tiempo  │  │ PK SK_MercadoLaboral  │         │
              │    anio       │  │    Ubicacion          │         │
              │    trimestre  │  │ FK SK_Region ──►┐     │         │
              │    mes        │  └──────────────────┼─────┘         │
              │    Semestre   │                     │                │
              └───────────────┘          ┌──────────▼────────┐      │
                                         │    DIM_REGION     │      │
                                         ├───────────────────┤      │
                                         │ PK SK_Region      │      │
                                         │    Ciudad         │      │
                                         │    Region         │      │
                                         └───────────────────┘      │
                                                                     │
                              NombreCategoria ◄─────────────────────┘
                              Básico / Intermedio / Avanzado
```

**8 tablas — 1 fact + 7 dimensiones (2 sub-dimensiones)**  
El copo de nieve normaliza `DIM_HABILIDAD → DIM_CATEGORIA_SKILL` y `DIM_MERCADO_LABORAL → DIM_REGION` para eliminar redundancia de datos.

---

## Esquema Copo de Nieve

Modelo normalizado elegido sobre esquema estrella por corrección técnica. Las sub-dimensiones reducen redundancia y mejoran la integridad referencial a costa de JOINs adicionales.

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

Documentación completa: [`docs/esquema_copo_nieve.md`](docs/esquema_copo_nieve.md)

---

## Equipo

| Integrante | Rol | GitHub |
|---|---|---|
| Abraham Flores Barrionuevo | Lead Bronze — Ingesta de Datos | [@AFB-9898](https://github.com/AFB-9898) |
| Juan Nicolás Flores Delgado | Lead Silver — Transformación | [@Juan7139nf](https://github.com/Juan7139nf) |
| Micaela Pérez Vásquez | Lead Gold — Diseño del Esquema | [@Sam24p](https://github.com/Sam24p) |
| Mayra Villca Méndez | Lead Análisis — Notebooks y KPIs | [@MayVillca](https://github.com/MayVillca) |
| Diego Vargas Urzagaste | Lead Dashboard — Integración y Despliegue | [@temps-code](https://github.com/temps-code) |

Progreso en el [Tablero Kanban de GitHub](https://github.com/users/temps-code/projects/3).

---

## Instalación

```bash
# 1. Clonar
git clone https://github.com/temps-code/brecha-digital-bi.git
cd brecha-digital-bi

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (ver abajo)

# 5. Cargar la base de datos Bronze
#    Ejecutar database/seed.sql en SQL Server Management Studio

# 6. Ejecutar el pipeline completo (un solo comando)
python -m src.run_pipeline

# Opcional: omitir ingesta si los CSVs raw ya existen
python -m src.run_pipeline --skip-ingestion
```

El orquestador (`src/run_pipeline.py`) ejecuta las 4 etapas en orden:

| Etapa | Qué hace |
|-------|----------|
| **1 — Ingestion** | Extrae desde SQL Server + API Adzuna + API CEPALSTAT + extracción de skills con LLM |
| **2 — Clean** | Limpia y valida todos los CSVs raw |
| **3 — Normalize** | Estandariza ciudades, carreras, fechas; crea vista unificada |
| **4 — Schema** | Carga dimensiones y tabla de hechos en `DW_BrechaDigital` |

---

## Variables de Entorno

Copiá `.env.example` y completá tus valores:

```bash
cp .env.example .env
```

```env
# SQL Server — Fuente Bronze
DB_SERVER=localhost,1433
DB_NAME=BrechaDigitalDB
DB_USER=sa
DB_PASSWORD=tu_contraseña

# SQL Server — Almacén Gold
DW_SERVER=localhost,1433
DW_NAME=DW_BrechaDigital
DW_USER=sa
DW_PASSWORD=tu_contraseña

# API de Groq — asistente IA + extracción de habilidades con LLM
GROQ_API_KEY=tu_clave_groq

# CEPALSTAT (API pública — sin clave requerida)
CEPALSTAT_BASE_URL=https://api-cepalstat.cepal.org/cepalstat/api/v1

# API de Empleo Adzuna
ADZUNA_APP_ID=tu_app_id
ADZUNA_APP_KEY=tu_app_key
```

> El archivo `.env` ya está en `.gitignore`. Nunca lo commitees.  
> El pipeline detecta el modo de autenticación automáticamente: SQL Auth si hay credenciales, Windows Auth en caso contrario.

---

## Despliegue en Streamlit Cloud

La aplicación está desplegada en **[brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/)**.

Para tu propio despliegue:

1. Hacer fork o push a GitHub
2. Conectar el repositorio en [share.streamlit.io](https://share.streamlit.io)
3. Configurar **Main file path** en `src/dashboard/app.py`
4. Agregar secrets en **Settings → Secrets** (formato TOML):

```toml
GROQ_API_KEY = "gsk_tu_clave_aqui"
ADZUNA_APP_ID = "tu_id"
ADZUNA_APP_KEY = "tu_clave"
DB_SERVER = "tu_servidor"
DB_NAME = "BrechaDigitalDB"
DB_USER = "tu_usuario"
DB_PASSWORD = "tu_contraseña"
DW_SERVER = "tu_servidor"
DW_NAME = "DW_BrechaDigital"
DW_USER = "tu_usuario"
DW_PASSWORD = "tu_contraseña"
```

> Sin acceso a SQL Server, el dashboard cae automáticamente a los CSVs pre-procesados en `data/processed/` — sin pérdida de funcionalidad en la versión desplegada.

---

<a href="LICENSE">
  <img src="https://img.shields.io/badge/Licencia-MIT-blue.svg?style=for-the-badge" alt="Licencia: MIT">
</a>
&nbsp;
<a href="https://brecha-digital-bolivia-bi.streamlit.app/">
  <img src="https://img.shields.io/badge/▶_Abrir_Demo_en_Vivo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Abrir Demo en Vivo">
</a>
