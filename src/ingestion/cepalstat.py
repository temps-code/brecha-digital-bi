"""
Ingestion — CEPALSTAT API (External)
Responsable: Abraham Flores Barrionuevo (@AFB-9898)

Consume la API REST de CEPALSTAT para obtener indicadores de
desempleo juvenil y competencias TIC en Bolivia y el Cono Sur.
Exporta los resultados en data/raw/cepalstat/.
"""
import requests
import pandas as pd
import os

def fetch_cepal_data():
    try:
        print("--- Iniciando extracción de CEPALSTAT (Indicador 4.4.1) ---")
        
        # Indicador 2096: Proporción de jóvenes con competencias en TIC
        url = "https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/2096/data" 
        
        response = requests.get(url)
        response.raise_for_status()
        
        json_data = response.json()
        
        # Extraemos solo los datos de la tabla (normalmente en 'body')
        # Si la estructura es irregular, usamos pd.json_normalize
        records = json_data.get('body', [])
        
        if not records:
            print("No se encontraron registros en el cuerpo de la respuesta.")
            return

        # json_normalize ayuda a manejar diccionarios de diferentes longitudes
        df = pd.json_normalize(records)
        
        # Validación de Ingeniería
        assert not df.empty, "Error: El DataFrame resultó vacío tras la normalización."
        print(f"Validación exitosa: {len(df)} registros normalizados.")

        # Crear ruta
        output_dir = 'data/raw/cepalstat'
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar
        file_path = os.path.join(output_dir, "indicadores_tic_region.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"Archivo de CEPAL guardado exitosamente en: {file_path}")

    except Exception as e:
        print(f"Error técnico en la ingesta: {e}")

if __name__ == "__main__":
    fetch_cepal_data()
