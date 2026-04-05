"""
Ingestion — Employment APIs (External)
Responsable: Abraham Flores Barrionuevo (@AFB-9898)

Consulta APIs externas de empleo para obtener vacantes activas
y habilidades TIC en tendencia. Exporta los resultados en data/raw/empleos/.
"""
import pandas as pd
import os
import random

def fetch_adzuna_jobs_mock():
    try:
        print("--- Iniciando extracción de Adzuna (Simulación con Variedad de Habilidades) ---")
        
        mock_jobs = []
        titles = ['Data Engineer', 'Data Analyst', 'BI Developer', 'Python Developer', 'SQL Specialist']
        locations = ['Tarija', 'La Paz', 'Santa Cruz', 'Cochabamba', 'Remote', 'Sucre']
        
        # Mapa de habilidades para generar variedad analítica
        skills_map = {
            'Data Engineer': 'Experiencia en pipelines ETL, Spark y SQL avanzado.',
            'Data Analyst': 'Manejo de Power BI, Excel avanzado y estadística descriptiva.',
            'BI Developer': 'Conocimientos en modelado dimensional, SSAS y DAX.',
            'Python Developer': 'Python orientado a datos, pandas y scikit-learn.',
            'SQL Specialist': 'Optimización de queries, stored procedures y DW design.'
        }
        
        for i in range(50):
            job_title = random.choice(titles)
            # Seleccionamos la descripción según el título elegido
            description = skills_map.get(job_title, 'Requerimos habilidades TIC para reducir la brecha digital.')
            
            mock_jobs.append({
                'id': f'adz-{1000+i}',
                'title': job_title,
                'location': random.choice(locations), 
                'salary_min': random.randint(800, 1800),
                'category': 'IT Jobs',                
                'description': description,          
                'created': '2026-03-30T10:00:00Z'
            })
        
        df = pd.DataFrame(mock_jobs)
        
        # Validación de salida
        assert not df.empty, "Error: El DataFrame de empleos está vacío."
        
        output_dir = 'data/raw/empleos'
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, "vacantes_tecnologicas.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"✅ Éxito: Generadas 50 vacantes con descripciones variadas en: {file_path}")

    except Exception as e:
        print(f"❌ Error en la simulación de empleos: {e}")

if __name__ == "__main__":
    fetch_adzuna_jobs_mock()