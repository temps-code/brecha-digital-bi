# Esquema Copo de Nieve — Documentación

**Almacenamiento:** SQL Server — base de datos `DW_BrechaDigital`
**Motor de carga:** `src/schema/dimensions.py` y `src/schema/facts.py` vía SQLAlchemy + PyODBC

## Por qué Copo de Nieve y no Estrella

El equipo eligió el esquema copo de nieve (snowflake) sobre el esquema estrella por razones técnicas:

| Criterio | Esquema Estrella | Esquema Copo de Nieve (elegido) |
|---|---|---|
| Redundancia de datos | Alta (datos repetidos en dimensiones) | Baja (normalización elimina repetición) |
| Integridad referencial | Débil (datos desnormalizados) | Fuerte (FKs entre dimensiones) |
| Mantenimiento | Difícil (actualizar = múltiples filas) | Simple (actualizar = una fila) |
| Complejidad de consultas | Menor (menos JOINs) | Mayor (JOINs adicionales) |
| Adecuado para este proyecto | No — datos de categorías y regiones se repiten | Sí — volumen manejable, necesidad de consistencia |

En este proyecto, `DIM_HABILIDAD` contiene registros que comparten la misma `NombreCategoria`, y `DIM_MERCADO_LABORAL` agrupa vacantes de la misma `Region`. La normalización evita inconsistencias que comprometerían los KPIs.

---

## Diagrama

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

---

## Tabla de Hechos

### FACT_INSERCION_LABORAL

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Tiempo | INT FK | Surrogate key → DIM_TIEMPO |
| SK_Region | INT FK | Surrogate key → DIM_REGION |
| SK_Carrera | INT FK | Surrogate key → DIM_CARRERA |
| SK_Estudiante | INT FK | Surrogate key → DIM_ESTUDIANTE |
| SK_MercadoLaboral | INT FK | Surrogate key → DIM_MERCADO_LABORAL |
| EstaEmpleado | INT | 1 si el egresado tiene empleo formal |
| SalarioMensualUSD | DECIMAL(10,2) | Salario mensual en USD (0 si sin empleo) |
| TrabajaEnAreaDeEstudio | BIT | 1 si trabaja en su área de formación |

---

## Dimensiones

### DIM_ESTUDIANTE

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Estudiante | INT PK | Surrogate key |
| EstudianteID | INT | Business key (ID original en Bronze) |
| nombre | NVARCHAR | Nombre completo (normalizado a minúsculas) |
| Genero | CHAR(1) | M / F |
| ciudad_residencia | NVARCHAR | Ciudad estandarizada (ej. Santa Cruz de la Sierra) |

### DIM_CARRERA

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Carrera | INT PK | Surrogate key |
| CarreraID | INT | Business key (ID original en Bronze) |
| nombrecarrera | NVARCHAR | Nombre de la carrera (normalizado) |
| area | NVARCHAR | Facultad o área de conocimiento |

### DIM_HABILIDAD

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Habilidad | INT PK | Surrogate key |
| NombreHabilidad | NVARCHAR | Nombre de la competencia digital (ej. Python, SQL) |
| SK_Categoria | INT FK | Surrogate key → DIM_CATEGORIA_SKILL |

### DIM_CATEGORIA_SKILL

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Categoria | INT PK | Surrogate key |
| NombreCategoria | NVARCHAR | Nivel de competencia: Básico / Intermedio / Avanzado |

> Sub-dimensión de `DIM_HABILIDAD`. Agrupa las 22 competencias digitales por nivel de dificultad.

### DIM_TIEMPO

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Tiempo | INT PK | Surrogate key |
| anio | INT | Año de ingreso (2020–2024) |
| trimestre | INT | Trimestre (valor por defecto: 1) |
| mes | INT | Mes (valor por defecto: 1) |
| Semestre | INT | Semestre (valor por defecto: 1) |

### DIM_MERCADO_LABORAL

| Columna | Tipo | Descripción |
|---|---|---|
| SK_MercadoLaboral | INT PK | Surrogate key |
| Ubicacion | NVARCHAR | Ciudad de la vacante (fuente: Adzuna API) |

### DIM_REGION

| Columna | Tipo | Descripción |
|---|---|---|
| SK_Region | INT PK | Surrogate key |
| Ciudad | NVARCHAR | Ciudad boliviana estandarizada |
| Region | NVARCHAR | Clasificación: Nacional / Remoto |

> Sub-dimensión de `DIM_MERCADO_LABORAL`. Normaliza la información geográfica.

---

## Fuentes de datos por dimensión

| Dimensión / Tabla | Fuente Bronze | Archivo Silver |
|---|---|---|
| DIM_ESTUDIANTE | `BrechaDigitalDB.Estudiantes` | `silver_integrated_data.csv` |
| DIM_CARRERA | `BrechaDigitalDB.Carreras` | `carreras_cleaned.csv` |
| DIM_HABILIDAD | `BrechaDigitalDB.CompetenciasDigitales` | `competenciasdigitales_cleaned.csv` |
| DIM_CATEGORIA_SKILL | `BrechaDigitalDB.CompetenciasDigitales` | `competenciasdigitales_cleaned.csv` |
| DIM_TIEMPO | Derivada de fechas de ingreso | `silver_integrated_data.csv` |
| DIM_MERCADO_LABORAL | Adzuna REST API | `empleos/vacantes_tecnologicas_cleaned.csv` |
| DIM_REGION | `Estudiantes` + Adzuna | `silver_integrated_data.csv` + vacantes |
| FACT_INSERCION_LABORAL | Join completo Silver | `silver_integrated_data.csv` + `seguimientoegresados_cleaned.csv` |
