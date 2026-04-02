"""
Transform — Data Cleaning (Bronze → Silver)
Responsable: Juan Nicolás Flores Delgado (@Juan7139nf)

Limpia los CSV crudos de data/raw/:
  - Elimina o imputa valores NULL (5% introducido intencionalmente en seed.sql)
  - Normaliza mayúsculas/minúsculas mezcladas en nombres
  - Elimina espacios extra en campos de texto
  - Valida tipos de datos y rangos

Salida: data/processed/
"""

import pandas as pd
import numpy as np
import os
import unicodedata
import warnings

# Ignorar advertencias de Pandas futuras para mantener la consola limpia
warnings.filterwarnings("ignore")

RAW_PATH = 'data/raw'
PROCESSED_PATH = 'data/processed'
os.makedirs(PROCESSED_PATH, exist_ok=True)

def limpiar_texto(texto):
    if pd.isna(texto):
        return texto
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()

def manejar_nulos(df):
    """
    CORREGIDO: Eliminamos inplace=True para evitar ChainedAssignmentError.
    """
    # 1. Eliminar filas con exceso de nulos
    threshold = int(df.shape[1] * 0.95)
    df = df.dropna(thresh=threshold)
    
    # 2. Imputación de nulos
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ['float64', 'int64', 'Int64', 'float']:
                # CORRECCIÓN: Asignación directa en lugar de inplace
                df[col] = df[col].fillna(df[col].median())
            else:
                moda = df[col].mode()
                if len(moda) > 0:
                    df[col] = df[col].fillna(moda[0])
                else:
                    df[col] = df[col].fillna('desconocido')
    return df

def extraer_anio(df, col_fecha_o_anio):
    if col_fecha_o_anio not in df.columns:
        df['anio'] = 2024
        return df

    df[col_fecha_o_anio] = df[col_fecha_o_anio].astype(str)
    anios = pd.to_numeric(df[col_fecha_o_anio].str.extract(r'(\d{4})')[0], errors='coerce')
    anios.fillna(2024, inplace=True)
    df['anio'] = anios.astype(int)
    return df

def procesar_archivo(nombre_archivo):
    print(f"🧹 Limpiando: {nombre_archivo}...")
    
    # CORRECCIÓN DE RUTA: Unimos directamente, ya que el nombre incluye subcarpetas si las hay
    ruta_completa = os.path.join(RAW_PATH, nombre_archivo)

    if not os.path.exists(ruta_completa):
        print(f"   ⚠️  Archivo no encontrado, saltando: {ruta_completa}")
        return

    df = pd.read_csv(ruta_completa)
    
    # Limpieza de texto
    # CORRECCIÓN WARNING: Incluimos 'string' para compatibilidad Pandas 2.x/3.x
    cols_texto = df.select_dtypes(include=['object', 'string']).columns
    for col in cols_texto:
        df[col] = df[col].apply(limpiar_texto)

    # Manejo de Nulos
    df = manejar_nulos(df)

    # Extracción de Año
    col_fecha = None
    for col in df.columns:
        if 'fecha' in col.lower() or 'date' in col.lower() or 'ingreso' in col.lower() or 'created' in col.lower():
            col_fecha = col
            break
    
    if not col_fecha:
        for col in df.columns:
            if 'anio' in col.lower() or 'year' in col.lower() or 'period' in col.lower():
                col_fecha = col
                break

    df = extraer_anio(df, col_fecha)

    # Assertion
    try:
        assert df.isnull().sum().sum() == 0, f"Aún existen nulos en {nombre_archivo}"
        print(f"   ✅ Assertion pasada: 0 Nulos.")
    except AssertionError as e:
        print(f"   ❌ {e}")
        return

    # Guardar
    output_name = nombre_archivo.replace('.csv', '_cleaned.csv')
    # Si el archivo tiene subcarpetas (ej: 'empleos/vacantes.csv'), mantenemos la estructura en processed
    if '/' in nombre_archivo:
        subdir = os.path.dirname(output_name)
        os.makedirs(os.path.join(PROCESSED_PATH, subdir), exist_ok=True)
        output_path = os.path.join(PROCESSED_PATH, output_name)
    else:
        output_path = os.path.join(PROCESSED_PATH, output_name)
        
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"   💾 Guardado en: {output_path}")

if __name__ == "__main__":
    print("--- INICIANDO LIMPIEZA DE DATOS (SILVER LAYER) ---")
    
    archivos_procesar = [
        'estudiantes.csv',
        'inscripciones.csv',
        'seguimientoegresados.csv',
        'carreras.csv', 
        'empleos/vacantes_tecnologicas.csv',
        'cepalstat/indicadores_tic_region.csv'
    ]

    for archivo in archivos_procesar:
        procesar_archivo(archivo)
    
    print("--- LIMPIEZA FINALIZADA ---")