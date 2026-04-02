# Guía de Git y GitHub — Para el equipo

**Para:** Todo el equipo  
**Objetivo:** Entender cómo usar Git y GitHub para trabajar en este proyecto sin romperse la cabeza

---

## ¿Para qué sirve Git?

Git es una herramienta que guarda el historial de todos los cambios que hacés en el código. Pensalo como un "Control Z" infinito que además permite que varias personas trabajen en el mismo proyecto sin pisarse entre sí.

**GitHub** es el sitio web donde guardamos ese historial en la nube, para que todo el equipo pueda acceder.

La regla de oro es simple: **nunca trabajás directamente en `main`**. Main es la versión oficial del proyecto — siempre creás tu propia rama, trabajás ahí, y después pedís que se incorpore.

---

## Antes de arrancar — Una sola vez

### 1. Clonar el repositorio

Esto descarga el proyecto a tu computadora. Solo lo hacés una vez.

```bash
git clone https://github.com/temps-code/brecha-digital-bi.git
cd brecha-digital-bi
```

### 2. Verificar que Git sabe quién sos

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

Usá el mismo email que usaste para crear tu cuenta de GitHub.

---

## El flujo de trabajo del proyecto

Cada vez que empezás a trabajar en tu fase, seguís estos pasos en orden.

### Paso 1 — Actualizá tu copia local

Antes de tocar cualquier archivo, asegurate de tener la versión más reciente:

```bash
git checkout main
git pull origin main
```

Esto evita conflictos con cambios que otros hicieron mientras no trabajabas.

### Paso 2 — Creá tu rama de trabajo

Nunca trabajés en `main`. Creá tu propia rama con el nombre de tu fase:

```bash
git checkout -b feature/tu-fase
```

Por ejemplo:
- `git checkout -b feature/silver` (Juan)
- `git checkout -b feature/gold` (Micaela)
- `git checkout -b feature/notebooks` (Mayra)

Si la rama ya existe porque la creaste antes:

```bash
git checkout feature/tu-fase
```

### Paso 3 — Trabajá normalmente

Abrí los archivos, escribí código, guardá. Git no hace nada automático — vos decidís cuándo guardar un "punto de control".

### Paso 4 — Guardá tu progreso (commit)

Cuando terminés algo concreto (una función, un archivo, una corrección), guardalo:

```bash
git add .
git commit -m "feat: descripción de lo que hiciste"
```

**¿Qué poner en el mensaje?** Algo breve y descriptivo:
- `feat: implementar extracción de estudiantes desde SQL Server`
- `fix: corregir nulos en columna ciudad`
- `docs: agregar comentarios a clean.py`

> Hacé commits seguido — no esperés a terminar todo. Un commit es como guardar en un videojuego: si algo sale mal, podés volver a ese punto.

### Paso 5 — Subí tu rama a GitHub

```bash
git push origin feature/tu-fase
```

La primera vez que pusheás una rama nueva, Git te va a pedir que confirmes. Hacé lo que te dice (normalmente te muestra el comando exacto).

### Paso 6 — Avisale a Diego que terminaste

Una vez que tu trabajo está listo y pusheado, entrá a GitHub, buscá tu rama y creá un **Pull Request** (PR). También podés avisarle directamente a Diego (@temps-code).

---

## Cómo crear un Pull Request

1. Entrá a `https://github.com/temps-code/brecha-digital-bi`
2. GitHub te va a mostrar un banner amarillo que dice "Compare & pull request" — hacé clic ahí
3. Poné un título descriptivo: `feat(silver): implementa limpieza y normalización`
4. En la descripción contá brevemente qué hiciste
5. Hacé clic en **Create pull request**
6. Mové la tarjeta del Kanban a **Testing/Review** y avisale a Diego

Diego va a revisar, dejar comentarios si hay algo para corregir, y cuando esté todo bien va a hacer el merge (incorporar tu trabajo a main).

---

## Errores comunes y cómo resolverlos

### "Your branch is behind 'origin/main'"

Alguien hizo cambios en main mientras vos trabajabas. Actualizá tu rama:

```bash
git checkout main
git pull origin main
git checkout feature/tu-fase
git merge main
```

### "Please commit your changes or stash them"

Tenés cambios sin guardar y Git no puede seguir. Dos opciones:

**Opción A — Guardarlos primero:**
```bash
git add .
git commit -m "wip: guardando progreso"
```

**Opción B — Guardarlos temporalmente (stash):**
```bash
git stash
# hacés lo que necesitabas
git stash pop  # recuperás tus cambios
```

### "Merge conflict"

Conflicto: dos personas editaron el mismo archivo en el mismo lugar. Git no sabe cuál versión conservar y te pide que lo resuelvas vos.

Abrí el archivo conflictivo — vas a ver algo así:

```
<<<<<<< HEAD
tu versión del código
=======
la versión de main
>>>>>>> main
```

Editá el archivo para quedarte con lo correcto (puede ser una versión, la otra, o una combinación), borrá las líneas con `<<<<`, `====` y `>>>>`, y después:

```bash
git add .
git commit -m "fix: resolver conflicto en clean.py"
```

Si no sabés cómo resolverlo, avisale a Diego antes de tocar nada.

### "Permission denied" al hacer push

Tu sesión de GitHub venció. Necesitás volver a autenticarte:

```bash
gh auth login
```

Seguí los pasos que te muestra en pantalla.

---

## Comandos de referencia rápida

| Qué querés hacer | Comando |
|------------------|---------|
| Ver el estado actual | `git status` |
| Ver qué cambió en los archivos | `git diff` |
| Ver el historial de commits | `git log --oneline` |
| Ver en qué rama estás | `git branch` |
| Cambiar de rama | `git checkout nombre-de-rama` |
| Deshacer cambios en un archivo (antes del commit) | `git checkout -- nombre-archivo` |
| Ver las ramas remotas | `git branch -r` |

---

## Reglas del equipo

1. **Nunca pusheés directo a `main`** — siempre trabajá en tu rama
2. **Commiteá seguido** — no acumulés un día entero de trabajo en un solo commit
3. **Mensajes descriptivos** — el equipo tiene que entender qué hiciste sin abrir el archivo
4. **Si rompés algo**, avisale a Diego antes de intentar arreglarlo solo — puede ser peor
5. **Antes de empezar cada día**, hacé `git pull origin main` para tener la última versión

---

## ¿Necesitás ayuda?

Avisale a Diego (@temps-code) por el canal del equipo. No te quedes trabado — perder 30 minutos intentando resolver un error de Git es tiempo que le sacás al proyecto.
