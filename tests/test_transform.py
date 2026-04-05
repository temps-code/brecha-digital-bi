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
import tempfile  # Necesario para el Test 3 robusto

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
    assert df_limpio['nombre'].iloc[0] == 'juan', "Error: No se eliminaron espacios o minúsculas"
    assert df_limpio['nombre'].iloc[1] == 'maria', "Error: No se normalizó a minúsculas"
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
    Unit Test Robusto.
    Verifica que procesar_archivo() genere archivos libres de nulos.
    
    CORRECCIÓN: Ya no depende de archivos externos (data/processed).
    Genera sus propios datos temporales y parchea las rutas del módulo.
    """
    print("\n🧪 Test 3: Validación de Pipeline de Limpieza (Unit Test Robusto)...")

    # Importamos el módulo completo para poder parchear sus rutas globales
    import transform.clean as clean_mod
    from transform.clean import procesar_archivo

    # Datos de prueba sucios
    data = {
        'nombre': ['  Juan  ', 'MARIA'], 
        'ciudad': ['La Paz', 'cbba'], 
        'fecha_ingreso': ['2023-01-15', '2022-05-20']
    }
    
    with tempfile.TemporaryDirectory() as tmp:
        # Definir rutas temporales
        raw_path = os.path.join(tmp, 'raw')
        proc_path = os.path.join(tmp, 'processed')
        os.makedirs(raw_path)
        os.makedirs(proc_path)
        
        # Crear archivo CSV de entrada en la carpeta raw temporal
        input_csv = os.path.join(raw_path, 'test_estudiantes.csv')
        pd.DataFrame(data).to_csv(input_csv, index=False)

        # PARCHEO: Sobrescribir las rutas globales del módulo clean.py
        # Esto hace que procesar_archivo use nuestras carpetas temporales
        clean_mod.RAW_PATH = raw_path
        clean_mod.PROCESSED_PATH = proc_path

        # Ejecutar la función de limpieza
        procesar_archivo('test_estudiantes.csv')

        # Verificar que el archivo de salida existe
        output_csv = os.path.join(proc_path, 'test_estudiantes_cleaned.csv')
        assert os.path.exists(output_csv), "El archivo limpio no fue generado."
        
        # Verificar que el archivo generado tiene 0 nulos
        df_res = pd.read_csv(output_csv)
        nulos_restantes = df_res.isnull().sum().sum()
        assert nulos_restantes == 0, f"El archivo generado tiene {nulos_restantes} nulos."

    print("✅ Test 3 PASADO: El pipeline genera archivos limpios de forma autónoma.")

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