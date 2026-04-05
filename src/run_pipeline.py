"""
Pipeline Orchestrator — Bronze → Silver → Gold
Ejecuta las 4 etapas del pipeline de datos en orden:
  1. Ingestion   (Bronze) — extrae CSVs desde SQL Server y APIs externas
  2. Clean       (Silver) — limpieza y normalización de tipos
  3. Normalize   (Silver) — estandarización geográfica y vista unificada
  4. Schema      (Gold)   — carga dimensiones y tabla de hechos en DW

Uso:
    python -m src.run_pipeline
    python -m src.run_pipeline --skip-ingestion
"""
import argparse
import time


def _run_stage(name: str, fn):
    """Ejecuta una etapa con timing e imprime resultado."""
    print(f"\n{'='*50}")
    print(f"[INICIO] {name}")
    print(f"{'='*50}")
    t0 = time.time()
    fn()
    elapsed = time.time() - t0
    print(f"[FIN] {name} — {elapsed:.1f}s")


def stage_ingestion():
    from ingestion.sqlserver import extract_to_raw
    from ingestion.empleos import fetch_adzuna_jobs_mock
    from ingestion.cepalstat import fetch_cepal_data

    extract_to_raw()
    fetch_adzuna_jobs_mock()
    fetch_cepal_data()


def stage_clean():
    import os
    from transform.clean import procesar_archivo

    archivos = [
        'estudiantes.csv',
        'inscripciones.csv',
        'seguimientoegresados.csv',
        'carreras.csv',
        'competenciasdigitales.csv',
        'empleos/vacantes_tecnologicas.csv',
        'cepalstat/indicadores_tic_region.csv',
    ]
    for archivo in archivos:
        procesar_archivo(archivo)


def stage_normalize():
    import os
    from transform.normalize import normalizar_archivo, crear_vista_unificada

    processed_path = 'data/processed'
    archivos = [f for f in os.listdir(processed_path) if f.endswith('_cleaned.csv')]
    if not archivos:
        raise RuntimeError(
            'No se encontraron archivos *_cleaned.csv. '
            'Asegurate de ejecutar la etapa Clean primero.'
        )
    for archivo in archivos:
        normalizar_archivo(archivo)
    crear_vista_unificada()


def stage_schema():
    from schema.dimensions import main as load_dimensions
    from schema.facts import main as load_facts

    load_dimensions()
    load_facts()


def main():
    parser = argparse.ArgumentParser(
        description='Orquestador del pipeline de datos Brecha Digital BI'
    )
    parser.add_argument(
        '--skip-ingestion',
        action='store_true',
        help='Omite la etapa de ingesta (útil cuando los CSVs raw ya existen)',
    )
    args = parser.parse_args()

    stages = [
        ('Etapa 1 — Ingestion (Bronze)', stage_ingestion, not args.skip_ingestion),
        ('Etapa 2 — Clean (Silver)',     stage_clean,     True),
        ('Etapa 3 — Normalize (Silver)', stage_normalize, True),
        ('Etapa 4 — Schema (Gold)',      stage_schema,    True),
    ]

    print("\n*** PIPELINE BRECHA DIGITAL BI ***")
    if args.skip_ingestion:
        print("INFO: --skip-ingestion activo, se omite la Etapa 1.")

    t_total = time.time()
    for name, fn, enabled in stages:
        if not enabled:
            print(f"\n[SKIP] {name}")
            continue
        try:
            _run_stage(name, fn)
        except Exception as exc:
            print(f"\n[ERROR CRITICO] {name} falló: {exc}")
            raise SystemExit(1) from exc

    elapsed_total = time.time() - t_total
    print(f"\n{'='*50}")
    print(f"PIPELINE COMPLETO — {elapsed_total:.1f}s totales")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    main()
