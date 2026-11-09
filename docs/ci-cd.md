# CI y producción visibles en GitHub

El sitio figura en **About** y cada push a `main` ejecuta pruebas y verifica el
commit publicado en **Actions**. El job de verificación registra su resultado
con el enlace del sitio en **Deployments → production**.

## Flujo

1. Un push o PR hacia `main` ejecuta pytest con Python 3.11 en Ubuntu, sin secretos.
   Se excluye `tests/test_connection.py`: ese script intenta conectar a SQL Server
   durante la colección y no es una prueba aislada.
2. Streamlit Cloud recibe los pushes a su rama conectada y despliega por su cuenta.
3. Solo en `main`, después de pasar las pruebas, Actions abre el sitio con Chromium
   y comprueba cada 3 segundos, durante un máximo de 3 minutos, que aparezca
   **Versión desplegada: SHA completo**, en la página o en el iframe oficial de la app.
4. El entorno `production` queda exitoso únicamente si coincide con el commit de
   esa ejecución. Un sitio disponible pero con una versión anterior no pasa.

**No es una barrera previa al despliegue:** Streamlit puede publicar antes de que
termine CI. Este workflow verifica el despliegue externo, no lo ejecuta ni lo
bloquea. Para exigir CI antes de publicar se necesita otro diseño de ramas o hosting.

## Dónde verlo

- **About:** enlace público de Streamlit.
- **Actions → CI y producción Streamlit:** pruebas y resultado de la comprobación.
- **Deployments → production:** historial con enlace al sitio y commit asociado.
- **Inicio del sitio, pie de página:** versión del checkout Git que ejecuta la app.

## Si falla la verificación

- Revisá los logs de Streamlit: rama `main`, entrada `src/dashboard/app.py` y datos.
- Si se muestra `desconocida`, el hosting no expone un checkout Git legible: la app
  sigue disponible, pero no se afirmará que el commit está verificado.
- Una app dormida, un error al arrancar, una pantalla de acceso o un redeploy lento
  también impiden la confirmación automática. Revisá el sitio antes de reintentar.
- Si llega un push nuevo, se cancela la comprobación del anterior: no debería
  confirmarse un commit que ya fue reemplazado.
- Después de corregir el problema, ejecutá el workflow desde **Run workflow** en
  `main`. Verificará el commit actual; no provoca un nuevo deploy de Streamlit.

## Seguridad y comprobación local

No se pasan claves de Groq ni de SQL Server a Actions. El permiso de escritura
`deployments` se limita al job de producción; los PRs solo ejecutan pruebas.
Las acciones externas están fijadas por SHA y checkout no conserva credenciales.

```bash
.venv/Scripts/python -m pytest tests -q --ignore=tests/test_connection.py
```

La comprobación del commit prueba que la página principal renderiza esa versión;
no confirma respuestas de Groq, calidad de datos ni el funcionamiento de cada página.
Para credenciales y prueba del chatbot, ver [actualizar Groq](actualizar-groq.md).
