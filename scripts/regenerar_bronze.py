"""
regenerar_bronze.py
-------------------
Regenera los CSVs de Bronze con los datos actualizados según los cambios en seed.sql.

Cambios aplicados:
  - inscripciones.csv: NotaFinal en [20, 100] con 5% NULLs
  - estudiantes.csv: ~15% de ciudades con inconsistencias de casing/abreviatura
  - seguimientoegresados.csv: 50,000 filas con distribución de empleo por carrera
"""

import csv
import random
from pathlib import Path

random.seed(42)

BASE = Path(__file__).resolve().parent.parent / "data" / "raw"

# ---------------------------------------------------------------------------
# PASO 1: Leer inscripciones actual para derivar EstudianteID -> CarreraID
# ---------------------------------------------------------------------------
print("Leyendo inscripciones.csv actual para mapeo EstudianteID → CarreraID...")

estudiante_carrera = {}  # EstudianteID (int) -> CarreraID (int)
inscripciones_rows = []  # todos los datos para regenerar después

with open(BASE / "inscripciones.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        eid = int(row["EstudianteID"])
        cid = int(row["CarreraID"])
        inscripciones_rows.append(row)
        # Si tiene múltiples inscripciones, usar la primera (orden de lectura)
        if eid not in estudiante_carrera:
            estudiante_carrera[eid] = cid

print(f"  Mapeados {len(estudiante_carrera)} estudiantes a su CarreraID.")

# ---------------------------------------------------------------------------
# PASO 2: Regenerar inscripciones.csv
#         NotaFinal: (% 81) + 20 = rango [20, 100], 5% NULLs
# ---------------------------------------------------------------------------
print("\nRegenerando inscripciones.csv...")

semestres_validos = list(range(1, 11))  # 1-10

with open(BASE / "inscripciones.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["InscripcionID", "EstudianteID", "CarreraID", "NotaFinal", "SemestreActual"])

    for i, row in enumerate(inscripciones_rows):
        insc_id = row["InscripcionID"]
        est_id = row["EstudianteID"]
        carr_id = row["CarreraID"]
        semestre = row["SemestreActual"]

        # 5% de NULLs intencionales en NotaFinal
        if random.random() < 0.05:
            nota = ""
        else:
            nota = round(random.randint(0, 80) + 20, 2)  # [20, 100]
            # Agregar decimales para realismo como el original
            nota = round(random.uniform(20.0, 100.0), 2)

        writer.writerow([insc_id, est_id, carr_id, nota, semestre])

print(f"  inscripciones.csv regenerado con {len(inscripciones_rows)} filas.")

# ---------------------------------------------------------------------------
# PASO 3: Regenerar estudiantes.csv con ~15% ciudades inconsistentes
# ---------------------------------------------------------------------------
print("\nRegenerando estudiantes.csv...")

# Variantes inconsistentes por ciudad
ciudad_variantes_inconsistentes = {
    "La Paz":      ["la paz", "LA PAZ", "la paz"],
    "Cochabamba":  ["Cbba.", "cochabamba", "COCHABAMBA", "Cbba."],
    "Santa Cruz":  ["santa cruz", "SANTA CRUZ", "santa cruz"],
    "Sucre":       ["SUCRE", "sucre", "SUCRE"],
    "Tarija":      ["tarija", "TARIJA", "tarija"],
    "Oruro":       ["oruro", "ORURO"],
    "Potosi":      ["potosi", "POTOSI"],
    "Trinidad":    ["trinidad"],
    "Cobija":      ["cobija"],
}

estudiantes_rows = []
with open(BASE / "estudiantes.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        estudiantes_rows.append(row)

with open(BASE / "estudiantes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["EstudianteID", "Nombre", "FechaIngreso", "Genero", "Ciudad"])

    inconsistentes_count = 0
    for row in estudiantes_rows:
        ciudad_original = row["Ciudad"]

        # ~15% de registros reciben una variante inconsistente
        if random.random() < 0.15 and ciudad_original in ciudad_variantes_inconsistentes:
            variantes = ciudad_variantes_inconsistentes[ciudad_original]
            ciudad = random.choice(variantes)
            inconsistentes_count += 1
        else:
            ciudad = ciudad_original

        writer.writerow([
            row["EstudianteID"],
            row["Nombre"],
            row["FechaIngreso"],
            row["Genero"],
            ciudad,
        ])

print(f"  estudiantes.csv regenerado con {len(estudiantes_rows)} filas.")
print(f"  Ciudades inconsistentes introducidas: {inconsistentes_count} ({inconsistentes_count/len(estudiantes_rows)*100:.1f}%)")

# ---------------------------------------------------------------------------
# PASO 4: Regenerar seguimientoegresados.csv para los 50,000 estudiantes
# ---------------------------------------------------------------------------
print("\nRegenerando seguimientoegresados.csv (50,000 filas)...")

# Distribución por carrera: (tasa_empleo, salario_min, salario_max)
CARRERA_CONFIG = {
    1: (0.82, 900,  1400),  # Ing. Sistemas
    2: (0.75, 850,  1300),  # Electrónica
    3: (0.68, 700,  1100),  # Administración
    4: (0.57, 550,   900),  # Diseño Gráfico
    5: (0.63, 650,  1050),  # Derecho
}
# Default para cualquier CarreraID no listado
CARRERA_DEFAULT = (0.65, 600, 1000)

# Determinar el set de 50,000 estudiantes (todos los IDs del mapeo)
# Si hay menos de 50,000 en el mapeo, generamos secuencial igual
todos_estudiantes = sorted(estudiante_carrera.keys())
assert len(todos_estudiantes) == 50000, f"Se esperaban 50000 estudiantes, hay {len(todos_estudiantes)}"

with open(BASE / "seguimientoegresados.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["EgresadoID", "EstudianteID", "TieneEmpleoFormal", "SalarioMensualUSD", "TrabajaEnAreaDeEstudio"])

    for egresado_id, estudiante_id in enumerate(todos_estudiantes, start=1):
        carrera_id = estudiante_carrera.get(estudiante_id, 1)
        tasa, sal_min, sal_max = CARRERA_CONFIG.get(carrera_id, CARRERA_DEFAULT)

        # 5% de NULLs en TieneEmpleoFormal
        if random.random() < 0.05:
            tiene_empleo = ""
            salario = ""
            trabaja_area = False
        else:
            tiene_empleo = random.random() < tasa

            if tiene_empleo:
                salario = round(random.uniform(sal_min, sal_max), 2)
                trabaja_area = random.random() < 0.65  # 65% trabaja en su área
            else:
                salario = ""
                trabaja_area = False

        writer.writerow([egresado_id, estudiante_id, tiene_empleo, salario, trabaja_area])

print("  seguimientoegresados.csv regenerado con 50,000 filas.")

# ---------------------------------------------------------------------------
# VERIFICACIÓN FINAL
# ---------------------------------------------------------------------------
print("\n=== VERIFICACIÓN ===")

for filename in ["inscripciones.csv", "estudiantes.csv", "seguimientoegresados.csv"]:
    with open(BASE / filename, newline="") as f:
        rows = list(csv.reader(f))
    print(f"  {filename}: {len(rows)-1} filas, columnas: {rows[0]}")

# Verificar rango NotaFinal en inscripciones
print("\n  Verificando NotaFinal en inscripciones.csv...")
notas = []
nulls = 0
with open(BASE / "inscripciones.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        v = row["NotaFinal"]
        if v == "":
            nulls += 1
        else:
            notas.append(float(v))

print(f"    NULLs: {nulls} ({nulls/50000*100:.1f}%)")
print(f"    NotaFinal min={min(notas):.2f}, max={max(notas):.2f}")

# Distribución de ciudades inconsistentes
print("\n  Distribución de ciudades en estudiantes.csv...")
ciudades_count = {}
with open(BASE / "estudiantes.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        c = row["Ciudad"]
        ciudades_count[c] = ciudades_count.get(c, 0) + 1

ciudades_ordenadas = sorted(ciudades_count.items(), key=lambda x: -x[1])
for ciudad, count in ciudades_ordenadas[:20]:
    print(f"    {ciudad!r}: {count}")

# NULLs en seguimientoegresados
print("\n  NULLs en TieneEmpleoFormal (seguimientoegresados.csv)...")
nulls_empleo = 0
with open(BASE / "seguimientoegresados.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["TieneEmpleoFormal"] == "":
            nulls_empleo += 1
print(f"    NULLs TieneEmpleoFormal: {nulls_empleo} ({nulls_empleo/50000*100:.1f}%)")

print("\nDone.")
