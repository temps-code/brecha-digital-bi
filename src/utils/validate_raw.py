import pandas as pd
import os

def validate_csvs():
    files_to_check = {
        'data/raw/estudiantes.csv': ['EstudianteID', 'Nombre', 'Ciudad'],
        # Usamos los nombres reales que detectamos con el comando print:
        'data/raw/cepalstat/indicadores_tic_region.csv': ['metadata.indicator_id', 'metadata.indicator_name'], 
        'data/raw/empleos/vacantes_tecnologicas.csv': ['id', 'title', 'salary_min']
    }

    print("--- Iniciando Validación Final de Capa Bronce ---")
    
    for path, columns in files_to_check.items():
        if not os.path.exists(path):
            print(f"❌ Error: El archivo {path} no existe.")
            continue
            
        df = pd.read_csv(path)
        
        # 1. Validar Forma (Shape)
        assert len(df) > 0, f"Error: {path} está vacío."
        
        # 2. Validar Dtypes (Columnas presentes)
        for col in columns:
            assert col in df.columns, f"Error: Falta la columna {col} en {path}."
        
        # 3. Validar Sin Vacíos en columnas críticas
        # Nota: En BI aceptamos nulos en notas, pero NO en IDs o Nombres
        critical_col = columns[0]
        assert df[critical_col].notnull().all(), f"Error: Hay nulos en la columna crítica {critical_col} de {path}."
        
        print(f"✅ {path} validado correctamente (Forma: {df.shape})")

if __name__ == "__main__":
    validate_csvs()