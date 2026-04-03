"""
Schema — Dimension Tables (Gold Layer)
Responsable: Micaela Pérez Vásquez

Carga las tablas de dimensión del esquema copo de nieve en SQLite:
  - DIM_ESTUDIANTE
  - DIM_CARRERA
  - DIM_HABILIDAD
  - DIM_CATEGORIA_SKILL
  - DIM_TIEMPO
  - DIM_MERCADO_LABORAL
  - DIM_REGION

Ver docs/esquema_copo_nieve.md para la definición completa.
"""

import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. Cargar configuración y definir el gestor de conexión ---
load_dotenv()

DW_SERVER = os.getenv('DW_SERVER')
DW_NAME = os.getenv('DW_NAME')
DW_USER = os.getenv('DW_USER')
DW_PASSWORD = os.getenv('DW_PASSWORD')

if not all([DW_SERVER, DW_NAME, DW_USER, DW_PASSWORD]):
    raise ValueError("Faltan variables de entorno para la conexión al Data Warehouse (DW_*)")

# Patrón Singleton para el motor de base de datos
_engine = None

def get_engine():
    """Crea y devuelve una instancia del motor de base de datos."""
    global _engine
    if _engine is None:
        connection_string = f"mssql+pyodbc://{DW_USER}:{DW_PASSWORD}@{DW_SERVER}/{DW_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
        print("   🔗 Creando conexión a la base de datos...")
        _engine = create_engine(connection_string)
    return _engine

def _validar_carga(df: pd.DataFrame, nombre_tabla: str):
    """Función de ayuda para ejecutar validaciones post-carga."""
    print(f"   🔍 Ejecutando validaciones para {nombre_tabla}...")
    try:
        assert not df.empty, f"ERROR: La tabla {nombre_tabla} está vacía después de la carga."
        assert df.duplicated().sum() == 0, f"ERROR: La tabla {nombre_tabla} contiene filas duplicadas."
        
        sk_col = [col for col in df.columns if col.startswith('SK_')][0]
        assert df[sk_col].is_unique, f"ERROR: La clave surrogate {sk_col} en {nombre_tabla} no es única."
        assert df[sk_col].notna().all(), f"ERROR: La clave surrogate {sk_col} en {nombre_tabla} contiene valores nulos."
        
        print(f"   ✅ Validaciones para {nombre_tabla} superadas.")
    except AssertionError as e:
        print(f"❌ {e}")
        raise ValueError(f"La validación de la tabla {nombre_tabla} falló.") from e

# --- 2. Funciones para cargar cada dimensión ---

def cargar_dim_tiempo():
    """Crea la dimensión de tiempo a partir de las columnas de año en los datos integrados."""
    print("Cargando DIM_TIEMPO...")
    df = pd.read_csv('data/processed/silver_integrated_data.csv')
    
    if 'anio_x' not in df.columns:
        raise ValueError("La columna 'anio_x' no se encontró en silver_integrated_data.csv.")
        
    df_tiempo = df[['anio_x']].drop_duplicates().sort_values('anio_x').reset_index(drop=True)
    df_tiempo['SK_Tiempo'] = df_tiempo.index + 1
    
    # Añadimos columnas de granularidad con valores por defecto
    df_tiempo['trimestre'] = 1
    df_tiempo['mes'] = 1
    df_tiempo['Semestre'] = 1
    
    df_tiempo.rename(columns={'anio_x': 'anio'}, inplace=True)
    df_tiempo = df_tiempo[['SK_Tiempo', 'anio', 'trimestre', 'mes', 'Semestre']]
    
    engine = get_engine()
    df_tiempo.to_sql('DIM_TIEMPO', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_TIEMPO cargada con {len(df_tiempo)} registros.")
    _validar_carga(df_tiempo, 'DIM_TIEMPO')

def cargar_dim_region():
    """Crea la dimensión de región a partir de ciudades de estudiantes y vacantes."""
    print("Cargando DIM_REGION...")
    df_estudiantes = pd.read_csv('data/processed/silver_integrated_data.csv')
    df_vacantes = pd.read_csv('data/processed/empleos/vacantes_tecnologicas_cleaned.csv')
    
    ciudades = pd.concat([df_estudiantes['Ciudad'], df_vacantes['location']]).drop_duplicates().to_frame(name='Ciudad')
    ciudades['Region'] = ciudades['Ciudad'].apply(lambda x: 'Remoto' if x == 'remoto' else 'Nacional')
    
    df_region = ciudades.drop_duplicates().reset_index(drop=True)
    df_region['SK_Region'] = df_region.index + 1
    df_region = df_region[['SK_Region', 'Ciudad', 'Region']]
    
    engine = get_engine()
    df_region.to_sql('DIM_REGION', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_REGION cargada con {len(df_region)} registros.")
    _validar_carga(df_region, 'DIM_REGION')

def cargar_dim_carrera():
    """Crea la dimensión de carrera a partir del catálogo de carreras."""
    print("Cargando DIM_CARRERA...")
    try:
        df_carreras = pd.read_csv('data/raw/carreras.csv')
    except FileNotFoundError:
        raise ValueError("No se encontró el archivo 'data/raw/carreras.csv'. Asegúrate de que la ruta sea correcta.") from None

    required_cols = ['CarreraID', 'NombreCarrera', 'Facultad']
    if not all(col in df_carreras.columns for col in required_cols):
        faltantes = [col for col in required_cols if col not in df_carreras.columns]
        raise ValueError(f"El archivo de carreras no contiene las columnas obligatorias: {faltantes}")

    df_carrera = df_carreras[required_cols].drop_duplicates().reset_index(drop=True)
    df_carrera.rename(columns={'NombreCarrera': 'nombrecarrera', 'Facultad': 'area'}, inplace=True)
    df_carrera['SK_Carrera'] = df_carrera.index + 1
    df_carrera = df_carrera[['SK_Carrera', 'CarreraID', 'nombrecarrera', 'area']]
    
    engine = get_engine()
    df_carrera.to_sql('DIM_CARRERA', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_CARRERA cargada con {len(df_carrera)} registros.")
    _validar_carga(df_carrera, 'DIM_CARRERA')

def cargar_dim_estudiante():
    """Crea la dimensión de estudiante a partir de los datos integrados."""
    print("Cargando DIM_ESTUDIANTE...")
    df = pd.read_csv('data/processed/silver_integrated_data.csv')

    required_cols = ['EstudianteID', 'Nombre', 'Genero', 'Ciudad']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"El archivo silver_integrated_data.csv no contiene todas las columnas requeridas: {required_cols}")

    df_estudiante = df[required_cols].drop_duplicates().reset_index(drop=True)
    df_estudiante.rename(columns={'Nombre': 'nombre', 'Ciudad': 'ciudad_residencia'}, inplace=True)
    df_estudiante['SK_Estudiante'] = df_estudiante.index + 1
    df_estudiante = df_estudiante[['SK_Estudiante', 'EstudianteID', 'nombre', 'Genero', 'ciudad_residencia']]
    
    engine = get_engine()
    df_estudiante.to_sql('DIM_ESTUDIANTE', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_ESTUDIANTE cargada con {len(df_estudiante)} registros.")
    _validar_carga(df_estudiante, 'DIM_ESTUDIANTE')

def cargar_dim_mercado_laboral():
    """Crea la dimensión de mercado laboral a partir de datos de vacantes."""
    print("Cargando DIM_MERCADO_LABORAL...")
    try:
        df_vacantes = pd.read_csv('data/processed/empleos/vacantes_tecnologicas_cleaned.csv')
    except FileNotFoundError:
        raise ValueError("No se encontró el archivo de vacantes. Verifica la ruta y el nombre del archivo.") from None

    if 'location' not in df_vacantes.columns:
        raise ValueError("El archivo de vacantes debe contener la columna 'location'.")

    df_ubicaciones = df_vacantes[['location']].drop_duplicates().reset_index(drop=True)
    df_mercado = df_ubicaciones
    df_mercado.rename(columns={'location': 'Ubicacion'}, inplace=True)
    df_mercado['SK_MercadoLaboral'] = df_mercado.index + 1
    df_mercado = df_mercado[['SK_MercadoLaboral', 'Ubicacion']]
    
    engine = get_engine()
    df_mercado.to_sql('DIM_MERCADO_LABORAL', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_MERCADO_LABORAL cargada con {len(df_mercado)} registros únicos.")
    _validar_carga(df_mercado, 'DIM_MERCADO_LABORAL')

def cargar_dim_categoria_y_habilidad():
    """Carga las dimensiones de categoría y habilidad basadas en descripciones de vacantes."""
    print("Cargando DIM_CATEGORIA_SKILL y DIM_HABILIDAD...")
    df_vacantes = pd.read_csv('data/processed/empleos/vacantes_tecnologicas_cleaned.csv')
    
    habilidades_map = {
        'python': 'Lenguajes de Programación', 'sql': 'Bases de Datos', 'spark': 'Big Data',
        'power bi': 'Herramientas de BI', 'excel': 'Herramientas de Oficina', 'etl': 'Procesos de Datos'
    }
    
    habilidades_encontradas = set()
    for desc in df_vacantes['description'].str.lower():
        for habilidad in habilidades_map.keys():
            if habilidad in desc:
                habilidades_encontradas.add(habilidad)
    
    categorias = sorted(list(set(habilidades_map.values())))
    df_cat = pd.DataFrame(categorias, columns=['NombreCategoria'])
    df_cat['SK_Categoria'] = df_cat.index + 1
    
    engine = get_engine()
    df_cat.to_sql('DIM_CATEGORIA_SKILL', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_CATEGORIA_SKILL cargada con {len(df_cat)} registros.")
    _validar_carga(df_cat, 'DIM_CATEGORIA_SKILL')

    df_habilidades_list = []
    for habilidad in sorted(list(habilidades_encontradas)):
        categoria = habilidades_map[habilidad]
        sk_cat = df_cat[df_cat['NombreCategoria'] == categoria]['SK_Categoria'].iloc[0]
        df_habilidades_list.append({'NombreHabilidad': habilidad.title(), 'SK_Categoria': sk_cat})
    
    df_hab = pd.DataFrame(df_habilidades_list)
    df_hab['SK_Habilidad'] = df_hab.index + 1
    df_hab = df_hab[['SK_Habilidad', 'NombreHabilidad', 'SK_Categoria']]
    df_hab.to_sql('DIM_HABILIDAD', con=engine, if_exists='replace', index=False)
    print(f"   ✅ DIM_HABILIDAD cargada con {len(df_hab)} registros.")
    _validar_carga(df_hab, 'DIM_HABILIDAD')

def main():
    """Función principal que ejecuta la carga de todas las dimensiones en orden."""
    print("--- INICIANDO CARGA DE TABLAS DE DIMENSIÓN (CAPA GOLD) ---")
    try:
        cargar_dim_tiempo()
        cargar_dim_region()
        cargar_dim_carrera()
        cargar_dim_estudiante()
        cargar_dim_mercado_laboral()
        cargar_dim_categoria_y_habilidad()
        print("--- TODAS LAS DIMENSIONES HAN SIDO CARGADAS EXITOSAMENTE ---")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO durante la carga de dimensiones: {e}")

if __name__ == "__main__":
    main()