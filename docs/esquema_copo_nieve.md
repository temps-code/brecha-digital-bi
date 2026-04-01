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

En este proyecto, `DIM_HABILIDAD` contiene cientos de registros que comparten la misma `categoria`, y `DIM_MERCADO_LABORAL` agrupa vacantes de la misma `region`. La normalización evita inconsistencias que comprometerían los KPIs.

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

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_hecho | INT IDENTITY PK | Clave primaria |
| id_estudiante | INT FK | Referencia a DIM_ESTUDIANTE |
| id_habilidad | INT FK | Referencia a DIM_HABILIDAD |
| id_tiempo | INT FK | Referencia a DIM_TIEMPO |
| id_mercado | INT FK | Referencia a DIM_MERCADO_LABORAL |
| insertado_laboralmente | BIT | 1 si el egresado consiguió empleo en su área |
| meses_hasta_empleo | INT | Meses transcurridos desde graduación hasta empleo |
| salario_inicial | DECIMAL(10,2) | Salario inicial obtenido (BOB) |
| match_skill | DECIMAL(5,2) | % de coincidencia entre skills del egresado y vacante |

---

## Dimensiones

### DIM_ESTUDIANTE

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_estudiante | INT IDENTITY PK | Clave primaria |
| id_carrera | INT FK | Referencia a DIM_CARRERA |
| nombre | NVARCHAR(150) | Nombre completo |
| anio_ingreso | INT | Año de ingreso a la institución |
| anio_egreso | INT NULL | Año de egreso (NULL si aún activo) |
| promedio_general | DECIMAL(4,2) | Promedio académico final |
| desertor | BIT | 1 si abandonó los estudios |

### DIM_CARRERA

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_carrera | INT IDENTITY PK | Clave primaria |
| nombre_carrera | NVARCHAR(100) | Nombre de la carrera técnica |
| duracion_anios | INT | Duración en años |
| area | NVARCHAR(60) | Área: TIC, Salud, Administración, etc. |

### DIM_HABILIDAD

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_habilidad | INT IDENTITY PK | Clave primaria |
| id_categoria | INT FK | Referencia a DIM_CATEGORIA_SKILL |
| nombre_habilidad | NVARCHAR(100) | Nombre de la habilidad (ej. Python, Excel, SQL) |
| nivel | NVARCHAR(20) | Básica / Intermedia / Avanzada |

### DIM_CATEGORIA_SKILL

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_categoria | INT IDENTITY PK | Clave primaria |
| nombre_categoria | NVARCHAR(60) | Categoría: Programación, Ofimática, Redes, Gestión, etc. |

> Sub-dimensión de `DIM_HABILIDAD`. Normaliza las categorías de habilidades para evitar repetición y facilitar actualizaciones masivas.

### DIM_TIEMPO

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_tiempo | INT IDENTITY PK | Clave primaria |
| fecha | DATE | Fecha completa |
| anio | INT | Año |
| trimestre | INT | Trimestre (1-4) |
| mes | INT | Mes (1-12) |

### DIM_MERCADO_LABORAL

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_mercado | INT IDENTITY PK | Clave primaria |
| id_region | INT FK | Referencia a DIM_REGION |
| nombre_empresa | NVARCHAR(150) | Empresa que publicó la vacante (fuente: Adzuna API) |
| sector | NVARCHAR(80) | Sector económico |
| tipo_contrato | NVARCHAR(30) | Tiempo completo / Parcial / Freelance |
| fuente | NVARCHAR(20) | Origen del dato: 'adzuna' / 'interno' |

### DIM_REGION

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_region | INT IDENTITY PK | Clave primaria |
| ciudad | NVARCHAR(80) | Ciudad boliviana |
| departamento | NVARCHAR(60) | Departamento (Santa Cruz, La Paz, Cochabamba, etc.) |
| zona | NVARCHAR(40) | Zona geográfica |

> Sub-dimensión de `DIM_MERCADO_LABORAL`. Normaliza la información geográfica para evitar inconsistencias entre vacantes de la misma región.

---

## Fuentes de datos por dimensión

| Dimensión / Tabla | Fuente Bronze |
|---|---|
| DIM_ESTUDIANTE | SQL Server `BrechaDigitalDB` |
| DIM_CARRERA | SQL Server `BrechaDigitalDB` |
| DIM_HABILIDAD | SQL Server `BrechaDigitalDB` |
| DIM_CATEGORIA_SKILL | SQL Server `BrechaDigitalDB` |
| DIM_TIEMPO | Generada en transformación Silver |
| DIM_MERCADO_LABORAL | Adzuna REST API |
| DIM_REGION | SQL Server `BrechaDigitalDB` + CEPALSTAT |
| FACT_INSERCION_LABORAL | Join integrado Silver (todas las fuentes anteriores) |
