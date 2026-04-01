# Esquema Copo de Nieve — Documentación

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
| id_hecho | INTEGER PK | Clave primaria |
| id_estudiante | INTEGER FK | Referencia a DIM_ESTUDIANTE |
| id_habilidad | INTEGER FK | Referencia a DIM_HABILIDAD |
| id_tiempo | INTEGER FK | Referencia a DIM_TIEMPO |
| id_mercado | INTEGER FK | Referencia a DIM_MERCADO_LABORAL |
| insertado_laboralmente | BOOLEAN | Si el egresado consiguió empleo en su área |
| meses_hasta_empleo | INTEGER | Meses transcurridos desde graduación hasta empleo |
| salario_inicial | DECIMAL | Salario inicial obtenido (BOB) |
| match_skill | DECIMAL | % de coincidencia entre skills del egresado y vacante |

---

## Dimensiones

### DIM_ESTUDIANTE

| Columna | Tipo | Descripción |
|---|---|---|
| id_estudiante | INTEGER PK | Clave primaria |
| id_carrera | INTEGER FK | Referencia a DIM_CARRERA |
| nombre | VARCHAR | Nombre completo |
| anio_ingreso | INTEGER | Año de ingreso a la institución |
| anio_egreso | INTEGER | Año de egreso (NULL si aún activo) |
| promedio_general | DECIMAL | Promedio académico final |
| desertor | BOOLEAN | Si abandonó los estudios |

### DIM_CARRERA

| Columna | Tipo | Descripción |
|---|---|---|
| id_carrera | INTEGER PK | Clave primaria |
| nombre_carrera | VARCHAR | Nombre de la carrera técnica |
| duracion_anios | INTEGER | Duración en años |
| area | VARCHAR | Area: TIC, Salud, Administración, etc. |

### DIM_HABILIDAD

| Columna | Tipo | Descripción |
|---|---|---|
| id_habilidad | INTEGER PK | Clave primaria |
| id_categoria | INTEGER FK | Referencia a DIM_CATEGORIA_SKILL |
| nombre_habilidad | VARCHAR | Nombre de la habilidad (ej. Python, Excel, SQL) |
| nivel | VARCHAR | Básica / Intermedia / Avanzada |

### DIM_CATEGORIA_SKILL

| Columna | Tipo | Descripción |
|---|---|---|
| id_categoria | INTEGER PK | Clave primaria |
| nombre_categoria | VARCHAR | Categoría (ej. Programación, Ofimática, Redes) |

### DIM_TIEMPO

| Columna | Tipo | Descripción |
|---|---|---|
| id_tiempo | INTEGER PK | Clave primaria |
| fecha | DATE | Fecha completa |
| anio | INTEGER | Año |
| trimestre | INTEGER | Trimestre (1-4) |
| mes | INTEGER | Mes (1-12) |

### DIM_MERCADO_LABORAL

| Columna | Tipo | Descripción |
|---|---|---|
| id_mercado | INTEGER PK | Clave primaria |
| id_region | INTEGER FK | Referencia a DIM_REGION |
| nombre_empresa | VARCHAR | Empresa que publicó la vacante |
| sector | VARCHAR | Sector económico |
| tipo_contrato | VARCHAR | Tiempo completo / Parcial / Freelance |

### DIM_REGION

| Columna | Tipo | Descripción |
|---|---|---|
| id_region | INTEGER PK | Clave primaria |
| ciudad | VARCHAR | Ciudad boliviana |
| departamento | VARCHAR | Departamento (Santa Cruz, La Paz, Cochabamba, etc.) |
| zona | VARCHAR | Zona geográfica |

---

## Por qué Copo de Nieve y no Estrella

El esquema estrella desnormaliza las dimensiones (repite datos). El copo de nieve las normaliza en sub-dimensiones:

- `DIM_ESTUDIANTE` no repite la carrera — la referencia via FK a `DIM_CARRERA`
- `DIM_HABILIDAD` no repite la categoría — la referencia via FK a `DIM_CATEGORIA_SKILL`
- `DIM_MERCADO_LABORAL` no repite la región — la referencia via FK a `DIM_REGION`

Esto elimina redundancia a costa de JOINs adicionales en las consultas. Para este proyecto es la elección correcta dado el volumen de datos y la necesidad de mantener integridad referencial.
