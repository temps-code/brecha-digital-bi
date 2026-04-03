"""
Dashboard — Page 4: Asistente IA (Gemini)
Responsable: Diego Vargas Urzagaste (@temps-code)

Chatbot con contexto del warehouse para responder preguntas en lenguaje natural.
Usa st.chat_input y st.chat_message de Streamlit con Google Gemini API.
Requiere GEMINI_API_KEY en el archivo .env.
"""
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.data_loader import build_gemini_context

load_dotenv()

st.title('🤖 Asistente BI')
st.caption('Consultá los datos del proyecto en lenguaje natural — potenciado por Gemini')

# --- Verificar API key ---
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    st.error(
        '**GEMINI_API_KEY no encontrada.** '
        'Agregá `GEMINI_API_KEY=tu_clave` en el archivo `.env` del proyecto.'
    )
    st.stop()

# --- Inicializar historial de chat ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'gemini_chat' not in st.session_state:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=build_gemini_context(),
        )
        st.session_state.gemini_chat = model.start_chat(history=[])
        st.session_state.gemini_error = None
    except Exception as e:
        st.session_state.gemini_chat = None
        st.session_state.gemini_error = str(e)

if st.session_state.get('gemini_error'):
    st.error(f'Error al inicializar Gemini: {st.session_state.gemini_error}')
    st.stop()

# --- Sugerencias de preguntas ---
if not st.session_state.messages:
    st.markdown('**Preguntas sugeridas:**')
    sugerencias = [
        '¿Cuál es la carrera con mayor tasa de empleo?',
        '¿Cuáles son las habilidades más demandadas en Bolivia?',
        '¿Qué recomendás para reducir la brecha digital?',
        '¿Cómo se compara Bolivia con la región en competencias TIC?',
    ]
    cols = st.columns(2)
    for i, sug in enumerate(sugerencias):
        if cols[i % 2].button(sug, key=f'sug_{i}'):
            st.session_state.messages.append({'role': 'user', 'content': sug})
            st.rerun()

# --- Mostrar historial ---
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# --- Input del usuario ---
if prompt := st.chat_input('Preguntá sobre los datos del proyecto...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Analizando...'):
            try:
                response = st.session_state.gemini_chat.send_message(prompt)
                answer = response.text
            except Exception as e:
                answer = f'Error al consultar Gemini: {e}'
        st.markdown(answer)
        st.session_state.messages.append({'role': 'assistant', 'content': answer})

# --- Botón limpiar historial ---
if st.session_state.messages:
    st.divider()
    if st.button('Limpiar conversación'):
        st.session_state.messages = []
        st.session_state.pop('gemini_chat', None)
        st.rerun()
