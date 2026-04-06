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
# DOCUMENTACIÓN: Se asume que si el usuario ingresa el nombre del departamento 
# (ej. 'beni', 'pando'), se refiere a su capital principal para fines de localización.
# CORRECCIÓN: Agregados aliases para ciudades con múltiples formas (e.g. 'Santa Cruz' y 'santa cruz' → 'Santa Cruz de la Sierra')
MAPA_CIUDADES = {
    'la paz': 'La Paz', 'lp': 'La Paz', 'el alto': 'El Alto',
    'santa cruz': 'Santa Cruz de la Sierra', 'santa cruz de la sierra': 'Santa Cruz de la Sierra', 'sc': 'Santa Cruz de la Sierra',
    'cochabamba': 'Cochabamba', 'cbba': 'Cochabamba', 'cbba.': 'Cochabamba',
    'sucre': 'Sucre', 'oruro': 'Oruro', 'potosi': 'Potosí', 'potosí': 'Potosí', 'tarija': 'Tarija',
    'beni': 'Trinidad',   # Mapeo Depto -> Capital
    'pando': 'Cobija',    # Mapeo Depto -> Capital
    'remote': 'Remoto'
}


def _normalize_geo(x):
    if pd.isna(x):
        return x
    key = str(x).strip().lower()
    return MAPA_CIUDADES.get(key, str(x).strip().title())


def estandarizar_geografia(df, col_geo):
    """Normaliza nombres de ciudades usando el mapa predefinido."""
    if col_geo not in df.columns:
        return df

    # Mapear: si la ciudad está en el diccionario, usar el valor estándar. Si no, Title Case.
    df[col_geo] = df[col_geo].apply(_normalize_geo)
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

    # 2. Estandarización Geográfica (lookup case-insensitive en nombre de columna)
    posibles_cols_geo = {'ciudad', 'location', 'ciudad_residencia'}
    for col in df.columns:
        if col.lower() in posibles_cols_geo:
            df = estandarizar_geografia(df, col)

    # 3. Preparación para Esquema Copo de Nieve (Tips de tipo)
    if 'anio' in df.columns:
        df['anio'] = df['anio'].astype(int)

    # CORRECCIÓN WARNING 5: Eliminado try/except desnudo. 
    # pd.to_numeric con errors='ignore' ya maneja los errores silenciosamente.
    for col in df.columns:
        if 'id' in col.lower():
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            # Si la conversión resultó en NaN (ej: el ID era "A-123"), dejamos el valor original
            df[col] = numeric_series.where(numeric_series.notna(), df[col])

    # 4. Guardar (Sobreescribir el cleaned)
    df.to_csv(path, index=False, encoding='utf-8')
    print(f"   ✅ Normalización completa y guardada.")

def crear_vista_unificada():
    """
    Realiza un Inner Join para unificar datos de Estudiantes e Inscripciones.
    CORRECCIÓN BUG 4: Se elimina el join por 'anio' para evitar falsas relaciones 
    cuando extraer_anio asigna 2024 por defecto. Se usa solo EstudianteID.
    """
    print("🔗 Realizando Inner Join (Estudiantes + Inscripciones)...")
    
    try:
        df_estudiantes = pd.read_csv(os.path.join(PROCESSED_PATH, 'estudiantes_cleaned.csv'))
        df_inscripciones = pd.read_csv(os.path.join(PROCESSED_PATH, 'inscripciones_cleaned.csv'))
        
        # CORRECCIÓN: Merge solo por EstudianteID. 
        # El 'anio' se mantiene como columna de atributo, no como llave de join aquí.
        df_merged = pd.merge(df_estudiantes, df_inscripciones, on='EstudianteID', how='inner')
        
        output_merged = os.path.join(PROCESSED_PATH, 'silver_integrated_data.csv')
        df_merged.to_csv(output_merged, index=False)
        print(f"   ✅ Join completado. Guardado en: {output_merged}")
        
    except FileNotFoundError as e:
        print(f"   ⚠️  No se pudo hacer el join (falta algun archivo): {e}")


if __name__ == "__main__":
    print("--- INICIANDO NORMALIZACIÓN DE DATOS ---")

    archivos = [f for f in os.listdir(PROCESSED_PATH) if f.endswith('_cleaned.csv')]

    if not archivos:
        print("❌ No se encontraron archivos *_cleaned.csv. Ejecuta primero clean.py")
    else:
        for archivo in archivos:
            normalizar_archivo(archivo)
            
        # Llamar a la función al final del script principal
        crear_vista_unificada()

    print("--- NORMALIZACIÓN FINALIZADA ---")