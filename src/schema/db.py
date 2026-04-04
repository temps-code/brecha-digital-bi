"""
Schema — Database Connection (Gold Layer)
Motor compartido para dimensions.py y facts.py.
Lazy initialization: la conexión se crea la primera vez que se llama a get_engine().
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

_engine = None


def get_engine():
    """Crea y retorna una instancia singleton del motor de base de datos."""
    global _engine
    if _engine is None:
        dw_server   = os.getenv('DW_SERVER')
        dw_name     = os.getenv('DW_NAME')
        dw_user     = os.getenv('DW_USER')
        dw_password = os.getenv('DW_PASSWORD')

        if not all([dw_server, dw_name, dw_user, dw_password]):
            raise ValueError(
                "Faltan variables de entorno para la conexión al Data Warehouse. "
                "Verificá que DW_SERVER, DW_NAME, DW_USER y DW_PASSWORD estén en el .env."
            )

        connection_string = (
            f"mssql+pyodbc://{dw_user}:{dw_password}@{dw_server}/{dw_name}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
        )
        print("   🔗 Creando conexión a la base de datos...")
        _engine = create_engine(connection_string)
    return _engine