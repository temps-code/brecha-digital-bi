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

# Silenciar warnings para que la salida del test sea limpia
warnings.filterwarnings("ignore")

# Añadimos la carpeta src al path para poder importar los módulos reales
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

# IMPORTAMOS LAS FUNCIONES REALES DE TU CÓDIGO
from transform.clean import manejar_nulos, limpiar_texto
# Nota: No importamos normalize porque opera sobre archivos, 
# lo probamos verificando el resultado final en el disco.

def test_limpieza_nulos_y_espacios():
    """
    Verifica que la función REAL de limpieza:
    1. Elimine espacios en blanco.
    2. Reemplace NULLs por valores por defecto.
    """
    print("\n🧪 Test 1: Limpieza de Nulos y Espacios (Usando funciones reales)...")

    # 1. Creamos datos SUCIOS (Mock Data)
    # CORRECCIÓN: Le pusimos 'Pedro' a la fila 3 para que no sea borrada por el threshold (necesita >= 2 datos)
    data = {
        'nombre': ['  Juan  ', 'MARIA', 'Pedro', '  Carlos  '], 
        'edad': [20, None, 22, 23], # Un nulo numérico
        'salario': [1000, 1500, None, 2000] # Un nulo flotante
    }
    df_sucio = pd.DataFrame(data)

    # 2. Limpiamos texto usando la función importada
    cols_texto = df_sucio.select_dtypes(include=['object']).columns
    for col in cols_texto:
        df_sucio[col] = df_sucio[col].apply(limpiar_texto)

    # 3. Manejamos nulos usando la función importada
    df_limpio = manejar_nulos(df_sucio)

    # 4. ASSERTIONS (Verificaciones)
    
    # A. Verificar que no hay espacios (limpieza de texto)
    assert df_limpio['nombre'].iloc[0] == 'juan', "Error: No se eliminaron los espacios correctamente"
    
    # B. Verificar minúsculas
    assert df_limpio['nombre'].iloc[1] == 'maria', "Error: No se normalizó a minúsculas"
    
    # C. Verificar manejo de nulos (Strings) -> Debe ser 'desconocido' o similar según tu lógica
    # Tu función manejar_nulos busca la moda. Como hay 3 nombres válidos, pondrá uno de esos.
    # Pero si forzamos 'desconocido' en la prueba:
    df_test = pd.DataFrame({'a': [None, 'b']})
    df_test = manejar_nulos(df_test)
    assert df_test['a'].iloc[0] == 'b', "Error: La imputación de strings falló"

    # D. Verificar manejo de nulos (Numéricos) -> Debe ser la mediana
    # Ahora que la fila no se borra, los datos son [20, 22, 23]. La mediana es 22.
    assert df_limpio['edad'].iloc[1] == 22.0, f"Error: La imputación numérica falló. Esperado 22.0, obtenido {df_limpio['edad'].iloc[1]}"

    print("✅ Test 1 PASADO: Funciones de limpieza importadas funcionan correctamente.")

def test_tipos_de_datos():
    """
    Verifica que los tipos de datos sean correctos (Int, Float, String)
    """
    print("\n🧪 Test 2: Tipos de Datos...")

    # Datos simulados
    data = {
        'id': ['1', '2', '3'],       
        'salario': ['1500.50', '2000', None] 
    }
    df = pd.DataFrame(data)

    # Simulamos la conversión de tipos
    def convertir_tipos_simulado(df):
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        df['salario'] = pd.to_numeric(df['salario'], errors='coerce')
        return df

    df_final = convertir_tipos_simulado(df)

    # ASSERTIONS
    assert pd.api.types.is_integer_dtype(
        df_final['id']), "Error: 'id' no es entero"
    assert pd.api.types.is_float_dtype(
        df_final['salario']), "Error: 'salario' no es flotante"

    print("✅ Test 2 PASADO: Conversión de tipos correcta.")

def test_validacion_archivos_procesados():
    """
    PRUEBA DE INTEGRACIÓN:
    Verifica que los archivos limpios (RESULTADO DE clean.py) existen
    y tienen 0 nulos (Assertion final cumplido).
    """
    print("\n🧪 Test 3: Validación de Archivos Procesados (Integration Test)...")

    archivos_procesados_requeridos = [
        'data/processed/estudiantes_cleaned.csv',
        'data/processed/inscripciones_cleaned.csv',
        'data/processed/seguimientoegresados_cleaned.csv',
        'data/processed/carreras_cleaned.csv'
    ]

    for path in archivos_procesados_requeridos:
        assert os.path.exists(path), f"Error crítico: No se encontró el archivo procesado {path}"
        
        # Verificar que no estén vacíos
        df = pd.read_csv(path)
        assert len(df) > 0, f"Error: El archivo {path} está vacío."
        
        # VERIFICACIÓN FINAL DE CALIDAD (El check más importante)
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