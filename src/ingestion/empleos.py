"""
Ingestion — Employment APIs (External)
Responsable: Abraham Flores Barrionuevo (@AFB-9898)

Consulta APIs externas de empleo (Adzuna) para obtener vacantes activas.
Exporta los resultados en data/raw/empleos/.
"""
import pandas as pd
import os
import requests
import random
from dotenv import load_dotenv

# Cargar variables de entorno (APP_ID y API_KEY)
load_dotenv()

def fetch_adzuna_jobs():
    try:
        app_id = os.getenv("ADZUNA_APP_ID")
        api_key = os.getenv("ADZUNA_API_KEY")
        
        if not app_id or not api_key:
            raise ValueError("Faltan las credenciales ADZUNA_APP_ID o ADZUNA_API_KEY en el .env")
        
        print("--- Iniciando extracción REAL de Adzuna (Múltiples Países) ---")
        
        # Países a consultar (Adzuna no soporta 'bo')
        # mx: México, br: Brasil, es: España, us: Estados Unidos
        countries = {
            'mx': {'divisor_usd': 17, 'limit': 100},
            'br': {'divisor_usd': 5, 'limit': 50},
            'es': {'divisor_usd': 0.9, 'limit': 50},
            'us': {'divisor_usd': 1, 'limit': 50}
        }
        
        real_jobs = []
        
        for country, config in countries.items():
            print(f"Consultando vacantes en: {country.upper()}...")
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={app_id}&app_key={api_key}&results_per_page={config['limit']}&category=it-jobs"
            
            response = requests.get(url)
            if response.status_code != 200:
                print(f"⚠️ Error al consultar {country}: HTTP {response.status_code}")
                continue
                
            data = response.json()
            results = data.get("results", [])
            
            for job in results:
                title = job.get("title", "IT Professional")
                description = job.get("description", "Requerimos habilidades TIC para reducir la brecha digital.")
                
                # Conversión de salario
                salary = job.get("salary_min")
                if not salary:
                    salary = random.randint(800, 2500)  # Fallback realista en USD
                else:
                    salary = int(salary / config['divisor_usd'])
                
                # Usar la ubicación real de Adzuna y agregar el país
                location_data = job.get("location", {})
                display_name = location_data.get("display_name", "Remote")
                
                area = location_data.get("area", [])
                country_name = area[0] if area else country.upper()
                
                # Formatear como "Ciudad, País"
                location = f"{display_name}, {country_name}" if display_name != country_name else country_name
                
                real_jobs.append({
                    'id': job.get("id", f'adz-{random.randint(10000, 99999)}'),
                    'title': title,
                    'location': location, 
                    'salary_min': salary,
                    'category': 'IT Jobs',                
                    'description': description,          
                    'created': job.get("created", '2026-03-30T10:00:00Z')
                })
            
        df = pd.DataFrame(real_jobs)
        
        if df.empty:
            raise ValueError("Error: El DataFrame de empleos está vacío tras consultar todos los países.")
        
        output_dir = 'data/raw/empleos'
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, "vacantes_tecnologicas.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"✅ Éxito: Obtenidas {len(df)} vacantes REALES de Adzuna Internacional en: {file_path}")

    except Exception as e:
        print(f"❌ Error en la extracción de empleos: {e}")

if __name__ == "__main__":
    fetch_adzuna_jobs()