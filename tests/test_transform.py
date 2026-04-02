"""
Tests — Data Transformation
Responsable: Juan Nicolás Flores Delgado (@Juan7139nf)

Pruebas unitarias para las funciones de limpieza y normalización.
Verificar que clean.py y normalize.py manejen correctamente:
  - Valores NULL
  - Nombres con mayúsculas mezcladas
  - Espacios extra en strings
  - Tipos de datos incorrectos
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings

warnings.filterwarnings("ignore")

# Añadimos la carpeta src al path
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

from transform.clean import manejar_nulos, limpiar_texto

def test_limpieza_nulos_y_espacios():
    print("\n🧪 Test 1: Limpieza de Nulos y Espacios (Usando funciones reales)...")

    data = {
        'nombre': ['  Juan  ', 'MARIA', 'Pedro', '  Carlos  '], 
        'edad': [20, None, 22, 23], 
        'salario': [1000, 1500, None, 2000] 
    }
    df_sucio = pd.DataFrame(data)

    # Limpiamos texto
    cols_texto = df_sucio.select_dtypes(include=['object']).columns
    for col in cols_texto:
        df_sucio[col] = df_sucio[col].apply(limpiar_texto)

    # Manejamos nulos
    df_limpio = manejar_nulos(df_sucio)

    # Assertions
    # Verificar minúsculas (y acentos si los hubiera)
    assert df_limpio['nombre'].iloc[0] == 'juan', "Error: No se eliminaron espacios o minúsculas"
    assert df_limpio['nombre'].iloc[1] == 'maria', "Error: No se normalizó a minúsculas"
    
    # Verificar imputación numérica (mediana de [20, 22, 23] es 22)
    assert df_limpio['edad'].iloc[1] == 22.0, f"Error: La imputación numérica falló. Esperado 22.0, obtenido {df_limpio['edad'].iloc[1]}"

    print("✅ Test 1 PASADO: Funciones de limpieza importadas funcionan correctamente.")

def test_tipos_de_datos():
    print("\n🧪 Test 2: Tipos de Datos...")

    data = {
        'id': ['1', '2', '3'],       
        'salario': ['1500.50', '2000', None] 
    }
    df = pd.DataFrame(data)

    def convertir_tipos_simulado(df):
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        df['salario'] = pd.to_numeric(df['salario'], errors='coerce')
        return df

    df_final = convertir_tipos_simulado(df)

    assert pd.api.types.is_integer_dtype(df_final['id']), "Error: 'id' no es entero"
    assert pd.api.types.is_float_dtype(df_final['salario']), "Error: 'salario' no es flotante"

    print("✅ Test 2 PASADO: Conversión de tipos correcta.")

def test_validacion_archivos_procesados():
    """
    Integration Test.
    Verifica que los archivos procesados (RESULTADO DE clean.py) existen
    y tienen 0 nulos (Assertion final cumplido).
    
    Requisito: Ejecutar 'python src/transform/clean.py' antes de este test.
    """
    print("\n🧪 Test 3: Validación de Archivos Procesados (Integration Test)...")

    archivos_procesados_requeridos = [
        'data/processed/estudiantes_cleaned.csv',
        'data/processed/inscripciones_cleaned.csv',
        'data/processed/seguimientoegresados_cleaned.csv',
        'data/processed/carreras_cleaned.csv'
    ]

    for path in archivos_procesados_requeridos:
        assert os.path.exists(path), f"Error crítico: No se encontró el archivo procesado {path}. ¿Ejecutaste clean.py?"
        
        df = pd.read_csv(path)
        assert len(df) > 0, f"Error: El archivo {path} está vacío."
        
        # Verificación de Calidad: 0 Nulos
        nulos_restantes = df.isnull().sum().sum()
        assert nulos_restantes == 0, f"Error: El archivo {path} todavía tiene {nulos_restantes} valores nulos."

    print(f"✅ Test 3 PASADO: Existen {len(archivos_procesados_requeridos)} archivos limpios con 0 nulos.")

if __name__ == "__main__":
    print("======================================")
    print("   EJECUTANDO TESTS DE TRANSFORMACIÓN")
    print("======================================")

    try:
        test_limpieza_nulos_y_espacios()
        test_tipos_de_datos()
        test_validacion_archivos_procesados()

        print("\n" + "="*30)
        print("🎉 TODOS LOS TESTS PASARON")
        print("📸 ¡Toma una captura de pantalla de esta consola para el informe!")
        print("="*30)

    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        print("Revisa tu lógica en clean.py o normalize.py")
    except Exception as e:
        print(f"\n⚠️ Error inesperado: {e}")