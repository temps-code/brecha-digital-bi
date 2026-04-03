"""
Schema — Fact Table (Gold Layer)
Responsable: Micaela Pérez Vásquez

Carga la tabla de hechos del esquema copo de nieve en SQLite:
  - FACT_INSERCION_LABORAL

Depende de que dimensions.py haya sido ejecutado primero.
Ver docs/esquema_copo_nieve.md para la definición completa.
"""

import pandas as pd

from .db import get_engine

def _validar_fact_table(df: pd.DataFrame, nombre_tabla: str):
    """Valida la integridad de la tabla de hechos."""
    print(f"   🔍 Ejecutando validaciones para {nombre_tabla}...")
    try:
        assert not df.empty, f"ERROR: La tabla {nombre_tabla} está vacía."
        
        fk_cols = [col for col in df.columns if col.startswith('SK_')]
        for col in fk_cols:
            nulls_count = df[col].isna().sum()
            assert nulls_count == 0, f"ERROR: La columna de FK '{col}' en {nombre_tabla} contiene {nulls_count} valores nulos. El lookup falló."
            
        print(f"   ✅ Validaciones para {nombre_tabla} superadas.")
    except AssertionError as e:
        print(f"❌ {e}")
        raise ValueError(f"La validación de la tabla de hechos {nombre_tabla} falló.") from e

def cargar_fact_insercion_laboral():
    """Crea la tabla de hechos combinando inscripciones y datos de seguimiento de egresados."""
    print("Cargando FACT_INSERCION_LABORAL...")
    
    df_inscripciones = pd.read_csv('data/processed/silver_integrated_data.csv')
    df_inscripciones['mes'] = 1
    
    try:
        df_empleo = pd.read_csv(
            'data/processed/seguimientoegresados_cleaned.csv',
            dtype={'TieneEmpleoFormal': 'boolean', 'TrabajaEnAreaDeEstudio': 'boolean'},
            true_values=['True'], false_values=['False']
        )
    except FileNotFoundError:
        raise ValueError("No se encontró el archivo de seguimiento de egresados. Verifica la ruta.") from None

    df_fact = pd.merge(df_inscripciones, df_empleo, on='EstudianteID', how='left')
    
    # Limpiar y calcular medidas
    df_fact['TrabajaEnAreaDeEstudio'] = df_fact['TrabajaEnAreaDeEstudio'].fillna(False)
    df_fact['TieneEmpleoFormal'] = df_fact['TieneEmpleoFormal'].fillna(False)
    df_fact['EstaEmpleado'] = df_fact['TieneEmpleoFormal'].astype(int)
    df_fact['SalarioMensualUSD'] = df_fact['SalarioMensualUSD'].fillna(0)

    # Obtener las claves surrogate (SK) de las tablas de dimensión
    engine = get_engine()
    sk_tiempo = pd.read_sql('SELECT SK_Tiempo, anio, mes FROM DIM_TIEMPO', con=engine)
    sk_region = pd.read_sql('SELECT SK_Region, Ciudad, Region FROM DIM_REGION', con=engine)
    sk_carrera = pd.read_sql('SELECT SK_Carrera, CarreraID FROM DIM_CARRERA', con=engine)
    sk_estudiante = pd.read_sql('SELECT SK_Estudiante, EstudianteID FROM DIM_ESTUDIANTE', con=engine)
    sk_mercado = pd.read_sql('SELECT SK_MercadoLaboral, Ubicacion FROM DIM_MERCADO_LABORAL', con=engine)

    # Crear una clave de combinación para la dimensión de tiempo
    df_fact['tiempo_key'] = df_fact['anio_x'].astype(str) + '_' + df_fact['mes'].astype(str)
    sk_tiempo['tiempo_key'] = sk_tiempo['anio'].astype(str) + '_' + sk_tiempo['mes'].astype(str)

    # Unir las claves surrogate
    df_fact = pd.merge(df_fact, sk_tiempo[['SK_Tiempo', 'tiempo_key']], on='tiempo_key', how='left')
    df_fact = df_fact.drop(columns=['tiempo_key'])
    df_fact = pd.merge(df_fact, sk_region, on='Ciudad')
    df_fact = pd.merge(df_fact, sk_carrera, on='CarreraID')
    df_fact = pd.merge(df_fact, sk_estudiante, on='EstudianteID')
    df_fact = pd.merge(df_fact, sk_mercado, left_on='Ciudad', right_on='Ubicacion')

    # Seleccionar y ordenar las columnas finales
    df_fact_final = df_fact[[
        'SK_Tiempo', 'SK_Region', 'SK_Carrera', 'SK_Estudiante', 'SK_MercadoLaboral',
        'EstaEmpleado', 'SalarioMensualUSD', 'TrabajaEnAreaDeEstudio'
    ]].drop_duplicates().reset_index(drop=True)

    # Cargar la tabla de hechos en la base de datos
    df_fact_final.to_sql('FACT_INSERCION_LABORAL', con=engine, if_exists='replace', index=False)
    print(f"   ✅ FACT_INSERCION_LABORAL cargada con {len(df_fact_final)} registros.")
    _validar_fact_table(df_fact_final, 'FACT_INSERCION_LABORAL')

def main():
    """Función principal que ejecuta la carga de la tabla de hechos."""
    print("--- INICIANDO CARGA DE TABLA DE HECHOS (CAPA GOLD) ---")
    try:
        cargar_fact_insercion_laboral()
        print("--- TABLA DE HECHOS CARGADA EXITOSAMENTE ---")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO durante la carga de la tabla de hechos: {e}")

if __name__ == "__main__":
    main()