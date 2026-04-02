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
import json

def fetch_cepal_data():
    try:
        print("--- Iniciando extracción de CEPALSTAT (Indicador 4.4.1) ---")
        
        # Indicador 2096: Proporción de jóvenes con competencias en TIC
        url = "https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/2096/data" 
        
        response = requests.get(url)
        response.raise_for_status()
        
        json_data = response.json()
        
        # Intentamos obtener los datos de las claves más comunes de la API
        records = json_data.get('body') or json_data.get('data') or json_data.get('results')
        
        # Si 'records' es un string (JSON anidado), lo convertimos a objeto Python
        if isinstance(records, str):
            records = json.loads(records)

        if not records:
            print("❌ Error: No se encontraron registros válidos en la respuesta de la API.")
            # Debug: imprimir claves para saber qué envió la API realmente
            print(f"Claves disponibles en el JSON: {list(json_data.keys())}")
            return

        # Si records es una lista de diccionarios, json_normalize hará una fila por registro
        df = pd.json_normalize(records)
        
        # Si por alguna razón Pandas metió todo en una columna llamada 'data', 
        # volvemos a normalizar ese contenido específico
        if 'data' in df.columns and len(df) == 1:
            inner_data = df['data'].iloc[0]
            df = pd.json_normalize(inner_data)

        # Validación de Ingeniería 
        assert not df.empty, "Error: El DataFrame resultó vacío tras la normalización."
        print(f"✅ Validación exitosa: {len(df)} registros reales generados (no celdas anidadas).")

        # Crear ruta
        output_dir = 'data/raw/cepalstat'
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar
        file_path = os.path.join(output_dir, "indicadores_tic_region.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"📦 Archivo de CEPAL guardado exitosamente en: {file_path}")

    except Exception as e:
        print(f"❌ Error técnico en la ingesta: {e}")

if __name__ == "__main__":
    fetch_cepal_data()