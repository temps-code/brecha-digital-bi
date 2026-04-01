# Esquema Estrella — Documentación

**Almacenamiento:** SQL Server — base de datos `DW_BrechaDigital`
**Motor de carga:** `src/schema/dimensions.py` y `src/schema/facts.py` vía SQLAlchemy + PyODBC

## Diagrama

En el esquema estrella, **todas las dimensiones conectan directamente a la tabla de hechos central**. No hay jerarquías ni FKs entre dimensiones — es la estructura que exige la rúbrica de la actividad.

```
FACT_INSERCION_LABORAL
├──► DIM_ESTUDIANTE
├──► DIM_CARRERA
├──► DIM_HABILIDAD          ← categoría incluida como columna (denormalizado)
├──► DIM_MERCADO_LABORAL    ← región incluida como columna (denormalizado)
└──► DIM_TIEMPO
```

---

## Tabla de Hechos

### FACT_INSERCION_LABORAL

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_hecho | INT IDENTITY PK | Clave primaria |
| id_estudiante | INT FK | Referencia a DIM_ESTUDIANTE |
| id_carrera | INT FK | Referencia a DIM_CARRERA |
| id_habilidad | INT FK | Referencia a DIM_HABILIDAD |
| id_mercado | INT FK | Referencia a DIM_MERCADO_LABORAL |
| id_tiempo | INT FK | Referencia a DIM_TIEMPO |
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
| nombre_habilidad | NVARCHAR(100) | Nombre de la habilidad (ej. Python, Excel, SQL) |
| categoria | NVARCHAR(60) | Categoría: Programación, Ofimática, Redes, etc. |
| nivel | NVARCHAR(20) | Básica / Intermedia / Avanzada |

> `categoria` está denormalizada directamente en esta tabla (en un esquema snowflake sería una FK a DIM_CATEGORIA_SKILL). En estrella se mantiene como columna para evitar JOINs adicionales.

### DIM_MERCADO_LABORAL

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_mercado | INT IDENTITY PK | Clave primaria |
| nombre_empresa | NVARCHAR(150) | Empresa que publicó la vacante (fuente: Adzuna API) |
| sector | NVARCHAR(80) | Sector económico |
| tipo_contrato | NVARCHAR(30) | Tiempo completo / Parcial / Freelance |
| fuente | NVARCHAR(20) | Origen del dato: 'adzuna' / 'interno' |
| ciudad | NVARCHAR(80) | Ciudad boliviana |
| departamento | NVARCHAR(60) | Departamento (Santa Cruz, La Paz, Cochabamba, etc.) |
| zona | NVARCHAR(40) | Zona geográfica |

> `ciudad`, `departamento` y `zona` están denormalizadas directamente en esta tabla (en snowflake serían una FK a DIM_REGION). En estrella se mantienen como columnas para simplificar las consultas.

### DIM_TIEMPO

| Columna | Tipo T-SQL | Descripción |
|---|---|---|
| id_tiempo | INT IDENTITY PK | Clave primaria |
| fecha | DATE | Fecha completa |
| anio | INT | Año |
| trimestre | INT | Trimestre (1-4) |
| mes | INT | Mes (1-12) |

---

## Por qué Esquema Estrella

La actividad exige explícitamente **Esquema Estrella** ("Modelado de datos — Esquema Estrella en SQL Server"). A diferencia del copo de nieve:

- Todas las dimensiones son planas (sin sub-dimensiones)
- Las consultas son más simples — menos JOINs
- El docente puede verificar el modelo directamente contra la rúbrica

La diferencia con copo de nieve es la denormalización de `categoria` en `DIM_HABILIDAD` y de `region` en `DIM_MERCADO_LABORAL`. Se repite algo de dato pero se elimina complejidad innecesaria para este contexto académico.

---

## Fuentes de datos por dimensión

| Dimensión / Tabla | Fuente Bronze |
|---|---|
| DIM_ESTUDIANTE | SQL Server `BrechaDigitalDB` |
| DIM_CARRERA | SQL Server `BrechaDigitalDB` |
| DIM_HABILIDAD | SQL Server `BrechaDigitalDB` |
| DIM_TIEMPO | Generada en transformación |
| DIM_MERCADO_LABORAL | Adzuna REST API |
| FACT_INSERCION_LABORAL | Join integrado Silver (todas las fuentes) |
