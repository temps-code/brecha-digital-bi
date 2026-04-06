# Guía del Proyecto — Brecha Digital BI

**Para:** Todo el equipo  
**Proyecto:** Estrategia para la Reducción de la Brecha Digital Laboral en la Educación Técnica Superior  
**Materia:** Inteligencia de Negocios — UPDS 2026  
**Versión:** 2.0 (Actualizada 2026-04-05)

---

## ¿De qué trata este proyecto?

Las instituciones de educación técnica en Bolivia tienen un problema concreto: **no saben si sus egresados consiguen trabajo**. Tienen datos de los estudiantes, de las carreras, de las inscripciones — pero esa información está guardada en una base de datos que nadie analiza. Al mismo tiempo, el mercado laboral pide habilidades específicas (Python, SQL, redes, etc.) que muchas veces no coinciden con lo que se enseña.

**Este proyecto construye un puente entre esos dos mundos.**

Tomamos los datos académicos internos y los cruzamos con información real del mercado laboral (vacantes de empleo, indicadores regionales) para responder preguntas como:
- ¿Qué porcentaje de egresados de Sistemas consiguió trabajo en su área?
- ¿Qué habilidades pide el mercado que la institución no está enseñando?
- ¿En qué ciudades hay más demanda de técnicos en TIC?

El resultado final es un **dashboard interactivo** que cualquier director académico puede abrir y usar para tomar mejores decisiones.

---

## OKRs del Proyecto

Los OKRs (Objectives and Key Results) definen el éxito del proyecto. Son tres objetivos concretos, cada uno con resultados clave medibles que nos permiten saber si lo logramos. No son aspiraciones vagas — son compromisos del equipo.

**O1: Construir un pipeline de datos funcional de punta a punta**
- KR1: Las 3 capas (Bronze → Silver → Gold) están implementadas y los datos fluyen sin errores hasta el DW
- KR2: Los datos en Silver tienen 0% de valores nulos o inconsistencias geográficas
- KR3: `DW_BrechaDigital` tiene la tabla de hechos y todas las dimensiones cargadas con datos reales

**O2: Generar insights accionables sobre la brecha digital laboral**
- KR1: El dashboard muestra al menos 4 KPIs calculados con datos reales
- KR2: Se identifican al menos 3 habilidades con brecha entre lo que enseña la institución y lo que pide el mercado
- KR3: El análisis cubre al menos 2 ciudades bolivianas para el benchmarking regional

**O3: Demostrar dominio de la metodología BI en la presentación final**
- KR1: El dashboard tiene las 4 secciones funcionando (KPIs, Inserción Laboral, Skill Gap, Chatbot)
- KR2: Cada integrante puede explicar su capa del pipeline sin leer notas
- KR3: El informe final documenta las decisiones técnicas clave (esquema elegido, fuentes de datos, criterios de limpieza)

> **¿Qué diferencia un OKR de un KPI?** Los KPIs miden el estado de algo en curso (ej: tasa de inserción laboral actual). Los OKRs definen a dónde queremos llegar y si llegamos. En este proyecto, los KPIs del dashboard son las herramientas con las que *medimos* si los OKRs se cumplen.

---

## ¿Qué es Business Intelligence (BI)?

BI es el proceso de transformar datos crudos en información útil para tomar decisiones. No es solo hacer gráficos bonitos — es construir todo el sistema que permite que esos gráficos sean confiables, actualizados y significativos.

Pensalo como una fábrica:

```
Materia prima          Procesamiento         Producto terminado
(datos crudos)    →    (limpieza + orden)  →  (dashboard + análisis)
```

En nuestro proyecto, esa fábrica tiene tres capas bien definidas. Cada capa depende de la anterior — si la anterior está mal, todo lo que viene después también va a estar mal.

---

## Las tres capas del proyecto

### Capa Bronze — "Los datos tal como están"

**¿Qué es?** La extracción de datos desde las fuentes originales, sin modificar nada. Es como sacar los ingredientes de la heladera y ponerlos sobre la mesa.

**¿Qué hicimos?**
- Conectamos con la base de datos SQL Server (`BrechaDigitalDB`) y extrajimos las tablas de estudiantes, inscripciones, carreras y egresados
- Consultamos la API de Adzuna para obtener vacantes laborales reales del sector tecnológico
- Consultamos la API de CEPALSTAT para obtener indicadores de conectividad digital por región

**¿Dónde quedan los datos?** En la carpeta `data/raw/` — archivos CSV, uno por cada fuente.

**¿Qué NO se hace en Bronze?** No se modifica ningún dato. Si hay errores, valores raros, o nombres mal escritos, se dejan así. La idea es tener una copia fiel de la fuente original.

**Archivos involucrados:**
- `src/ingestion/sqlserver.py` — Extrae de SQL Server (conexión + queries)
- `src/empleos/empleos.py` — Consulta API Adzuna y extrae habilidades
- `src/empleos/cepalstat.py` — Consulta API CEPALSTAT
- `data/raw/` — Donde se guardan los CSVs crudos
  - `estudiantes_raw.csv`
  - `inscripciones_raw.csv`
  - `egresados_raw.csv`
  - `carreras_raw.csv`
  - `adzuna_raw.csv`
  - `cepalstat_raw.csv`

**Cómo ejecutar:**
```bash
# Extraer todos los datos Bronze
python scripts/run_ingestion.py

# O individually
python src/ingestion/sqlserver.py
python src/empleos/empleos.py
python src/empleos/cepalstat.py
```

**Responsable:** Abraham Flores

---

### Capa Silver — "Los datos limpios y organizados"

**¿Qué es?** La limpieza y estandarización de los datos Bronze. Es como lavar, pelar y cortar los ingredientes antes de cocinar.

**¿Qué se hace?**
- Se eliminan espacios, caracteres raros, valores duplicados
- Se unifican los formatos (todas las ciudades escritas igual, todas las fechas en el mismo formato)
- Se reemplazan los valores vacíos con valores por defecto cuando tiene sentido hacerlo
- Se integran datos de distintas fuentes que hablan de lo mismo
- Se valida la calidad (0% nulos, sin inconsistencias geográficas)

**¿Dónde quedan los datos?** En `data/processed/` — archivos CSV limpios, listos para análisis.

**¿Por qué es importante?** Un dato sucio en Silver contamina todos los análisis que vienen después.

**Archivos involucrados:**
- `src/transform/limpiar_estudiantes.py` — Limpieza de académicos
  - Normaliza nombres de carreras
  - Valida rangos (género, semestre, notas)
  - Trata valores ausentes
- `src/transform/limpiar_empleos.py` — Limpieza de vacantes
  - Estandariza ciudades
  - Extrae y normaliza salarios
  - Extrae habilidades de descripciones
- `src/transform/validar_calidad.py` — Valida calidad de datos
  - Porcentaje de nulos
  - Duplicados
  - Valores fuera de rango
- `data/processed/` — Archivos limpios
  - `estudiantes_cleaned.csv`
  - `inscripciones_cleaned.csv`
  - `egresados_cleaned.csv`
  - `carreras_cleaned.csv`
  - `competenciasdigitales_cleaned.csv`
  - `empleos/vacantes_tecnologicas_cleaned.csv`
  - `cepalstat/indicadores_tic_region_cleaned.csv`

**Cómo ejecutar:**
```bash
# Transformación completa
python src/transform/main.py

# O paso a paso
python src/transform/limpiar_estudiantes.py
python src/transform/limpiar_empleos.py
python src/transform/validar_calidad.py
```

**Responsable:** Juan Nicolás Flores

---

### Capa Gold — "El almacén de datos final"

**¿Qué es?** La carga de los datos limpios (Silver) en una base de datos estructurada, diseñada específicamente para análisis. Es el producto terminado listo para usar.

**¿Qué se hace?**
- Se cargan los datos en tablas especialmente diseñadas para responder preguntas de negocio rápidamente
- Se organiza todo en un **esquema copo de nieve**: una tabla central de hechos rodeada de dimensiones
- La tabla central es `FACT_INSERCION_LABORAL` — cada fila representa a un egresado y si consiguió trabajo

**¿Dónde quedan los datos?** En SQL Server, base de datos `DW_BrechaDigital`. También disponible como CSVs para deployment.

**Archivos involucrados:**
- `database/schema/create_dimensions.sql` — Crea tablas de dimensiones
  - `DIM_ESTUDIANTE`
  - `DIM_CARRERA`
  - `DIM_REGION`
  - `DIM_TIEMPO`
  - `DIM_COMPETENCIA`
  - `DIM_VACANTE`
- `database/schema/create_fact.sql` — Crea tabla de hechos
  - `FACT_INSERCION_LABORAL` (eventos: egresado X tiene/no tiene empleo)
- `scripts/seed.sql` — Carga datos desde CSVs a Gold
  - Trunca tablas
  - Inserta dimensiones
  - Inserta hechos con cálculos
- `src/schema/` — Código Python para cargas automáticas

**Cómo ejecutar:**
```bash
# Carga completa
python scripts/load_data.py

# O vía SQL directo (en SQL Server)
sqlcmd -S SERVER -d DW_BrechaDigital -i scripts/seed.sql
```

**Responsable:** Micaela Pérez

---

## Capa Final: Dashboard y Análisis

### Notebooks de Análisis (Antes del Dashboard)

**¿Qué son?** Archivos Jupyter donde se escriben los KPIs y se hacen análisis exploratorios. Aquí es donde se responden las preguntas de negocio.

**Archivos involucrados:**
- `notebooks/01_eda_estudiantes.ipynb` — Análisis exploratorio
  - Distribución de estudiantes por carrera IT
  - Tendencias demográficas
  - Datos académicos (semestre, notas)
- `notebooks/02_brecha_habilidades.ipynb` — Skill gap analysis
  - Habilidades del mercado vs currículo
  - Fuzzy matching (0.80 threshold)
  - Brecha identificada
- `notebooks/03_calculo_kpis.ipynb` — KPIs finales
  - Tasa de empleo: 82.7%
  - % empleados en área: 98%
  - Salario promedio: $2,800+
  - Deserción: validación de heurística

**Cambios recientes:**
- Refactorizados para usar CSVs (no SQL Server)
- Filtrados a 5 carreras IT solo
- Resultado portable y deployable

**Cómo ejecutar:**
```bash
jupyter notebook notebooks/
# Abrir y ejecutar cada notebook (las celdas con comentarios)
```

**Responsable:** Mayra Villca

---

### Dashboard Interactivo

**¿Qué es?** Aplicación web interactiva donde se visualizan los datos con gráficos, tablas y un asistente IA.

**Tecnología:** Streamlit + Plotly + Groq API

**Estructura:**
```
src/dashboard/
├── app.py                          # Entry point (hero + KPI cards)
├── components/
│   ├── data_loader.py              # Carga datos + filtrado IT + validación
│   ├── charts.py                   # Funciones de gráficos
│   └── styles.py                   # Diseño (colores, fuentes, componentes)
└── pages/
    ├── 01_kpis.py                  # KPIs generales + benchmarking
    ├── 02_insercion.py             # Análisis de inserción laboral
    ├── 03_skill_gap.py             # Visualización brecha de habilidades (OPTIMIZADA)
    └── 04_chatbot.py               # Asistente IA con Groq
```

#### 4.1 Data Layer - `components/data_loader.py`

**Lo que hace:** Carga datos desde SQL o CSVs, filtra a 5 carreras IT, valida, calcula KPIs.

**Funciones principales:**

**`load_df()` — Carga datos (líneas 95-180)**
```python
# Intenta SQL Server (si disponible)
# Si falla: usa CSVs desde data/processed/
# Filtra: solo 5 carreras IT (IT_CAREERS constante, líneas 8-12)
# Agrega: columna graduation_year (fórmula)
# Valida: cobertura de datos
# Retorna: DataFrame + errors list
```

**`get_kpis()` — Calcula indicadores (líneas 292-342)**
```python
# Tasa empleo: 82.7%
# % en área: 98%
# Salario promedio: $2,800+
# Total egresados: 49,866
# Retorna: dict con KPIs + _errors
```

**`get_skill_gap()` — Analiza brecha (líneas 443-551)**
```python
# Fuzzy matching: difflib.SequenceMatcher
# Threshold: 0.80 similitud
# Retorna: DataFrame [habilidad, demanda, cobertura_%]
```

**`get_skill_gap_filtered(top_n=15)` — Filtra para visualización (líneas NEW)**
```python
# Retorna: top 15 habilidades + count de otras
# Uso: evita que gráfico sea ilegible
```

**`get_habilidades_demandadas_filtered(top_n=10)` — Filtra demanda (líneas NEW)**
```python
# Retorna: top 10 + count de otras
# Uso: gráfico compacto
```

**Cambios recientes (Commits 53c88de - 08be7ca):**
- Agregado IT_CAREERS constant (5 carreras)
- Agregado cálculo graduation_year
- Implementado fuzzy matching
- Agregada validación de datos
- Agregadas funciones de filtrado

#### 4.2 Visualización - `components/charts.py`

**`combo_skill_gap()` — Gráfico demanda vs cobertura (líneas 247-285)**
- Barras azules: demanda (vacantes)
- Línea naranja: cobertura (%)
- Doble eje Y
- Interactivo

**`bar_habilidades_demandadas()` — Top habilidades (línea 133-160)**
- Barras horizontales
- Ordenadas por demanda
- Top 10 mostrados

#### 4.3 Páginas

**`01_kpis.py` — KPIs generales**
- 4 tarjetas: Empleo, Área, Salario, Egresados
- Badge de validación (línea 41)
- Gráfico de benchmarking CEPALSTAT
- Gauge de deserción
- Cambios: agregada validación (líneas 31-38)

**`02_insercion.py` — Inserción laboral**
- Tabla: empleo por carrera
- Gráfico: evolución temporal (ahora usa graduation_year)
- Mapa de calor: ciudades
- Cambios: temporal fix, validación de salarios (líneas 60-74)

**`03_skill_gap.py` — Brecha de habilidades (OPTIMIZADA - Commit 08be7ca)**
- Expander: advertencias colapsadas (líneas 45-60)
- Gráfico 1: Top 15 + "+944 adicionales" (líneas 65-75)
- Gráfico 2: Top 10 demandadas + expander (líneas 80-105)
- Expanders: tabla completa, vacantes (líneas 135-140)
- Cambios: filtrado, mensajes cortos, mejor UX

**`04_chatbot.py` — Asistente IA**
- Chat interactivo con Groq API
- Contexto: KPIs + skill gap
- Prompts sugeridos (español)
- Cambios: contexto actualizado para IT-only

**Cómo ejecutar:**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr dashboard
streamlit run src/dashboard/app.py

# Accesible en http://localhost:8501
```

**Archivos de configuración:**
- `.env` — Credenciales (DW_SERVER, ADZUNA_APP_ID, GROQ_API_KEY)
- `.streamlit/config.toml` — Configuración Streamlit
- `requirements.txt` — Dependencias Python

**Responsable:** Diego Vargas

---

## El flujo completo de un dato

Para entender cómo todo se conecta, seguimos a un dato específico desde el origen hasta el dashboard:

```
1. SQL Server tiene: EstudianteID=42, Nombre="María Quispe", Carrera="Ingeniería de Sistemas"

2. Bronze (sqlserver.py) lo extrae:
   data/raw/estudiantes_raw.csv

3. Silver (limpiar_estudiantes.py) lo normaliza:
   data/processed/estudiantes_cleaned.csv
   → "Ingeniería de Sistemas" (estandarizado)

4. Gold (dimensions.py) lo carga:
   DIM_ESTUDIANTE → SK_Estudiante=42, SK_Carrera=3 (Sistemas)

5. Dashboard (data_loader.py) lo filtra:
   if NombreCarrera in IT_CAREERS: ✓ (Sistemas es IT)
   load_df() retorna fila con María Quispe

6. KPIs lo cuentan:
   get_kpis() → +1 a total_egresados

7. Dashboard muestra:
   "Egresados Analizados: 49,866"
```

---

### Fase 4: UI Polish (COMPLETADA)
- **Commits:** 1af7744
- **Qué:** Data quality indicators, badges, contexto IA
- **Archivos:** app.py + 4 pages
- **Status:** ✅ DONE — todas las páginas muestran datos

### Fase 5: Testing & Optimization (COMPLETADA)
- **Commits:** d35c082, 08be7ca
- **Qué:** 40 tests, visualización optimizada
- **Archivos:** tests/dashboard/ + 03_skill_gap.py optimizado
- **Status:** ✅ DONE — 40/40 tests passing, gráficos legibles

---

## Responsabilidades del equipo

| Integrante | Rol | Qué entrega | Estado |
|------------|-----|-------------|--------|
| Abraham Flores | Lead Bronze | Scripts de extracción + `data/raw/` | ✅ |
| Juan Nicolás Flores | Lead Silver | Scripts de limpieza + `data/processed/` | ✅ |
| Micaela Pérez | Lead Gold | Tablas + schema copo nieve + `DW_BrechaDigital` | ✅ |
| Mayra Villca | Lead Análisis | Notebooks con KPIs + `notebooks/` | ✅ |
| Diego Vargas | Lead Dashboard | Dashboard 4 secciones + `src/dashboard/` | ✅ |

**Todos contribuyen en todas las fases.**

---

## ¿Qué se presenta en la demo?

1. **Problema** (1 min) — por qué la brecha digital importa
2. **Arquitectura** (2 min) — pipeline Bronze → Silver → Gold
3. **Demo del dashboard** (5 min) — las 4 secciones con datos reales
4. **Conclusiones** (2 min) — qué responde, qué decisiones permitiría

**Cada integrante debe explicar su capa sin leer notas.**

---

## Comandos rápidos

```bash
# Setup
git clone https://github.com/temps-code/brecha-digital-bi.git
cd brecha-digital-bi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar pipeline completo
python scripts/run_ingestion.py     # Bronze
python src/transform/main.py        # Silver
python scripts/load_data.py         # Gold

# Dashboard
streamlit run src/dashboard/app.py

# Tests
pytest tests/dashboard/ -v

# Ver rama actual
git branch
git status

# Cambiar rama
git checkout main
```

---

## Documentación adicional

- [`docs/guia-git.md`](guia-git.md) — Git workflow para el proyecto
- [`docs/esquema_copo_nieve.md`](esquema_copo_nieve.md) — Esquema Gold técnico
- [`README.md`](../README.md) — Overview del proyecto
- [`design.md`](../design.md) — Decisiones técnicas dashboard
- [`proposal.md`](../proposal.md) — Propuesta cambio dashboard

---

## Glosario rápido

| Término | Qué significa en este proyecto |
|---------|-------------------------------|
| **Pipeline** | Bronze → Silver → Gold → Dashboard |
| **CSV** | Archivo de texto con datos (estudiantes.csv, empleos.csv, etc.) |
| **Carrera IT** | Solo 5: Sistemas, Software, Data, Telecomunicaciones, Ciberseguridad |
| **Fuzzy Matching** | Comparación de similitud entre textos (0.80 threshold) |
| **Graduation Year** | Año de egreso (no entrada) — fórmula: anio_y + (8-SemestreActual)/2 |
| **KPI** | Número clave (82.7% empleo, $2800 salario, etc.) |
| **Skill Gap** | Diferencia entre habilidades que enseña institución vs mercado |
| **Streamlit** | Framework Python para dashboards (localhost:8501) |
| **Groq API** | Servicio de IA (LLaMA) para el chatbot |
| **DW** | Data Warehouse — BD estructurada para análisis |

---

**Última actualización:** 2026-04-05  
**Contribuidores:** Equipo BI — UPDS 2026  
**Rama principal:** `main`
