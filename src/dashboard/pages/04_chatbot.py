"""
Dashboard — Page 4: Asistente IA (Groq + LLaMA)
Responsable: Diego Vargas Urzagaste (@temps-code)

Chatbot con contexto del warehouse. Usa Groq API (free tier: 30 RPM, sin límite diario).
Requiere GROQ_API_KEY en el archivo .env — obtener en: https://console.groq.com
"""
import os
import sys
import traceback
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_ROOT / '.env', override=False)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from components.styles import inject_styles

_MODEL = 'llama-3.1-8b-instant'
_SYSTEM_FALLBACK = (
    'Sos un asistente de Business Intelligence para el proyecto '
    '"Brecha Digital Laboral — UPDS Bolivia 2026". '
    'Respondé preguntas sobre inserción laboral, habilidades TIC y brecha digital. '
    'Respondé siempre en español, de forma concisa y orientada a datos.'
)

st.set_page_config(
    page_title='Asistente BI — Brecha Digital BI',
    page_icon=':material/smart_toy:',
    layout='wide',
)

inject_styles()

# ── DEBUG PANEL ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('---')
    with st.expander('Estado del chatbot', expanded=False):
        api_key_debug = os.getenv('GROQ_API_KEY', '')
        st.write(f'GROQ_API_KEY: `{"OK — " + api_key_debug[:8] + "..." if api_key_debug else "NO ENCONTRADA"}`')
        st.write(f'.env path: `{_ROOT / ".env"}`')
        st.write(f'.env existe: `{(_ROOT / ".env").exists()}`')
        st.write(f'groq_client en session: `{"groq_client" in st.session_state}`')
        st.write(f'groq_error: `{st.session_state.get("groq_error", "ninguno")}`')
        st.write(f'mensajes: `{len(st.session_state.get("messages", []))}`')
        if st.button('Reiniciar chatbot', use_container_width=True):
            for k in ['groq_client', 'groq_error', 'groq_system', 'messages']:
                st.session_state.pop(k, None)
            st.rerun()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.html("""
<div class="page-header">
  <h2><i class="ti ti-robot"></i> Asistente BI</h2>
  <p>Consultá los datos del proyecto en lenguaje natural — LLaMA 3 via Groq</p>
</div>
<hr class="divider">
""")

# ── API KEY ───────────────────────────────────────────────────────────────────
api_key = os.getenv('GROQ_API_KEY', '').strip()
if not api_key:
    st.error(f'GROQ_API_KEY no encontrada en `{_ROOT / ".env"}`')
    st.stop()

# ── CLIENTE ───────────────────────────────────────────────────────────────────
if 'groq_client' not in st.session_state:
    print('[chatbot] inicializando cliente Groq...')
    st.session_state.groq_client = None
    st.session_state.groq_error  = None
    st.session_state.groq_system = _SYSTEM_FALLBACK
    try:
        from groq import Groq
        st.session_state.groq_client = Groq(api_key=api_key)
        print('[chatbot] cliente Groq OK')
        try:
            from components.data_loader import build_gemini_context
            st.session_state.groq_system = build_gemini_context()
            print('[chatbot] contexto KPIs cargado OK')
        except Exception as ctx_err:
            print(f'[chatbot] contexto KPIs fallido (usando fallback): {ctx_err}')
    except Exception as e:
        st.session_state.groq_error = str(e)
        print(f'[chatbot] ERROR inicializando Groq: {e}')

if st.session_state.groq_error:
    st.error(f'Error al inicializar Groq: `{st.session_state.groq_error}`')
    st.stop()

if st.session_state.groq_client is None:
    st.error('Cliente Groq no disponible. Revisá la consola del servidor.')
    st.stop()

# ── HISTORIAL ─────────────────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ── SUGERENCIAS ───────────────────────────────────────────────────────────────
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

# ── HISTORIAL RENDERIZADO ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# ── INPUT ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input('Preguntá sobre los datos del proyecto...'):
    print(f'[chatbot] prompt recibido: {prompt[:50]}')

    # Mostrar mensaje del usuario
    with st.chat_message('user'):
        st.markdown(prompt)

    # Construir historial para la API
    api_messages = [{'role': 'system', 'content': st.session_state.groq_system}]
    for msg in st.session_state.messages:
        api_messages.append({'role': msg['role'], 'content': msg['content']})
    api_messages.append({'role': 'user', 'content': prompt})

    print(f'[chatbot] enviando {len(api_messages)} mensajes a Groq...')

    # Generar respuesta
    answer = ''
    with st.chat_message('assistant'):
        try:
            # Generador que hace streaming desde Groq
            def _groq_stream():
                stream = st.session_state.groq_client.chat.completions.create(
                    model=_MODEL,
                    messages=api_messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=1024,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta

            # st.write_stream renderiza el generador en tiempo real dentro del chat bubble
            answer = st.write_stream(_groq_stream())
            print(f'[chatbot] respuesta recibida: {len(answer)} chars')

        except Exception as e:
            tb = traceback.format_exc()
            print(f'[chatbot] ERROR en generación:\n{tb}')
            err = str(e)
            if '429' in err or 'rate_limit' in err.lower():
                answer = 'Límite de solicitudes alcanzado. Esperá unos segundos y volvé a intentar.'
            elif 'auth' in err.lower() or 'api_key' in err.lower():
                answer = 'GROQ_API_KEY inválida. Verificá el sidebar.'
            else:
                answer = f'Error: {err}'
            st.markdown(answer)

    # Persistir en historial
    st.session_state.messages.append({'role': 'user',      'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': answer or '(sin respuesta)'})
    print(f'[chatbot] historial actualizado: {len(st.session_state.messages)} mensajes')

# ── LIMPIAR ───────────────────────────────────────────────────────────────────
if st.session_state.messages:
    st.html('<hr class="divider">')
    if st.button('Limpiar conversacion', icon=':material/delete:'):
        for k in ['messages', 'groq_client', 'groq_error', 'groq_system']:
            st.session_state.pop(k, None)
        st.rerun()
