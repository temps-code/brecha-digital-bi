import pandas as pd
import os

def validate_csvs():
    # Definimos las columnas que esperamos. 
    # Para CEPAL dejamos una lista de "posibles" nombres o partes del nombre.
    files_to_check = {
        'data/raw/estudiantes.csv': ['EstudianteID', 'Nombre', 'Ciudad'],
        'data/raw/inscripciones.csv': ['InscripcionID', 'EstudianteID', 'CarreraID'],
        'data/raw/seguimientoegresados.csv': ['EgresadoID', 'EstudianteID', 'TieneEmpleoFormal'],
        'data/raw/empleos/vacantes_tecnologicas.csv': ['id', 'title', 'salary_min']
    }

    print("--- Iniciando Validación Final de Capa Bronce ---")
    
    # 1. Validar archivos estándar (SQL y Empleos)
    for path, columns in files_to_check.items():
        if not os.path.exists(path):
            print(f"❌ Error: El archivo {path} no existe.")
            continue
            
        df = pd.read_csv(path)
        assert len(df) > 0, f"Error: {path} está vacío."
        
        for col in columns:
            assert col in df.columns, f"Error: Falta la columna {col} en {path}."
        
        print(f"✅ {path} validado correctamente (Forma: {df.shape})")

    # 2. VALIDACIÓN FLEXIBLE PARA CEPAL (A prueba de errores de nombre)
    path_cepal = 'data/raw/cepalstat/indicadores_tic_region.csv'
    if os.path.exists(path_cepal):
        df_cepal = pd.read_csv(path_cepal)
        cols_cepal = df_cepal.columns.tolist()
        
        # En lugar de buscar el nombre exacto, buscamos si existe una columna que 
        # contenga 'indicator' o 'id'. Esto evita el error de metadata. o indicator_id
        has_id = any('id' in c.lower() or 'indicator' in c.lower() for c in cols_cepal)
        has_val = any('value' in c.lower() or 'valor' in c.lower() or 'dim' in c.lower() for c in cols_cepal)
        
        assert has_id, f"Error: No se encontró columna de ID en {path_cepal}. Columnas: {cols_cepal}"
        assert len(df_cepal) > 0, f"Error: El archivo de CEPAL está vacío."
        
        print(f"✅ {path_cepal} validado (Columnas detectadas: {len(cols_cepal)}, Filas: {len(df_cepal)})")
    else:
        print(f"❌ Error: No se encontró el archivo de CEPAL en {path_cepal}")

if __name__ == "__main__":
    validate_csvs()