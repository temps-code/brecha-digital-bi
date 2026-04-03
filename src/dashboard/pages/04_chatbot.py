"""
Dashboard — Page 4: Asistente IA (Groq + LLaMA)
Responsable: Diego Vargas Urzagaste (@temps-code)

Chatbot con contexto del warehouse. Usa Groq API (free tier: 30 RPM, sin límite diario).
Requiere GROQ_API_KEY en el archivo .env — obtener en: https://console.groq.com
"""
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Path absoluto al .env — garantiza que siempre lo encuentra independiente del CWD
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

# ── DEBUG PANEL (sidebar) ─────────────────────────────────────────────────────
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

# ── VERIFICAR API KEY ─────────────────────────────────────────────────────────
api_key = os.getenv('GROQ_API_KEY', '').strip()
if not api_key:
    st.error(
        '**GROQ_API_KEY no encontrada.**  \n'
        f'Ruta buscada: `{_ROOT / ".env"}`  \n'
        'Agregá `GROQ_API_KEY=gsk_...` a ese archivo.'
    )
    st.stop()

# ── INICIALIZAR CLIENTE (una sola vez por sesión) ─────────────────────────────
if 'groq_client' not in st.session_state:
    st.session_state.groq_client = None
    st.session_state.groq_error  = None
    st.session_state.groq_system = _SYSTEM_FALLBACK

    try:
        from groq import Groq
        st.session_state.groq_client = Groq(api_key=api_key)

        # Enriquecer el contexto con los KPIs si están disponibles
        try:
            from components.data_loader import build_gemini_context
            ctx = build_gemini_context()
            if ctx:
                st.session_state.groq_system = ctx
        except Exception:
            pass  # contexto básico ya está seteado en groq_system

    except Exception as e:
        st.session_state.groq_error = str(e)

if st.session_state.groq_error:
    st.error(f'Error al inicializar Groq: `{st.session_state.groq_error}`')
    st.caption('Verificá que `groq` esté instalado: `pip install groq --break-system-packages`')
    st.stop()

if st.session_state.groq_client is None:
    st.error('Cliente Groq no inicializado. Revisá el panel de debug en el sidebar.')
    st.stop()

# ── HISTORIAL ─────────────────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ── SUGERENCIAS (solo si historial vacío) ─────────────────────────────────────
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

# ── RENDERIZAR HISTORIAL ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# ── INPUT Y GENERACIÓN ────────────────────────────────────────────────────────
if prompt := st.chat_input('Preguntá sobre los datos del proyecto...'):

    # 1. Mostrar mensaje del usuario
    with st.chat_message('user'):
        st.markdown(prompt)

    # 2. Construir historial para la API
    api_messages = [{'role': 'system', 'content': st.session_state.groq_system}]
    for msg in st.session_state.messages:
        api_messages.append({'role': msg['role'], 'content': msg['content']})
    api_messages.append({'role': 'user', 'content': prompt})

    # 3. Generar respuesta con streaming visible
    answer = ''
    with st.chat_message('assistant'):
        placeholder = st.empty()
        placeholder.markdown('▌')  # cursor visible inmediatamente

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
                placeholder.markdown(answer + '▌')

            placeholder.markdown(answer)

        except Exception as e:
            err = str(e)
            if '429' in err or 'rate_limit' in err.lower():
                answer = 'Límite de solicitudes alcanzado. Esperá unos segundos y volvé a intentar.'
            elif 'auth' in err.lower() or 'api_key' in err.lower():
                answer = 'GROQ_API_KEY inválida. Verificá el sidebar para más detalles.'
            else:
                answer = f'Error inesperado: {err}'
            placeholder.markdown(answer)

    # 4. Persistir historial
    st.session_state.messages.append({'role': 'user',      'content': prompt})
    st.session_state.messages.append({'role': 'assistant', 'content': answer})

# ── LIMPIAR ───────────────────────────────────────────────────────────────────
if st.session_state.messages:
    st.html('<hr class="divider">')
    if st.button('Limpiar conversacion', icon=':material/delete:'):
        for k in ['messages', 'groq_client', 'groq_error', 'groq_system']:
            st.session_state.pop(k, None)
        st.rerun()
