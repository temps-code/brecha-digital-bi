"""
Dashboard — Page 4: Asistente IA (Groq + LLaMA)
Responsable: Diego Vargas Urzagaste (@temps-code)

Chatbot con contexto del warehouse para responder preguntas en lenguaje natural.
Usa Groq API (free tier generoso: 30 RPM, sin límite diario).
Requiere GROQ_API_KEY en el archivo .env — obtener en: https://console.groq.com
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

st.set_page_config(
    page_title='Asistente BI — Brecha Digital BI',
    page_icon=':material/smart_toy:',
    layout='wide',
)

inject_styles()

st.html("""
<div class="page-header">
  <h2><i class="ti ti-robot"></i> Asistente BI</h2>
  <p>Consulta los datos del proyecto en lenguaje natural — LLaMA 3 via Groq</p>
</div>
<hr class="divider">
""")

_MODEL  = 'llama-3.1-8b-instant'   # 30 RPM, 131k tokens/min, free tier sin límite diario
_SYSTEM = None                       # se construye en la inicialización

# --- Verificar API key ---
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    st.error(
        '**GROQ_API_KEY no encontrada.**  \n'
        'Conseguí tu clave gratis en [console.groq.com](https://console.groq.com) '
        'y agregá al `.env`:  \n'
        '```\nGROQ_API_KEY=gsk_...\n```'
    )
    st.stop()

# --- Inicializar cliente Groq ---
if 'groq_client' not in st.session_state:
    try:
        from groq import Groq
        st.session_state.groq_client = Groq(api_key=api_key)
        try:
            st.session_state.groq_system = build_gemini_context()
        except Exception:
            st.session_state.groq_system = (
                'Sos un asistente de Business Intelligence para el proyecto '
                '"Brecha Digital Laboral — UPDS Bolivia 2026". '
                'Respondé preguntas sobre inserción laboral, habilidades TIC '
                'y brecha digital. Respondé siempre en español, de forma concisa.'
            )
        st.session_state.groq_error = None
    except Exception as e:
        st.session_state.groq_client = None
        st.session_state.groq_error  = str(e)

if st.session_state.get('groq_error'):
    st.error(f'Error al inicializar Groq: {st.session_state.groq_error}')
    st.stop()

# --- Historial de mensajes ---
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

    # Construir mensajes para la API (sistema + historial completo)
    api_messages = [{'role': 'system', 'content': st.session_state.groq_system}]
    for msg in st.session_state.messages:
        api_messages.append({'role': msg['role'], 'content': msg['content']})

    answer = ''
    with st.chat_message('assistant'):
        placeholder = st.empty()
        # Cursor parpadeante — el usuario sabe que se está procesando
        placeholder.markdown('▌')

        try:
            stream = st.session_state.groq_client.chat.completions.create(
                model=_MODEL,
                messages=api_messages,
                stream=True,
                temperature=0.7,
                max_tokens=1024,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content or ''
                answer += delta
                # Actualizar el placeholder con el texto acumulado + cursor
                placeholder.markdown(answer + '▌')

            # Renderizado final sin cursor
            placeholder.markdown(answer)

        except Exception as e:
            err = str(e)
            if '429' in err or 'rate_limit' in err.lower():
                answer = 'Limite de solicitudes alcanzado. Espera unos segundos y volvé a intentar.'
            elif 'auth' in err.lower() or 'api_key' in err.lower():
                answer = 'GROQ_API_KEY invalida. Verificá el valor en el `.env`.'
            else:
                answer = f'Error: {err}'
            placeholder.markdown(answer)

    if answer:
        st.session_state.messages.append({'role': 'assistant', 'content': answer})

# --- Limpiar conversación ---
if st.session_state.messages:
    st.html('<hr class="divider">')
    if st.button('Limpiar conversacion', icon=':material/delete:', use_container_width=False):
        st.session_state.messages = []
        st.session_state.pop('groq_client', None)
        st.rerun()
