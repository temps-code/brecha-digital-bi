"""
Ingestion — SQL Server (Bronze Layer)
Responsable: Abraham Flores Barrionuevo (@AFB-9898)

Extrae todas las tablas fuente desde SQL Server y las exporta
como archivos CSV en data/raw/.
"""
import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv

# 1. Configuración de conexión
server = r'DESKTOP-IHBJA7E\SQLEXPRESS' 
database = 'BrechaDigitalDB'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def extract_to_raw(table_name):
    try:
        print(f"--- Iniciando extracción de {table_name} ---")
        conn = pyodbc.connect(connection_string)
        query = f"SELECT * FROM {table_name}"
        
        # Cargar a DataFrame
        df = pd.read_sql(query, conn)
        
        # Validaciones (Afirmaciones post-extracción)
        assert not df.empty, f"Error: La tabla {table_name} está vacía."
        print(f"Validación exitosa: {len(df)} filas extraídas.")

        # Crear carpeta si no existe
        output_dir = 'data/raw'
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar en CSV
        file_path = os.path.join(output_dir, f"{table_name.lower()}.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"Archivo guardado en: {file_path}")
        conn.close()

    except Exception as e:
        print(f"Error crítico en la ingesta de {table_name}: {e}")

if __name__ == "__main__":
    # Lista de tablas para extraer
    tablas = ['Estudiantes', 'Carreras', 'Inscripciones', 'SeguimientoEgresados']
    for tabla in tablas:
        extract_to_raw(tabla)
