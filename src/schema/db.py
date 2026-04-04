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
    """Crea y retorna una instancia singleton del motor de base de datos.

    Soporta dos modos de autenticación:
    - SQL Auth (Docker / Linux / Windows con credenciales): requiere DW_USER y DW_PASSWORD.
    - Windows Auth (Windows con SQL Server local): dejar DW_USER y DW_PASSWORD vacíos.
    """
    global _engine
    if _engine is None:
        dw_server   = os.getenv('DW_SERVER')
        dw_name     = os.getenv('DW_NAME')
        dw_user     = os.getenv('DW_USER')
        dw_password = os.getenv('DW_PASSWORD')

        if not all([dw_server, dw_name]):
            raise ValueError(
                "Faltan variables de entorno para la conexión al Data Warehouse. "
                "Verificá que DW_SERVER y DW_NAME estén en el .env."
            )

        print("   🔗 Creando conexión a la base de datos...")

        if dw_user and dw_password:
            # SQL Auth — compatible con Docker y servidores remotos
            connection_string = (
                f"mssql+pyodbc://{dw_user}:{dw_password}@{dw_server}/{dw_name}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )
        else:
            # Windows Auth — entornos locales sin contenedor
            connection_string = (
                f"mssql+pyodbc://@{dw_server}/{dw_name}"
                "?driver=SQL+Server&trusted_connection=yes"
            )

        _engine = create_engine(connection_string)
    return _engine
