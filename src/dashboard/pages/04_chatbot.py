"""
Dashboard — Page 4: Asistente IA (Gemini)
Responsable: Diego Vargas Urzagaste (@temps-code)

Chatbot con contexto del warehouse para responder preguntas en lenguaje natural.
Usa st.chat_input y st.chat_message de Streamlit con Google Gemini API.
Requiere GEMINI_API_KEY en el archivo .env.

SDK: google-genai >= 1.0 (google.genai — NO usar google.generativeai, está deprecado)
"""
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import build_gemini_context
from components.styles import inject_styles

load_dotenv()

st.set_page_config(page_title='Asistente BI — Brecha Digital BI', page_icon=':material/smart_toy:', layout='wide')

inject_styles()

st.html("""
<div class="page-header">
  <h2><i class="ti ti-robot"></i> Asistente BI</h2>
  <p>Consulta los datos del proyecto en lenguaje natural — potenciado por Gemini</p>
</div>
<hr class="divider">
""")

# --- Verificar API key ---
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    st.error(
        '**GEMINI_API_KEY no encontrada.**  \n'
        'Crea un archivo `.env` en la raíz del proyecto con:  \n'
        '```\nGEMINI_API_KEY=tu_clave_aqui\n```'
    )
    st.stop()

# --- Inicializar cliente Gemini (google-genai SDK 1.x) ---
if 'gemini_client' not in st.session_state:
    st.session_state.gemini_client  = None
    st.session_state.gemini_history = []   # lista de dicts {role, parts}
    st.session_state.gemini_ctx     = None
    st.session_state.gemini_error   = None

    try:
        from google import genai  # SDK nuevo: pip install google-genai

        st.session_state.gemini_client = genai.Client(api_key=api_key)

        try:
            st.session_state.gemini_ctx = build_gemini_context()
        except Exception:
            st.session_state.gemini_ctx = (
                'Sos un asistente de Business Intelligence para el proyecto '
                '"Brecha Digital Laboral — UPDS Bolivia". '
                'Respondé preguntas sobre educación técnica, inserción laboral '
                'y brecha digital. Respondé siempre en español.'
            )

    except Exception as e:
        st.session_state.gemini_error = str(e)

if st.session_state.gemini_error:
    st.error(f'Error al inicializar Gemini: {st.session_state.gemini_error}')
    st.caption('Verificá que `google-genai` esté instalado: `pip install google-genai`')
    st.stop()

# --- Historial de mensajes (display) ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Sugerencias (solo si historial vacío) ---
if not st.session_state.messages:
    st.html('<div class="sug-label">Preguntas sugeridas</div>')
    sugerencias = [
        'Cual es la carrera con mayor tasa de empleo?',
        'Cuales son las habilidades mas demandadas en Bolivia?',
        'Que recomendas para reducir la brecha digital?',
        'Como se compara Bolivia con la region en competencias TIC?',
    ]
    cols = st.columns(2)
    for i, sug in enumerate(sugerencias):
        if cols[i % 2].button(sug, key=f'sug_{i}', use_container_width=True):
            st.session_state.messages.append({'role': 'user', 'content': sug})
            st.rerun()
    st.html('<hr class="divider">')

# --- Renderizar historial ---
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# --- Input del usuario ---
if prompt := st.chat_input('Pregunta sobre los datos del proyecto...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    answer = ''
    with st.chat_message('assistant'):
        try:
            from google import genai
            from google.genai import types

            # Construir contents con historial completo para mantener contexto
            contents = []
            for msg in st.session_state.messages[:-1]:  # excluir el último (ya es el prompt actual)
                role = 'user' if msg['role'] == 'user' else 'model'
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part(text=msg['content'])],
                ))
            contents.append(types.Content(
                role='user',
                parts=[types.Part(text=prompt)],
            ))

            # Retry con backoff — el free tier de AI Studio limita a 15 RPM
            import time
            max_retries = 3
            last_err = None
            for attempt in range(max_retries):
                try:
                    response_stream = st.session_state.gemini_client.models.generate_content_stream(
                        model='gemini-1.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=st.session_state.gemini_ctx,
                            temperature=0.7,
                        ),
                    )
                    answer = st.write_stream(
                        chunk.text for chunk in response_stream if chunk.text
                    )
                    last_err = None
                    break
                except Exception as inner_e:
                    last_err = inner_e
                    err_str = str(inner_e)
                    if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str:
                        wait = 5 * (attempt + 1)
                        with st.spinner(f'Limite de API alcanzado — reintentando en {wait}s...'):
                            time.sleep(wait)
                    else:
                        break

            if last_err is not None:
                err = str(last_err)
                if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                    answer = 'La API de Gemini alcanzo el limite de solicitudes por minuto. Esperá unos segundos y volvé a intentar.'
                elif 'API_KEY' in err or 'invalid' in err.lower():
                    answer = 'La API key no es valida. Verificá `GEMINI_API_KEY` en el `.env`.'
                else:
                    answer = f'Error: {err}'
                st.markdown(answer)

        except Exception as e:
            err = str(e)
            answer = f'Error inesperado: {err}'
            st.markdown(answer)

    if answer:
        st.session_state.messages.append({'role': 'assistant', 'content': answer})

# --- Limpiar conversación ---
if st.session_state.messages:
    st.html('<hr class="divider">')
    if st.button('Limpiar conversacion', icon=':material/delete:', use_container_width=False):
        st.session_state.messages         = []
        st.session_state.gemini_history   = []
        st.session_state.pop('gemini_client', None)
        st.rerun()
