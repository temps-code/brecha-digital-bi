# test_connection.py
import os
from dotenv import load_dotenv
import sqlalchemy
import pyodbc

load_dotenv()

DW_SERVER = os.getenv('DW_SERVER')
DW_NAME = os.getenv('DW_NAME')
DW_USER = os.getenv('DW_USER')
DW_PASSWORD = os.getenv('DW_PASSWORD')

# Imprime las variables para verificar que se cargaron bien
print(f"Conectando a: Servidor={DW_SERVER}, BD={DW_NAME}, Usuario={DW_USER}")

connection_string = f"mssql+pyodbc://{DW_USER}:{DW_PASSWORD}@{DW_SERVER}/{DW_NAME}?driver=ODBC+Driver+17+for+SQL+Server"

try:
    engine = sqlalchemy.create_engine(connection_string)
    with engine.connect() as connection:
        print("✅ Conexión a SQL Server exitosa!")
        result = connection.execute(sqlalchemy.text("SELECT @@VERSION"))
        for row in result:
            print("Versión de SQL Server:", row[0])
except Exception as e:
    print(f"❌ Error de conexión: {e}")
