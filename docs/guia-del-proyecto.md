# Guía del Proyecto — Brecha Digital BI

**Para:** Todo el equipo  
**Proyecto:** Estrategia para la Reducción de la Brecha Digital Laboral en la Educación Técnica Superior  
**Materia:** Inteligencia de Negocios — UPDS 2026

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
- Consultamos la API de CEPALSTAT para obtener indicadores de conectividad digital por región
- Consultamos la API de Adzuna para obtener vacantes laborales reales del sector tecnológico

**¿Dónde quedan los datos?** En la carpeta `data/raw/` — archivos CSV, uno por cada fuente.

**¿Qué NO se hace en Bronze?** No se modifica ningún dato. Si hay errores, valores raros, o nombres mal escritos, se dejan así. La idea es tener una copia fiel de la fuente original.

**Responsable:** Abraham Flores — `src/ingestion/`

---

### Capa Silver — "Los datos limpios y organizados"

**¿Qué es?** La limpieza y estandarización de los datos Bronze. Es como lavar, pelar y cortar los ingredientes antes de cocinar.

**¿Qué se hace?**
- Se eliminan espacios, caracteres raros, valores duplicados
- Se unifican los formatos (todas las ciudades escritas igual, todas las fechas en el mismo formato)
- Se reemplazan los valores vacíos con valores por defecto cuando tiene sentido hacerlo
- Se integran datos de distintas fuentes que hablan de lo mismo (ej: un estudiante en la base interna + su ciudad en los datos regionales)

**¿Dónde quedan los datos?** En `data/processed/` — archivos CSV limpios, uno por cada tabla.

**¿Por qué es importante?** Si en Bronze un estudiante tiene ciudad = "Stanta Cruz" y otro tiene "santa cruz de la sierra", son la misma ciudad pero el sistema los va a contar como dos ciudades distintas. Silver es donde eso se arregla. Un dato sucio en Silver contamina todos los análisis que vienen después.

**Responsable:** Juan Nicolás Flores — `src/transform/`

---

### Capa Gold — "El almacén de datos final"

**¿Qué es?** La carga de los datos limpios (Silver) en una base de datos estructurada, diseñada específicamente para análisis. Es el producto terminado listo para usar.

**¿Qué se hace?**
- Se cargan los datos en tablas especialmente diseñadas para responder preguntas de negocio rápidamente
- Se organiza todo en un **esquema copo de nieve**: una tabla central de hechos (los eventos que queremos analizar) rodeada de tablas de dimensiones (el contexto de esos eventos)
- La tabla central es `FACT_INSERCION_LABORAL` — cada fila representa a un egresado y si consiguió trabajo o no, con cuánto salario, en qué ciudad, con qué habilidades

**¿Dónde quedan los datos?** En SQL Server, base de datos `DW_BrechaDigital`.

**¿Qué es el esquema copo de nieve?** Es una forma de organizar las tablas. En lugar de tener todo mezclado en una sola tabla gigante (que sería redundante y difícil de mantener), separamos la información en tablas más pequeñas que se conectan entre sí. Por ejemplo:

- `FACT_INSERCION_LABORAL` → registra el evento (egresado X consiguió trabajo)
- `DIM_ESTUDIANTE` → datos del estudiante (nombre, carrera, año de ingreso)
- `DIM_HABILIDAD` → 22 competencias digitales del currículo académico (fuente: `CompetenciasDigitales` en Bronze)
- `DIM_MERCADO_LABORAL` → datos de la empresa que lo contrató
- `DIM_REGION` → ciudad y departamento

**Responsable:** Micaela Pérez — `src/schema/`

---

## Análisis y KPIs — "Las preguntas que respondemos"

Antes de construir el dashboard, necesitamos calcular los indicadores clave (**KPIs**). Esto se hace en notebooks de Jupyter — archivos donde se escribe código Python y se ven los resultados al instante.

Los KPIs que calculamos son:
- **Tasa de inserción laboral:** % de egresados que consiguieron empleo en su área dentro de los 12 meses de graduarse
- **Índice de brecha de habilidades:** comparación entre las habilidades que enseña la institución y las que pide el mercado laboral
- **Predicción de deserción:** identificación de estudiantes con alto riesgo de abandonar según su historial académico
- **Benchmarking regional:** cómo está Bolivia comparada con otros países de América Latina en conectividad digital (datos CEPALSTAT)

**Responsable:** Mayra Villca — `notebooks/`

---

## El Dashboard — "Lo que se muestra en la demo"

El dashboard es la interfaz final. Es una aplicación web que cualquier persona puede abrir en el navegador y explorar los datos sin saber nada de programación.

Tiene cuatro secciones:
1. **KPIs generales** — los números más importantes en pantalla grande
2. **Inserción laboral** — gráficos por carrera, ciudad y año
3. **Skill Gap** — qué pide el mercado vs qué enseña la institución
4. **Asistente IA** — se puede hacer preguntas en lenguaje natural ("¿cuántos egresados de Sistemas consiguieron trabajo en 2024?") y la IA responde usando los datos

**Responsable:** Diego Vargas — `src/dashboard/`

---

## El flujo completo de un dato

Para entender cómo todo se conecta, seguimos a un dato específico desde el origen hasta el dashboard:

```
1. SQL Server tiene registrado (50.000 estudiantes, 25.000 seguimientos, 22 competencias):
   EstudianteID=42, Nombre="María Quispe", Carrera="Sistemas", Promedio=78

2. Bronze (sqlserver.py) lo extrae y guarda en:
   data/raw/estudiantes.csv  →  fila: 42, María Quispe, Sistemas, 78

3. Silver (clean.py + normalize.py) lo limpia:
   - "María Quispe" queda como "María Quispe" (sin espacios extra)
   - Ciudad "LA PAZ" se estandariza a "La Paz"
   data/processed/estudiantes_cleaned.csv

4. Gold (dimensions.py) lo carga en:
   DIM_ESTUDIANTE  →  SK_Estudiante=42, nombre="María Quispe", SK_Carrera=3

5. Gold (facts.py) registra el hecho:
   FACT_INSERCION_LABORAL  →  SK_Estudiante=42, EstaEmpleado=1, SalarioMensualUSD=650, TrabajaEnAreaDeEstudio=1

6. Dashboard muestra:
   "Sistemas: 74% de inserción laboral — promedio 7.2 meses hasta primer empleo"
```

Si en cualquier paso hay un error, el dato llega mal al final y el KPI es incorrecto. Por eso cada capa importa.

---

## Cronograma y estado actual

| Día | Fecha | Fase | Estado |
|-----|-------|------|--------|
| Día 1 | 1 de abril | Bronze — Extracción de datos | ✅ Completado |
| Día 2 | 2 de abril | Silver — Limpieza y transformación | 🔄 En progreso |
| Día 3 | 3 de abril | Gold — Modelado + Dashboard | ⏳ Pendiente |
| Día 4 | 6 de abril | Pruebas finales y documentación | ⏳ Pendiente |
| Día 5 | 7 de abril | **DEMO DAY** | ⏳ Pendiente |

---

## Responsabilidades del equipo

Cada integrante es **lead** de su fase — eso significa que es responsable de que esa parte funcione correctamente y de revisar el trabajo de los demás en esa área.

| Integrante | Rol | Qué entrega |
|------------|-----|-------------|
| Abraham Flores | Lead Bronze | Scripts de extracción funcionando, datos en `data/raw/` |
| Juan Nicolás Flores | Lead Silver | Scripts de limpieza funcionando, datos en `data/processed/` sin nulos ni inconsistencias |
| Micaela Pérez | Lead Gold | Tablas cargadas en `DW_BrechaDigital`, esquema copo de nieve completo |
| Mayra Villca | Lead Análisis | Notebooks con KPIs calculados y comentados |
| Diego Vargas | Lead Dashboard | Dashboard corriendo en Streamlit con las 4 secciones funcionando |

**Todos contribuyen en todas las fases.** El rol de Lead no significa que trabaja solo — significa que coordina, revisa y garantiza la calidad de esa capa.

---

## ¿Qué se presenta en la demo?

La presentación final dura 10 minutos. El objetivo es mostrar el sistema funcionando de punta a punta:

1. **Problema** (1 min) — explicar la brecha digital y por qué importa
2. **Arquitectura** (2 min) — mostrar el pipeline Bronze → Silver → Gold en el diagrama
3. **Demo del dashboard** (5 min) — navegar las 4 secciones con datos reales
4. **Conclusiones** (2 min) — qué responde el sistema, qué decisiones permitiría tomar

El jurado va a preguntar sobre las decisiones técnicas — por qué copo de nieve y no estrella, por qué limpiar los datos de esa manera, cómo funciona el asistente IA. Cada integrante debe poder explicar su capa.

---

## Documentación adicional

- [`docs/guia-git.md`](guia-git.md) — Cómo usar Git y GitHub en este proyecto (para quienes recién arrancan)
- [`docs/esquema_copo_nieve.md`](esquema_copo_nieve.md) — Documentación técnica completa del esquema Gold

---

## Glosario rápido

| Término | Qué significa en este proyecto |
|---------|-------------------------------|
| **Pipeline** | El flujo completo de datos desde la fuente hasta el dashboard |
| **Bronze / Silver / Gold** | Las tres etapas de procesamiento de datos (crudo → limpio → estructurado) |
| **Data Warehouse (DW)** | Base de datos optimizada para análisis, no para transacciones |
| **Esquema Copo de Nieve** | Forma de organizar las tablas del DW para evitar redundancia |
| **Tabla de Hechos (FACT)** | Registra los eventos que queremos analizar (ej: inserción laboral) |
| **Dimensión (DIM)** | Contexto del evento (quién, dónde, cuándo, qué habilidades) |
| **KPI** | Indicador clave de desempeño — el número que resume algo importante |
| **ETL / ELT** | Proceso de Extraer, Transformar y Cargar datos |
| **CSV** | Archivo de texto con datos en filas y columnas, separados por comas |
| **API** | Servicio externo del que obtenemos datos (Adzuna, CEPALSTAT) |
