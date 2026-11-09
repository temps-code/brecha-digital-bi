# Reactivar Groq en local y en Streamlit Cloud

El chatbot y la extracción de habilidades usan `openai/gpt-oss-20b` por defecto.
Ambos aceptan `GROQ_MODEL` para cambiar de modelo sin editar código.
Groq [retiró `llama-3.1-8b-instant` de los planes free/developer](https://console.groq.com/docs/deprecations)
el 16 de agosto de 2026 y recomienda este reemplazo.

## Local

1. Conservá tu nueva `GROQ_API_KEY` en `.env` (no la subas a Git).
2. Si ya tenés `GROQ_MODEL`, reemplazá cualquier modelo retirado:
   ```dotenv
   GROQ_MODEL=openai/gpt-oss-20b
   ```
   Si falta o está vacío se usa el modelo por defecto. Las variables del proceso
   tienen prioridad sobre `.env`; reiniciá Streamlit después de cambiarlas.
3. Instalá dependencias y arrancá:
   ```bash
   python -m venv .venv
   # Windows:
   .venv/Scripts/python -m pip install -r requirements.txt
   .venv/Scripts/python -m streamlit run src/dashboard/app.py
   ```
4. Abrí **Asistente BI**, comprobá el modelo en **Estado del chatbot** y enviá
   una pregunta. Confirmá que llega una respuesta en español basada en los datos.

## Producción: Streamlit Cloud

1. Publicá el cambio revisado en la rama conectada a la aplicación.
   La entrada debe seguir siendo `src/dashboard/app.py`.
2. En la configuración de la app → **Secrets**, actualizá estos valores de
   nivel superior; conservá los demás secrets:
   ```toml
   GROQ_API_KEY = "TU_NUEVA_CLAVE"
   GROQ_MODEL = "openai/gpt-oss-20b"
   ```
   El `.env` local **no actualiza** los secrets de producción.
3. Reiniciá la app para descartar clientes y configuración en sesiones previas.
4. Probá una sugerencia del chatbot y una pregunta propia. Verificá también
   que las páginas de indicadores carguen sin depender de Groq.

## Diagnóstico

- **401 / autenticación:** revisar la clave de ese entorno, no compartirla en capturas.
- **Modelo inexistente o sin acceso:** contrastar `GROQ_MODEL` con los modelos
  disponibles para tu cuenta en Groq Console; revisar variables y secrets antiguos.
- **429:** revisar cuotas del modelo y esperar antes de reintentar.
- **Volver atrás:** restaurar una versión de código probada y seleccionar un modelo
  todavía disponible; volver al identificador retirado no recupera el servicio.

Prueba de configuración sin dependencias ni llamadas a la API:
```bash
python -m unittest discover -s tests -p test_groq_model_config.py -v
```
Esta prueba no confirma acceso de la cuenta ni calidad de las respuestas:
la comprobación del chatbot en cada entorno sigue siendo necesaria.
