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

st.set_page_config(page_title='Asistente BI — Brecha Digital BI', page_icon='🤖', layout='wide')

st.markdown("""
<style>
  .page-header h2 { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem; }
  .page-header p  { color: #9CA3AF; font-size: 0.9rem; margin: 0; }
  .sug-label { font-size: 0.8rem; color: #9CA3AF; margin-bottom: 0.5rem; }
  hr.thin { border: none; border-top: 1px solid #2A2D3E; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h2>🤖 Asistente BI</h2>
  <p>Consultá los datos del proyecto en lenguaje natural — potenciado por Gemini</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- Verificar API key ---
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    st.error('**GEMINI_API_KEY no encontrada.** Agregá `GEMINI_API_KEY=tu_clave` en el `.env` del proyecto.')
    st.stop()

# --- Inicializar modelo Gemini (mismo patrón que Road-to-build-with-AI) ---
if 'gemini_model' not in st.session_state:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        st.session_state.gemini_model   = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=build_gemini_context(),
        )
        st.session_state.gemini_history = []
        st.session_state.gemini_error   = None
    except Exception as e:
        st.session_state.gemini_model = None
        st.session_state.gemini_error = str(e)

if st.session_state.get('gemini_error'):
    st.error(f'Error al inicializar Gemini: {st.session_state.gemini_error}')
    st.stop()

# --- Inicializar historial de mensajes ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Sugerencias (solo si historial vacío) ---
if not st.session_state.messages:
    st.markdown('<div class="sug-label">Preguntas sugeridas</div>', unsafe_allow_html=True)
    sugerencias = [
        '¿Cuál es la carrera con mayor tasa de empleo?',
        '¿Cuáles son las habilidades más demandadas en Bolivia?',
        '¿Qué recomendás para reducir la brecha digital?',
        '¿Cómo se compara Bolivia con la región en competencias TIC?',
    ]
    cols = st.columns(2)
    for i, sug in enumerate(sugerencias):
        if cols[i % 2].button(sug, key=f'sug_{i}', use_container_width=True):
            st.session_state.messages.append({'role': 'user', 'content': sug})
            st.rerun()
    st.markdown('<hr class="thin">', unsafe_allow_html=True)

# --- Historial de chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# --- Input ---
if prompt := st.chat_input('Preguntá sobre los datos del proyecto...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Analizando...'):
            try:
                chat = st.session_state.gemini_model.start_chat(
                    history=st.session_state.gemini_history,
                )
                response = chat.send_message(
                    prompt,
                    request_options={'timeout': 15},
                )
                answer = response.text
                st.session_state.gemini_history = chat.history
            except Exception as e:
                err = str(e)
                if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                    answer = '⏳ La API de Gemini alcanzó el límite de solicitudes por minuto. Esperá unos segundos y volvé a intentar.'
                else:
                    answer = f'Error al consultar Gemini: {err}'
        st.markdown(answer)
        st.session_state.messages.append({'role': 'assistant', 'content': answer})

# --- Limpiar ---
if st.session_state.messages:
    st.markdown('<hr class="thin">', unsafe_allow_html=True)
    if st.button('🗑️ Limpiar conversación', use_container_width=False):
        st.session_state.messages         = []
        st.session_state.gemini_history   = []
        st.session_state.pop('gemini_model', None)
        st.rerun()
