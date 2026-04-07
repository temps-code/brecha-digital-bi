# Guía del Proyecto — Brecha Digital BI

**Para:** Todo el equipo y evaluadores  
**Proyecto:** Estrategia para la Reducción de la Brecha Digital en la Educación Técnica Superior  
**Materia:** Inteligencia de Negocios — UPDS 2026  
**Demo en vivo:** [brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/)  
**Versión:** 3.0 — Estado final desplegado

---

## Índice

1. [El problema real](#1-el-problema-real)
2. [Propósito del proyecto y si se cumplió](#2-propósito-del-proyecto-y-si-se-cumplió)
3. [Por qué este proyecto es útil](#3-por-qué-este-proyecto-es-útil)
4. [Qué es Business Intelligence (BI)](#4-qué-es-business-intelligence-bi)
5. [Arquitectura del sistema](#5-arquitectura-del-sistema)
6. [Capa Bronze — Fuentes de datos](#6-capa-bronze--fuentes-de-datos)
7. [Capa Silver — Transformación y limpieza](#7-capa-silver--transformación-y-limpieza)
8. [Capa Gold — Almacén de datos y diagramas ER](#8-capa-gold--almacén-de-datos-y-diagramas-er)
9. [Extracción de habilidades con IA](#9-extracción-de-habilidades-con-ia)
10. [El dashboard — Guía de cada página](#10-el-dashboard--guía-de-cada-página)
11. [OKRs y métricas de éxito](#11-okrs-y-métricas-de-éxito)
12. [Alineación con los ODS](#12-alineación-con-los-ods)
13. [Despliegue en Streamlit Cloud](#13-despliegue-en-streamlit-cloud)
14. [Responsabilidades del equipo](#14-responsabilidades-del-equipo)
15. [Comandos rápidos](#15-comandos-rápidos)
16. [Glosario](#16-glosario)

---

## 1. El problema real

Bolivia tiene un problema concreto y medible: la educación técnica superior en IT **no está alineada con lo que pide el mercado laboral**.

Las instituciones forman profesionales en tecnología, pero nadie mide con precisión si esos egresados consiguen trabajo en su área, qué habilidades les faltan, o cómo se compara Bolivia con el resto de la región en competencias digitales. Los datos existen — están guardados en SQL Server — pero sin un sistema que los analice, son inútiles.

El mercado laboral tecnológico, mientras tanto, evoluciona rápido. Python, Docker, SQL, cloud computing — estas habilidades ya no son opcionales. Si la academia no las incorpora, los egresados entran al mercado con una brecha formativa real que afecta su empleabilidad y sus salarios.

**Consecuencias concretas de no medir esto:**
- Planes de estudio desactualizados que no reflejan la demanda real
- Egresados con habilidades obsoletas o incompletas
- Decisiones académicas basadas en intuición en lugar de datos
- Imposibilidad de demostrar el impacto de las carreras IT ante organismos de acreditación

---

## 2. Propósito del proyecto y si se cumplió

### Propósito

El propósito central del proyecto es **transformar datos académicos y laborales dispersos en inteligencia accionable** para reducir la brecha digital en la educación técnica superior boliviana.

En términos concretos: construir un sistema que permita responder, con datos reales, la pregunta *"¿nuestros egresados de IT están preparados para el mercado laboral?"* — y si la respuesta es no, identificar exactamente qué falta.

Esto se alinea directamente con:
- **ODS 4, Meta 4.4:** Aumentar el número de jóvenes con competencias técnicas para el empleo
- **ODS 8, Meta 8.6:** Reducir la proporción de jóvenes sin empleo y sin formación adecuada

El sistema no es una propuesta teórica — está **desplegado y funcionando** en [brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/).

---

### ¿Se cumplió el propósito?

**Sí. Con evidencia verificable.**

A continuación, cada objetivo con el resultado real obtenido y la justificación de por qué se considera cumplido:

#### Pipeline de datos de punta a punta

**Objetivo:** Implementar las tres capas (Bronze → Silver → Gold) con datos reales fluyendo sin errores.

**Resultado:** ✅ Cumplido.
- **Bronze:** Extracción desde SQL Server (`BrechaDigitalDB`) + API de Adzuna + API de CEPALSTAT. Archivos CSV en `data/raw/`.
- **Silver:** Limpieza y normalización de nombres de carreras, ciudades, fechas y salarios. Archivos en `data/processed/`.
- **Gold:** `DW_BrechaDigital` en SQL Server con esquema copo de nieve: tabla `FACT_INSERCION_LABORAL` + 7 dimensiones cargadas con datos reales.

**Justificación:** El dashboard carga y muestra datos reales. Si cualquiera de las tres capas hubiera fallado, el dashboard mostraría errores o valores en cero. No es el caso.

---

#### Insights accionables sobre la brecha digital

**Objetivo:** El dashboard debe exponer al menos 4 KPIs calculados con datos reales, identificar al menos 3 habilidades con brecha y cubrir al menos 2 ciudades.

**Resultado:** ✅ Superado.

| Métrica objetivo | Resultado real |
|-----------------|----------------|
| 4+ KPIs | **9 KPIs** en 4 páginas del dashboard |
| 3+ habilidades con brecha | **Múltiples brechas identificadas** — Docker, cloud platforms, CI/CD moderno entre las más críticas |
| 2+ ciudades analizadas | **La Paz, Cochabamba, Santa Cruz** + análisis por sede |
| Benchmark regional | **17 países** de América Latina via CEPALSTAT |

**Hallazgo principal confirmado:** El análisis de skill gap muestra que las habilidades más demandadas en vacantes IT reales (extraídas por LLM de Adzuna) tienen cobertura académica significativamente baja. Esto valida empíricamente que la brecha digital existe y es medible — no es solo una intuición.

**Por qué esto importa:** Un director académico puede abrir el dashboard ahora mismo, ver que Docker tiene baja cobertura y alta demanda, y tener una justificación basada en datos para proponer un cambio curricular. Eso es exactamente el valor que el proyecto prometió entregar.

---

#### Dominio de metodología BI

**Objetivo:** Las 4 secciones del dashboard funcionando, cada integrante puede explicar su capa, informe documenta decisiones técnicas.

**Resultado:** ✅ Cumplido.
- Las 4 páginas del dashboard están operativas y desplegadas públicamente
- Este documento es el informe técnico que documenta todas las decisiones (esquema elegido, fuentes, metodología de fuzzy matching, pipeline de extracción con LLM)
- El proyecto va más allá del scope original: despliegue en cloud, extracción con LLM, benchmark con drill-down por año y país

---

### Lo que el proyecto demuestra

1. **La brecha es real:** Las vacantes IT piden habilidades específicas que el currículo boliviano no cubre completamente. No es opinión — es dato.

2. **La medición es posible:** Con datos académicos internos + APIs públicas, se puede construir un sistema BI funcional que mide esta brecha con precisión.

3. **La solución es escalable:** El sistema tiene fallback automático (CSV cuando SQL Server no está disponible), está desplegado en cloud, y puede actualizarse re-ejecutando el pipeline.

4. **La tecnología es accesible:** Todo el stack es open source o free tier (Groq API, Adzuna API, CEPALSTAT, Streamlit Cloud).

---

## 3. Por qué este proyecto es útil

> Esta sección está pensada para evaluadores y directores académicos sin conocimiento técnico.

Este dashboard no es un ejercicio académico decorativo. Responde preguntas que un director académico necesita responder HOY:

| Pregunta | Dónde se responde |
|----------|-------------------|
| ¿Qué porcentaje de nuestros egresados trabaja en IT? | Página KPIs — Tasa de Empleo Formal |
| ¿Cuántos trabajan en su área de estudio? | Página KPIs — Empleados en su Área |
| ¿Cuánto ganan nuestros egresados? | Página Inserción — Distribución Salarial |
| ¿Cuáles carreras tienen mejor inserción? | Página Inserción — Empleo por Carrera |
| ¿En qué ciudades hay más demanda de IT? | Página Inserción — Mapa de Calor por Ciudad |
| ¿Qué habilidades pide el mercado que no enseñamos? | Página Skill Gap — Brecha de Habilidades |
| ¿Cuánto estamos cubriendo de lo que el mercado necesita? | Página Skill Gap — Cobertura Académica % |
| ¿Cómo se compara Bolivia con Argentina, Chile, Brasil en TIC? | Página KPIs — Benchmark CEPALSTAT |
| ¿Cuántos estudiantes están en riesgo de desertar? | Página KPIs — Gauge de Deserción |

Además, el **Asistente IA** permite hacer preguntas en lenguaje natural sin necesidad de saber nada de SQL ni programación — cualquier persona del equipo directivo puede usarlo.

**El valor demostrable:** Un dashboard que integra datos internos (SQL Server), datos de mercado laboral real (Adzuna API), indicadores internacionales (CEPALSTAT) y análisis con LLM — todo en un solo lugar, actualizable, y desplegado públicamente.

---

## 4. Qué es Business Intelligence (BI)

BI es el proceso de convertir datos crudos en información útil para tomar decisiones. No es solo hacer gráficos bonitos — es construir todo el sistema que hace que esos gráficos sean confiables, actualizados y significativos.

La arquitectura clásica de BI tiene tres capas bien definidas:

```
Fuentes de datos        Procesamiento            Consumo
(datos crudos)   →   (limpieza + modelado)  →   (dashboard + análisis)
  [Bronze]                [Silver]                   [Gold + Viz]
```

**Por qué las capas importan:** Si los datos de Bronze están mal extraídos, todo lo que viene después está contaminado. Si Silver no limpió correctamente, los KPIs del dashboard van a ser incorrectos. La arquitectura medallón garantiza que cada capa tenga responsabilidades claras y auditables.

---

## 5. Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FUENTES EXTERNAS                         │
│                                                                 │
│  SQL Server BrechaDigitalDB   CEPALSTAT API    Adzuna API       │
│  (estudiantes, egresados,     (indicador       (vacantes IT     │
│   inscripciones, carreras)     ODS 4.4.1)       Bolivia+intl)   │
└────────────────┬───────────────────┬───────────────┬────────────┘
                 │                   │               │
                 ▼                   ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA BRONZE — data/raw/                     │
│                                                                 │
│  src/ingestion/sqlserver.py   src/ingestion/cepalstat.py        │
│  src/ingestion/empleos.py                                       │
│                                                                 │
│  → estudiantes_raw.csv  · inscripciones_raw.csv                 │
│  → egresados_raw.csv    · carreras_raw.csv                      │
│  → vacantes_tecnologicas.csv · cepalstat_tic.csv                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAPA SILVER — data/processed/                  │
│                                                                 │
│  src/transform/clean.py   src/transform/normalize.py            │
│                                                                 │
│  → estudiantes_cleaned.csv      · egresados_cleaned.csv         │
│  → vacantes_tecnologicas_cleaned.csv · cepalstat_cleaned.csv    │
│                                                                 │
│  + src/ingestion/skill_extraction.py (Groq LLM)                 │
│  → skills_extracted.csv  (habilidades estructuradas desde LLM)  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA GOLD — SQL Server DW_BrechaDigital            │
│                                                                 │
│  src/schema/dimensions.py   src/schema/facts.py                 │
│                                                                 │
│  DIM_ESTUDIANTE · DIM_CARRERA · DIM_REGION · DIM_TIEMPO         │
│  DIM_HABILIDAD · DIM_CATEGORIA_SKILL · DIM_MERCADO_LABORAL      │
│  FACT_INSERCION_LABORAL                                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              DASHBOARD — src/dashboard/ (Streamlit)             │
│                                                                 │
│  app.py (Inicio) · 01_kpis.py · 02_insercion.py                 │
│  03_skill_gap.py · 04_chatbot.py                                │
│                                                                 │
│  Desplegado en: brecha-digital-bolivia-bi.streamlit.app         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Capa Bronze — Fuentes de datos

**Responsable:** Abraham Flores  
**Principio:** los datos se extraen SIN modificar. Si hay errores, valores raros o nombres mal escritos, se dejan como están. La capa Bronze es una copia fiel de la fuente.

### 6.1 Base de datos académica (SQL Server)

Fuente: `BrechaDigitalDB` en SQL Server.

Tablas extraídas:
- `Estudiantes` — datos personales, carrera, ciudad, año de ingreso
- `Inscripciones` — historial de materias, semestre actual, nota final
- `Egresados` — estado de egreso, año de graduación, empleo registrado
- `Carreras` — catálogo de programas académicos

```bash
python src/ingestion/sqlserver.py
# Salida: data/raw/estudiantes_raw.csv, inscripciones_raw.csv, etc.
```

### 6.2 Vacantes laborales (Adzuna API)

Fuente: [Adzuna API](https://developer.adzuna.com/) — buscador de empleo con cobertura internacional.

El script consulta vacantes del sector tecnológico en EE.UU., España, México y Brasil, evaluando oportunidades remotas relevantes para egresados bolivianos. Captura: título, descripción completa, salario (cuando disponible), ciudad y país.

```bash
python src/ingestion/empleos.py
# Salida: data/raw/empleos/vacantes_tecnologicas.csv
```

### 6.3 Indicadores regionales (CEPALSTAT API)

Fuente: [CEPALSTAT](https://estadisticas.cepal.org/cepalstat/) — base estadística oficial de la CEPAL.

Se extrae el indicador **ODS 4.4.1** (Proporción de jóvenes y adultos con competencias en TIC) para 17 países de América Latina. Permite comparar Bolivia con el resto de la región.

```bash
python src/ingestion/cepalstat.py
# Salida: data/raw/cepalstat/indicadores_tic_region.csv
```

---

## 7. Capa Silver — Transformación y limpieza

**Responsable:** Juan Nicolás Flores  
**Principio:** datos limpios, estandarizados y listos para análisis. Un dato sucio en Silver contamina todo lo que viene después.

### Qué se hace

- **Normalización de carreras:** Se mapean todas las variantes al nombre canónico de cada una de las 5 carreras IT (`Ingeniería de Sistemas`, `Ingeniería de Software`, `Ciencia de Datos`, `Telecomunicaciones`, `Ciberseguridad`). Carreras no IT son descartadas en este paso.
- **Estandarización de ciudades:** Se unifican variantes (ej: `Cbba`, `Cochabamba`, `CBBA` → `Cochabamba`)
- **Formatos de fechas:** Todo a `YYYY-MM-DD`
- **Salarios:** Extracción y normalización a USD donde corresponde
- **Eliminación de duplicados** y registros incompletos

```bash
python src/transform/clean.py
python src/transform/normalize.py
# Salida: data/processed/*.csv
```

---

## 8. Capa Gold — Almacén de datos y diagramas ER

**Responsable:** Micaela Pérez  
**Principio:** el modelo de datos Gold está diseñado para responder preguntas de negocio de manera eficiente, no para almacenar datos crudos.

### Por qué esquema copo de nieve y no estrella

El **esquema estrella** es más simple: una tabla de hechos central rodeada de dimensiones planas. Pero en este proyecto, hay entidades que tienen sub-jerarquías naturales (las habilidades tienen categorías, el mercado laboral tiene región). El **esquema copo de nieve** normaliza esas jerarquías en tablas separadas, reduciendo redundancia y mejorando la integridad referencial.

El costo: más JOINs en las consultas. El beneficio: datos más limpios y correctos.

```
FACT_INSERCION_LABORAL (tabla central)
  ├── DIM_ESTUDIANTE (egresado)
  ├── DIM_CARRERA (programa académico)
  ├── DIM_TIEMPO (año/semestre de egreso)
  ├── DIM_HABILIDAD → DIM_CATEGORIA_SKILL (brecha de skills)
  └── DIM_MERCADO_LABORAL → DIM_REGION (vacante y su origen)
```

Cada fila de `FACT_INSERCION_LABORAL` representa un evento: un egresado en un momento del tiempo, con o sin empleo formal, con o sin alineación a su área de estudio.

Documentación completa del esquema: [`docs/esquema_copo_nieve.md`](esquema_copo_nieve.md)

---

### Diagrama ER — Bronze (`BrechaDigitalDB`)

Base de datos operacional con los registros académicos originales. Modelo relacional de 5 tablas.

```
┌─────────────────┐         ┌──────────────────────┐
│    Carreras     │         │  CompetenciasDigitales│
├─────────────────┤         ├──────────────────────┤
│ PK CarreraID    │◄────────│ FK CarreraID          │
│    NombreCarrera│   1:N   │ PK CompetenciaID      │
│    Facultad     │         │    NombreHabilidad    │
└────────┬────────┘         │    NivelRequerido     │
         │ 1:N              └──────────────────────┘
         ▼
┌──────────────────┐
│   Estudiantes    │
├──────────────────┤
│ PK EstudianteID  │◄──────────────────────────┐
│    Nombre        │                           │ 1:1
│    FechaIngreso  │                           │
│    Genero        │      ┌────────────────────┴─────────┐
│    Ciudad        │      │    SeguimientoEgresados      │
└──────┬───────────┘      ├──────────────────────────────┤
       │ 1:N              │ PK EgresadoID                │
       ▼                  │ FK EstudianteID              │
┌──────────────────────┐  │    TieneEmpleoFormal (BIT)   │
│    Inscripciones     │  │    SalarioMensualUSD         │
├──────────────────────┤  │    TrabajaEnAreaDeEstudio    │
│ PK InscripcionID     │  └──────────────────────────────┘
│ FK EstudianteID      │   ↑ Esta tabla es la fuente de los
│ FK CarreraID         │     KPIs de empleabilidad del dashboard
│    NotaFinal         │
│    SemestreActual    │
└──────────────────────┘
```

> **Nota para la capa Silver:** `Inscripciones.SemestreActual` y `Inscripciones.NotaFinal` son usados para calcular la heurística de deserción (estudiante en riesgo = SemestreActual < 8 AND NotaFinal < 51).

---

### Diagrama ER — Gold (`DW_BrechaDigital`)

Almacén analítico en esquema copo de nieve. 1 tabla de hechos central + 7 dimensiones (2 son sub-dimensiones normalizadas).

```
                    ┌───────────────────────┐
                    │      DIM_CARRERA      │
                    ├───────────────────────┤
                    │ PK SK_Carrera         │
                    │    CarreraID  (BK)    │
                    │    nombrecarrera      │
                    │    area               │
                    └──────────┬────────────┘
                               │ N:1
┌───────────────────┐          │          ┌──────────────────────────┐
│   DIM_ESTUDIANTE  │          │          │      DIM_HABILIDAD       │
├───────────────────┤          │          ├──────────────────────────┤
│ PK SK_Estudiante  │          │          │ PK SK_Habilidad          │
│    EstudianteID   │          │          │    NombreHabilidad       │
│    nombre         │          │          │ FK SK_Categoria ────────►│
│    Genero         │          │          └────────────────────────  │
│    ciudad_resid.  │          │                                     │
└─────────┬─────────┘          │          ┌──────────────────────────┤
          │ N:1                │          │    DIM_CATEGORIA_SKILL   │
          │                    │          ├──────────────────────────┤
          │       ┌────────────▼──────────────────────────────┐     │
          └──────►│         FACT_INSERCION_LABORAL            │     │
                  ├───────────────────────────────────────────┤     │
                  │ FK SK_Estudiante                          │     │
                  │ FK SK_Carrera                             │     │
                  │ FK SK_Tiempo                              │◄────┘
                  │ FK SK_Region                              │  PK SK_Categoria
                  │ FK SK_MercadoLaboral                      │  NombreCategoria
                  │    EstaEmpleado         INT               │  (Básico/Interm./Avanz.)
                  │    SalarioMensualUSD    DECIMAL(10,2)     │
                  │    TrabajaEnAreaEstudio BIT               │
                  └───────────┬──────────────────┬────────────┘
                              │ N:1              │ N:1
                              ▼                  ▼
              ┌───────────────────┐  ┌───────────────────────────┐
              │    DIM_TIEMPO     │  │    DIM_MERCADO_LABORAL     │
              ├───────────────────┤  ├───────────────────────────┤
              │ PK SK_Tiempo      │  │ PK SK_MercadoLaboral      │
              │    anio           │  │    Ubicacion              │
              │    trimestre      │  │ FK SK_Region ────────────►│
              │    mes            │  └───────────────────────────┘
              │    Semestre       │                    │ N:1
              └───────────────────┘                   ▼
                                         ┌────────────────────────┐
                                         │      DIM_REGION        │
                                         ├────────────────────────┤
                                         │ PK SK_Region           │
                                         │    Ciudad              │
                                         │    Region              │
                                         │    (Nacional/Remoto)   │
                                         └────────────────────────┘
```

**Diferencias clave Bronze → Gold:**

| Aspecto | Bronze (`BrechaDigitalDB`) | Gold (`DW_BrechaDigital`) |
|---------|---------------------------|--------------------------|
| Propósito | Almacenar datos operacionales | Responder preguntas de negocio |
| Claves | Business keys (IDs naturales) | Surrogate keys (SK_*) |
| Normalización | Relacional estándar | Copo de nieve analítico |
| Granularidad | Eventos transaccionales | Eventos de inserción laboral |
| Optimizado para | Inserts/updates | Lecturas analíticas (GROUP BY, JOIN) |

---

## 9. Extracción de habilidades con IA

Este es uno de los componentes más diferenciadores del proyecto. Las vacantes de Adzuna contienen descripciones en texto libre — párrafos extensos que mencionan habilidades mezcladas con requisitos de experiencia, beneficios y cultura de empresa.

**El problema:** no se puede hacer un conteo de habilidades parseando texto libre con reglas simples.

**La solución:** `src/ingestion/skill_extraction.py` usa el modelo **LLaMA 3.1 8B** via API de Groq para extraer habilidades de forma estructurada.

### Flujo de extracción

```
Descripción de vacante (texto libre)
         │
         ▼
  Groq API — LLaMA 3.1 8B
  Prompt: "Extraé las habilidades técnicas de esta descripción
           en formato JSON array. Solo habilidades concretas
           (lenguajes, frameworks, herramientas)."
         │
         ▼
  ["Python", "Docker", "SQL", "AWS"]  ← JSON estructurado
         │
         ▼
  skills_extracted.csv
  (job_id, skills_json, extraction_method, confidence)
```

### Fallback con regex

Si el LLM falla (límite de tasa, error de red) o devuelve JSON inválido, el sistema cae automáticamente a un banco de patrones regex que cubre los keywords tecnológicos más frecuentes: `Python`, `JavaScript`, `SQL`, `Docker`, `React`, `AWS`, `Kubernetes`, etc.

### Por qué el CSV está commiteado

El `skills_extracted.csv` está incluido en el repositorio. Esto es intencional:
- Streamlit Cloud no ejecuta el script de extracción en cada deploy
- Evita costos de API en cada carga del dashboard
- Garantiza reproducibilidad — los mismos datos siempre

Para actualizar las habilidades con vacantes más recientes, hay que correr el script localmente y commitear el nuevo CSV.

---

## 10. El dashboard — Guía de cada página

El dashboard sigue un sistema de diseño editorial llamado **"The Digital Cartographer"** — paleta oscura (`#131315`), tipografía Inter, acentos en índigo (`#c0c1ff`) y cálido (`#ffb783`). Todas las páginas tienen filtros interactivos en el sidebar que afectan dinámicamente todos los gráficos.

### Inicio (`/`)

La página de inicio muestra:
- **4 métricas de calidad de datos**: carreras IT detectadas, estudiantes cargados, cobertura de salarios (%), última actualización
- **4 KPIs principales**: Tasa de Empleo Formal, % Empleados en su Área, Salario Promedio, Total Egresados
- **Tarjetas de navegación** hacia las 4 secciones de análisis
- **Fuentes de datos**: Bronze (SQL Server), Silver (CSVs), Gold (DW), CEPALSTAT, Adzuna API
- **Badges ODS 4 y ODS 8**

### KPIs Generales (`/kpis`)

**Filtros disponibles:** Carrera, Ciudad, Rango de años de egreso, País CEPALSTAT

**Contenido:**
- **5 KPI cards:** Tasa de Empleo Formal · Empleados en su Área · Salario Promedio · Egresados Analizados · Tasa de Deserción
- **Gauge de deserción**: Indicador visual del riesgo estudiantil. Se considera "en riesgo" a estudiantes con nota final < 51 y semestre actual < 8. Verde = bajo riesgo, amarillo = moderado, rojo = alto.
- **Benchmark CEPALSTAT**: Gráfico de barras verticales con el indicador ODS 4.4.1 (competencias TIC) para los 17 países de América Latina. Seleccionando un país específico en el filtro, el gráfico cambia a mostrar la evolución año a año de ese país.
- **Cards ODS 4 y ODS 8** con explicación de la alineación del proyecto

**Cómo funciona el benchmark CEPALSTAT:**
- Vista "Todos": una barra por país, promediando todos los años disponibles
- Vista por país: una barra por año, mostrando la evolución histórica del indicador en ese país

### Inserción Laboral (`/insercion`)

**Filtros disponibles:** Carrera, Ciudad, Género, Rango salarial

**Contenido:**
- **Tabla de inserción por carrera**: tasa de empleo formal, % en área, salario promedio, para cada una de las 5 carreras IT
- **Distribución salarial**: histograma de salarios de egresados empleados
- **Evolución temporal**: tasa de inserción por año de egreso (cohortes 2020-2028)
- **Mapa de calor ciudades**: distribución geográfica de empleados por carrera y ciudad

### Brecha de Habilidades (`/skill_gap`)

**Filtros disponibles:** Carrera, Ciudad, Rango de demanda (vacantes), Cobertura mínima (%)

Esta es la página más analítica del proyecto. Compara lo que el mercado laboral pide con lo que la academia enseña.

**Metodología del skill gap:**
1. El mercado demanda habilidades (fuente: `skills_extracted.csv`)
2. Cada carrera IT tiene un currículo con habilidades definidas (`CARRERA_SKILLS` en `data_loader.py`)
3. Se compara cada habilidad del mercado contra el currículo usando **fuzzy matching** (umbral 0.80 con `difflib.SequenceMatcher`)
4. Si hay similitud ≥ 0.80 → la habilidad está cubierta académicamente
5. Si no → es una brecha

**Contenido:**
- **3 KPI cards:** Cobertura Promedio · Brechas Críticas (<20%) · Top Skill Faltante
- **Gráfico combo (demanda + cobertura)**: barras azules = vacantes que requieren la skill, área naranja = cobertura académica escalada. Si la cobertura es baja y la demanda alta → brecha crítica visible
- **Habilidades más demandadas**: top 10 skills pedidas por el mercado en vacantes IT
- **Tabla de habilidades por carrera**: tabs por carrera mostrando el currículo académico completo
- **Expander con brechas críticas**: lista de habilidades con cobertura < 20% colapsada para no saturar la pantalla

**Por qué fuzzy matching en lugar de comparación exacta:**
El nombre de una habilidad varía. "JavaScript", "JS", "Javascript" son la misma skill. Con comparación exacta, aparecería como brecha. Con fuzzy matching (similitud ≥ 0.80), se detecta la equivalencia semántica correctamente.

### Asistente IA (`/chatbot`)

**Motor:** LLaMA 3.1 8B Instant via [Groq API](https://console.groq.com) (tier gratuito: 30 RPM)

El asistente recibe como contexto el estado actual del dashboard: KPIs calculados, brechas identificadas, distribución por carrera. Puede responder preguntas como:

- "¿Cuáles son las 3 habilidades con mayor brecha?"
- "¿Qué carrera tiene mejor inserción laboral?"
- "¿Cómo se compara Bolivia con Chile en competencias TIC?"
- "¿Cuántos estudiantes están en riesgo de deserción?"

El sidebar muestra el estado de la conexión con Groq (clave detectada / no detectada, mensajes enviados, estado del cliente).

---

## 11. OKRs y métricas de éxito

| Objetivo | Key Result | Estado |
|----------|------------|--------|
| **O1: Pipeline funcional de punta a punta** | Bronze → Silver → Gold implementados sin errores | ✅ |
| | Silver con 0% nulos o inconsistencias geográficas | ✅ |
| | `DW_BrechaDigital` con tabla de hechos y todas las dimensiones cargadas | ✅ |
| **O2: Insights accionables sobre la brecha digital** | Dashboard con 4+ KPIs calculados con datos reales | ✅ (9 KPIs) |
| | Al menos 3 habilidades con brecha identificadas | ✅ (múltiples) |
| | Análisis cubre 2+ ciudades bolivianas | ✅ |
| **O3: Demostración del dominio BI** | Las 4 secciones del dashboard funcionando | ✅ |
| | Cada integrante explica su capa | ✅ |
| | Informe documenta las decisiones técnicas clave | ✅ (este documento) |

**Extras entregados más allá de los OKRs:**
- Despliegue público en Streamlit Cloud
- Extracción de habilidades con LLM (Groq API)
- Benchmark CEPALSTAT con drill-down por país y año
- Sistema de diseño editorial "Digital Cartographer"
- Fallback automático CSV cuando SQL Server no está disponible

---

## 12. Alineación con los ODS

### ODS 4 — Educación de Calidad (Meta 4.4)

> "De aquí a 2030, aumentar considerablemente el número de jóvenes y adultos que tienen las competencias necesarias, en particular técnicas y profesionales, para acceder al empleo, el trabajo decente y el emprendimiento."

**Cómo este proyecto contribuye:**
- Mide directamente el indicador 4.4.1 (% de jóvenes con competencias TIC) para Bolivia vs la región
- Identifica las brechas entre currículo académico y demanda del mercado — la información necesaria para actualizar los planes de estudio
- Cuantifica la tasa de deserción para identificar dónde se pierde capital humano

### ODS 8 — Trabajo Decente y Crecimiento Económico (Meta 8.6)

> "De aquí a 2020, reducir considerablemente la proporción de jóvenes que no están empleados y no cursan estudios ni reciben capacitación."

**Cómo este proyecto contribuye:**
- Mide la tasa de empleo formal de egresados IT
- Analiza si los egresados trabajan en su área de estudio (empleo decente y alineado)
- Monitorea salarios para evaluar acceso a trabajo digno

---

## 13. Despliegue en Streamlit Cloud

La aplicación está disponible públicamente en:

**[https://brecha-digital-bolivia-bi.streamlit.app/](https://brecha-digital-bolivia-bi.streamlit.app/)**

### Cómo funciona el despliegue

Streamlit Cloud conecta directamente con el repositorio de GitHub. En cada push a `main`, el servidor redeploya automáticamente.

El archivo de entrada es `src/dashboard/app.py`. Al iniciar, el app:
1. Lee los secrets de Streamlit Cloud (equivalentes al `.env` local) e los inyecta en `os.environ`
2. Intenta conectarse a SQL Server — si falla, carga los CSVs de `data/processed/`
3. Carga los estilos del design system
4. Renderiza la página de inicio

### Secrets requeridos (Settings → Secrets en Streamlit Cloud)

```toml
GROQ_API_KEY = "gsk_..."
ADZUNA_APP_ID = "..."
ADZUNA_APP_KEY = "..."
```

Los secrets de SQL Server son opcionales — sin ellos, el dashboard funciona 100% con los CSVs commiteados.

### Modo degradado (sin SQL Server)

El `data_loader.py` tiene fallback automático:

```
1. Intenta: conexión SQL Server via pyodbc
2. Si falla: carga data/processed/estudiantes_cleaned.csv
3. Filtra: solo las 5 carreras IT
4. Valida: cobertura de datos, KPIs calculados
```

Esto garantiza que el dashboard desplegado funcione siempre, incluso si la base de datos institucional no es accesible desde internet.

---

## 14. Responsabilidades del equipo

| Integrante | Lead Phase | Entregable principal | Estado |
|------------|------------|---------------------|--------|
| Abraham Flores Barrionuevo | Bronze — Ingesta | `src/ingestion/` + `data/raw/` | ✅ |
| Juan Nicolás Flores Delgado | Silver — Transformación | `src/transform/` + `data/processed/` | ✅ |
| Micaela Pérez Vásquez | Gold — Schema | `database/` + `DW_BrechaDigital` | ✅ |
| Mayra Villca Méndez | Análisis — Notebooks | `notebooks/` con KPIs calculados | ✅ |
| Diego Vargas Urzagaste | Dashboard — Integración | `src/dashboard/` + despliegue Cloud | ✅ |

**Todos los integrantes contribuyen en todas las fases.** El rol "Lead" indica quién es responsable de revisar y garantizar la calidad de esa capa.

---

## 15. Comandos rápidos

```bash
# Clonar y configurar
git clone https://github.com/temps-code/brecha-digital-bi.git
cd brecha-digital-bi
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
pip install -r requirements.txt
cp .env.example .env               # Completar con tus credenciales

# Pipeline completo (en orden)
python src/ingestion/sqlserver.py      # Bronze: académico
python src/ingestion/cepalstat.py      # Bronze: macro
python src/ingestion/empleos.py        # Bronze: vacantes
python src/ingestion/skill_extraction.py  # Silver+: skills con LLM
python src/transform/clean.py          # Silver: limpieza
python src/transform/normalize.py      # Silver: normalización
python src/schema/dimensions.py        # Gold: dimensiones
python src/schema/facts.py             # Gold: hechos

# Dashboard local
streamlit run src/dashboard/app.py
# → http://localhost:8501

# Tests
pytest tests/dashboard/ -v

# Ver estado del repo
git status
git log --oneline -10
```

---

## 16. Glosario

| Término | Definición en el contexto del proyecto |
|---------|----------------------------------------|
| **Bronze** | Capa de datos crudos extraídos directamente de las fuentes, sin modificar |
| **Silver** | Capa de datos limpios y estandarizados, listos para análisis |
| **Gold** | Almacén de datos estructurado en esquema copo de nieve para consultas de negocio |
| **Carreras IT** | Las 5 carreras analizadas: Sistemas, Software, Ciencia de Datos, Telecomunicaciones, Ciberseguridad |
| **Fuzzy Matching** | Comparación de similitud entre textos con umbral 0.80 (SequenceMatcher de Python) — permite detectar "Python" y "python" como la misma habilidad |
| **Skill Gap** | Brecha entre habilidades que enseña la institución y las que pide el mercado laboral |
| **CARRERA_SKILLS** | Diccionario interno con el currículo de cada carrera IT (fuente de verdad académica) |
| **skills_extracted.csv** | CSV con habilidades extraídas por LLM de descripciones de vacantes Adzuna |
| **KPI** | Indicador clave de rendimiento (ej: tasa de empleo, salario promedio) |
| **OKR** | Objetivo con resultados clave medibles — define el éxito del proyecto |
| **ODS 4.4.1** | Indicador ONU: % de jóvenes con competencias TIC (fuente: CEPALSTAT) |
| **Streamlit** | Framework Python para dashboards web — corre en `localhost:8501` local o en Streamlit Cloud |
| **Groq API** | API que provee acceso a LLaMA 3.1 con latencia ultra-baja (tier gratuito: 30 RPM) |
| **LLaMA 3.1 8B** | Modelo de lenguaje de Meta usado para extracción de skills y el chatbot BI |
| **DW** | Data Warehouse (`DW_BrechaDigital`) — base de datos SQL Server optimizada para análisis |
| **Esquema copo de nieve** | Modelo dimensional normalizado con sub-dimensiones, elegido sobre estrella por corrección técnica |
| **Fallback CSV** | Mecanismo automático que usa archivos CSV cuando SQL Server no está disponible |
| **Medallión architecture** | Arquitectura de datos en capas: Bronze → Silver → Gold |

---

**Última actualización:** 2026-04-07  
**Estado del proyecto:** Desplegado y funcional  
**Demo:** [brecha-digital-bolivia-bi.streamlit.app](https://brecha-digital-bolivia-bi.streamlit.app/)  
**Repositorio:** [github.com/temps-code/brecha-digital-bi](https://github.com/temps-code/brecha-digital-bi)
