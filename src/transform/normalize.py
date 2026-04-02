"""
Transform — Data Normalization (Silver)
Responsable: Juan Nicolás Flores Delgado (@Juan7139nf)

Normaliza los datos limpios:
  - Estandariza nombres de departamentos/ciudades de Bolivia
  - Unifica formatos de fechas
  - Deduplica registros
  - Prepara columnas para el esquema copo de nieve

Salida: data/processed/ (sobreescribe con versión normalizada)
"""

import pandas as pd
import os

PROCESSED_PATH = 'data/processed'

# Diccionario de estandarización geográfica (Bolivia)
# Input: lo que viene de clean.py (todo minúsculas)
# Output: Valor estándar para el DW
MAPA_CIUDADES = {
    'la paz': 'La Paz', 'lp': 'La Paz', 'el alto': 'El Alto',
    'santa cruz': 'Santa Cruz de la Sierra', 'santa cruz de la sierra': 'Santa Cruz de la Sierra',
    'cochabamba': 'Cochabamba', 'cbba': 'Cochabamba',
    'sucre': 'Sucre', 'oruro': 'Oruro', 'potosi': 'Potosí', 'tarija': 'Tarija',
    'beni': 'Trinidad', 'pando': 'Cobija',
    'remote': 'Remoto'
}


def estandarizar_geografia(df, col_geo):
    """Normaliza nombres de ciudades usando el mapa predefinido."""
    if col_geo not in df.columns:
        return df

    # Mapear: si la ciudad está en el diccionario, usar el valor estándar. Si no, Title Case.
    df[col_geo] = df[col_geo].apply(lambda x: MAPA_CIUDADES.get(x, x.title()))
    return df


def normalizar_archivo(nombre_archivo):
    print(f"⚙️  Normalizando: {nombre_archivo}...")

    path = os.path.join(PROCESSED_PATH, nombre_archivo)
    if not os.path.exists(path):
        print(f"   ⚠️  No encontrado (quizás falló clean.py): {path}")
        return

    df = pd.read_csv(path)

    # 1. Deduplicación
    original_len = len(df)
    df = df.drop_duplicates()
    if len(df) < original_len:
        print(f"   ℹ️  Eliminados {original_len - len(df)} duplicados.")

    # 2. Estandarización Geográfica
    # Buscamos columnas que puedan ser ciudades
    posibles_cols_geo = ['ciudad', 'location', 'ciudad_residencia']
    for col in posibles_cols_geo:
        if col in df.columns:
            df = estandarizar_geografia(df, col)

    # 3. Preparación para Esquema Copo de Nieve (Tips de tipo)
    # Asegurar que 'anio' sea entero para los joins en Gold
    if 'anio' in df.columns:
        df['anio'] = df['anio'].astype(int)

    # Asegurar que los IDs sean cadenas limpias o enteros consistentes
    # (Útil para evitar problemas de tipo en SQL Server)
    for col in df.columns:
        if 'id' in col.lower():
            # Si parece numérico pero tiene ceros a la izquierda, mantener como string
            # Si es puro número, int64
            try:
                # Intento de conversión segura
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass

    # 4. Guardar (Sobreescribir el cleaned)
    df.to_csv(path, index=False, encoding='utf-8')
    print(f"   ✅ Normalización completa y guardada.")

def crear_vista_unificada():
    """
    Realiza un Inner Join para unificar datos de Estudiantes e Inscripciones
    como ejemplo de integración de fuentes para la Capa Silver.
    """
    print("🔗 Realizando Inner Join (Estudiantes + Inscripciones)...")
    
    try:
        df_estudiantes = pd.read_csv(os.path.join(PROCESSED_PATH, 'estudiantes_cleaned.csv'))
        df_inscripciones = pd.read_csv(os.path.join(PROCESSED_PATH, 'inscripciones_cleaned.csv'))
        
        # Hacemos el Inner Join usando la columna 'EstudianteID' y 'anio'
        # Nota: Asegúrate de que ambas tablas tengan la columna 'anio' generada en clean.py
        df_merged = pd.merge(df_estudiantes, df_inscripciones, on=['EstudianteID', 'anio'], how='inner')
        
        output_merged = os.path.join(PROCESSED_PATH, 'silver_integrated_data.csv')
        df_merged.to_csv(output_merged, index=False)
        print(f"   ✅ Join completado. Guardado en: {output_merged}")
        
    except FileNotFoundError as e:
        print(f"   ⚠️  No se pudo hacer el join (falta algun archivo): {e}")


if __name__ == "__main__":
    print("--- INICIANDO NORMALIZACIÓN DE DATOS ---")

    # Buscamos todos los archivos que terminan en _cleaned.csv
    archivos = [f for f in os.listdir(
        PROCESSED_PATH) if f.endswith('_cleaned.csv')]

    if not archivos:
        print("❌ No se encontraron archivos *_cleaned.csv. Ejecuta primero clean.py")
    else:
        for archivo in archivos:
            normalizar_archivo(archivo)
            
        # Llamar a la función al final del script principal
        crear_vista_unificada()

    print("--- NORMALIZACIÓN FINALIZADA ---")
