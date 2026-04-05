"""
Ingestion — SQL Server (Bronze Layer)
Responsable: Abraham Flores Barrionuevo (@AFB-9898)

Extrae todas las tablas fuente desde SQL Server y las exporta
como archivos CSV en data/raw/.
"""
import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv

# 1. Cargar configuración desde el archivo .env
load_dotenv() 

def extract_to_raw():
    try:
        # Obtener credenciales del .env
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_NAME')
        
        if not server or not database:
            print("❌ Error: No se encontraron DB_SERVER o DB_NAME en el archivo .env")
            return

        print(f"--- Conectando a SQL Server: {server} ---")

        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')

        if user and password:
            # SQL Auth — compatible con Docker y servidores remotos
            conn_str = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={server};DATABASE={database};'
                f'UID={user};PWD={password};'
            )
        else:
            # Windows Auth — entornos locales sin contenedor
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

        conn = pyodbc.connect(conn_str)
        
        tablas = ['Estudiantes', 'Carreras', 'Inscripciones', 'SeguimientoEgresados', 'CompetenciasDigitales']
        
        # Asegurar que la carpeta de destino exista
        output_dir = 'data/raw'
        os.makedirs(output_dir, exist_ok=True)

        for table_name in tablas:
            print(f"--- Iniciando extracción de {table_name} ---")
            query = f"SELECT * FROM {table_name}"
            
            # Cargar a DataFrame
            df = pd.read_sql(query, conn)
            
            # Validación de Ingeniería (Punto clave de la rúbrica)
            assert not df.empty, f"Error: La tabla {table_name} está vacía en la base de datos."
            
            # Guardar en CSV (usamos .lower() para mantener consistencia en los nombres)
            file_path = os.path.join(output_dir, f"{table_name.lower()}.csv")
            df.to_csv(file_path, index=False, encoding='utf-8')
            
            print(f" Tabla {table_name} exportada con éxito: {len(df)} filas.")

        conn.close()
        print("--- Proceso de Ingesta SQL finalizado correctamente ---")

    except Exception as e:
        print(f" Error crítico en la ingesta de SQL Server: {e}")

if __name__ == "__main__":
    extract_to_raw()