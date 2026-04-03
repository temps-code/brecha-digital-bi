"""
Schema — Fact Table (Gold Layer)
Responsable: Micaela Pérez Vásquez

Carga la tabla de hechos del esquema copo de nieve en SQLite:
  - FACT_INSERCION_LABORAL

Depende de que dimensions.py haya sido ejecutado primero.
Ver docs/esquema_copo_nieve.md para la definición completa.
"""

import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. Cargar configuración y conectar a la BD Gold ---
load_dotenv()

DW_SERVER = os.getenv('DW_SERVER')
DW_NAME = os.getenv('DW_NAME')
DW_USER = os.getenv('DW_USER')
DW_PASSWORD = os.getenv('DW_PASSWORD')

connection_string = f"mssql+pyodbc://{DW_USER}:{DW_PASSWORD}@{DW_SERVER}/{DW_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)

# Dentro de src/schema/facts.py
# Dentro de src/schema/facts.py

# Dentro de src/schema/facts.py

# Dentro de src/schema/facts.py
def _validar_fact_table(df: pd.DataFrame, nombre_tabla: str):
    """
    Valida la integridad de la tabla de hechos.
    La validación más crítica es que no haya claves foráneas nulas.
    """
    print(f"   🔍 Ejecutando validaciones para {nombre_tabla}...")
    try:
        # 1. La tabla no debe estar vacía
        assert not df.empty, f"ERROR: La tabla {nombre_tabla} está vacía."
        
        # 2. Las claves foráneas (columnas SK_) no deben ser nulas.
        # Un nulo indica que el lookup falló para ese registro.
        fk_cols = [col for col in df.columns if col.startswith('SK_')]
        for col in fk_cols:
            nulls_count = df[col].isna().sum()
            assert nulls_count == 0, f"ERROR: La columna de FK '{col}' en {nombre_tabla} contiene {nulls_count} valores nulos. El lookup falló para estos registros."
            
        print(f"   ✅ Validaciones para {nombre_tabla} superadas.")
    except AssertionError as e:
        print(f"❌ {e}")
        # Si una validación falla, es mejor detener el proceso para no cargar datos corruptos.
        raise
    
def cargar_fact_insercion_laboral():
    """Crea la tabla de hechos combinando inscripciones y datos de seguimiento de egresados."""
    print("Cargando FACT_INSERCION_LABORAL...")
    
    # 1. Cargar el archivo de inscripciones principal
    df_inscripciones = pd.read_csv('data/processed/silver_integrated_data.csv')
    df_inscripciones['mes'] = 1
    
    # 2. Cargar el archivo de seguimiento de egresados (FORMA ROBUSTA)
    try:
        print("   📂 Leyendo seguimientoegresados_cleaned.csv...")
        df_empleo = pd.read_csv(
            'data/processed/seguimientoegresados_cleaned.csv',
            dtype={
                'TieneEmpleoFormal': 'boolean',
                'TrabajaEnAreaDeEstudio': 'boolean' # <-- FORZAMOS EL TIPO AQUÍ
            },
            true_values=['True'],
            false_values=['False']
        )
        print("   ✅ Archivo leído. Tipos de datos:")
        print(df_empleo[['TieneEmpleoFormal', 'TrabajaEnAreaDeEstudio']].dtypes)
        print("\n   Valores únicos en 'TrabajaEnAreaDeEstudio' después de leer:")
        print(df_empleo['TrabajaEnAreaDeEstudio'].value_counts(dropna=False))

    except FileNotFoundError:
        print("   ❌ ERROR CRÍTICO: No se encontró el archivo 'data/processed/seguimientoegresados_cleaned.csv'.")
        raise

    # 3. Combinar (merge) ambos DataFrames
    print("\n   🔗 Combinando datos...")
    df_fact = pd.merge(df_inscripciones, df_empleo, on='EstudianteID', how='left')
    
    # --- DEPURACIÓN 1: ¿Cómo se ve la columna DESPUÉS del merge? ---
    print("\n   🔍 [DEBUG 1] Estado de 'TrabajaEnAreaDeEstudio' DESPUÉS del merge:")
    print(df_fact['TrabajaEnAreaDeEstudio'].value_counts(dropna=False))
    
    # 4. Calcular las medidas y limpiar datos
    print("\n   🧹 Limpiando y calculando medidas...")
    
    # Limpieza para 'TrabajaEnAreaDeEstudio'
    # Como forzamos el tipo, los NaN son el único problema.
    df_fact['TrabajaEnAreaDeEstudio'] = df_fact['TrabajaEnAreaDeEstudio'].fillna(False)
    
    # --- DEPURACIÓN 2: ¿Cómo se ve la columna DESPUÉS de la limpieza? ---
    print("\n   🔍 [DEBUG 2] Estado de 'TrabajaEnAreaDeEstudio' DESPUÉS de .fillna(False):")
    print(df_fact['TrabajaEnAreaDeEstudio'].value_counts(dropna=False))

    # Limpieza para las otras columnas (tu código original)
    df_fact['TieneEmpleoFormal'] = df_fact['TieneEmpleoFormal'].fillna(False)
    df_fact['EstaEmpleado'] = df_fact['TieneEmpleoFormal'].astype(int)
    df_fact['SalarioMensualUSD'] = df_fact['SalarioMensualUSD'].fillna(0)

    # 5. Obtener las claves surrogate (SK) de las tablas de dimensión
    # (Este código no debería afectar la columna, pero lo mantenemos)
    sk_tiempo = pd.read_sql('SELECT SK_Tiempo, anio, mes FROM DIM_TIEMPO', con=engine)
    sk_region = pd.read_sql('SELECT SK_Region, Ciudad, Region FROM DIM_REGION', con=engine)
    sk_carrera = pd.read_sql('SELECT SK_Carrera, CarreraID FROM DIM_CARRERA', con=engine)
    sk_estudiante = pd.read_sql('SELECT SK_Estudiante, EstudianteID FROM DIM_ESTUDIANTE', con=engine)
    sk_mercado = pd.read_sql('SELECT SK_MercadoLaboral, Ubicacion FROM DIM_MERCADO_LABORAL', con=engine)

    # 6. Crear una clave de combinación para la dimensión de tiempo
    df_fact['tiempo_key'] = df_fact['anio_x'].astype(str) + '_' + df_fact['mes'].astype(str)
    sk_tiempo['tiempo_key'] = sk_tiempo['anio'].astype(str) + '_' + sk_tiempo['mes'].astype(str)

    # 7. Unir las claves surrogate
    df_fact = pd.merge(df_fact, sk_tiempo[['SK_Tiempo', 'tiempo_key']], on='tiempo_key', how='left')
    df_fact = df_fact.drop(columns=['tiempo_key'])
    df_fact = pd.merge(df_fact, sk_region, on='Ciudad')
    df_fact = pd.merge(df_fact, sk_carrera, on='CarreraID')
    df_fact = pd.merge(df_fact, sk_estudiante, on='EstudianteID')
    df_fact = pd.merge(df_fact, sk_mercado, left_on='Ciudad', right_on='Ubicacion')

    # 8. Seleccionar y ordenar las columnas finales
    df_fact_final = df_fact[[
        'SK_Tiempo', 'SK_Region', 'SK_Carrera', 'SK_Estudiante', 'SK_MercadoLaboral',
        'EstaEmpleado', 'SalarioMensualUSD', 'TrabajaEnAreaDeEstudio'
    ]].drop_duplicates().reset_index(drop=True)

    # --- DEPURACIÓN 3: ¿Cómo se ve la columna en el DataFrame FINAL? ---
    print("\n   🔍 [DEBUG 3] Estado de 'TrabajaEnAreaDeEstudio' en df_fact_final (antes de guardar):")
    print(df_fact_final['TrabajaEnAreaDeEstudio'].value_counts(dropna=False))

    # 9. Cargar la tabla de hechos en la base de datos
    print("\n   💾 Guardando en la base de datos...")
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