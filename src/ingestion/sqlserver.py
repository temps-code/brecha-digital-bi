"""
Ingestion — SQL Server (Bronze Layer)
Responsable: Abraham Flores Barrionuevo (@AFB-9898)

Extrae todas las tablas fuente desde SQL Server y las exporta
como archivos CSV en data/raw/.
"""
import os
from dotenv import load_dotenv
import pyodbc

load_dotenv() 

server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')

conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'