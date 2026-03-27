# 🤝 Módulo 5: Trabajo en equipo y colaboración entre forks

## 🎯 Objetivo

Entender cómo dos estudiantes pueden partir de un repositorio del profesor, trabajar en sus propios forks y colaborar entre ellos para construir una solución compartida sin modificar el repositorio original del docente.

## 🌍 Contexto real de esta clase

En este curso, el repositorio del profesor funciona como base de trabajo:

- contiene instrucciones, tareas o archivos iniciales
- sirve como punto de partida común
- no debe recibir directamente los cambios de los estudiantes

Eso significa que los estudiantes no trabajan para hacer merge en el repositorio del profesor. En cambio:

- cada estudiante hace un `fork` del repositorio del profesor
- cada estudiante trabaja en su propio workspace
- los estudiantes colaboran entre sí sobre uno de sus propios repositorios
- la solución final vive en el repositorio del equipo de estudiantes, no en el repositorio del profesor

Este modelo se parece mucho a un entorno académico o a un trabajo por equipos donde el docente entrega la plantilla y cada grupo construye su propia versión.

## 🧠 Conceptos clave

### Fork

Un `fork` es una copia de un repositorio en tu propia cuenta de GitHub.

En esta clase, el `fork` sirve para que cada estudiante tenga independencia sobre su trabajo sin tocar el repositorio del profesor.

### Origin

`origin` suele apuntar al repositorio propio del estudiante.

Ejemplo:

- Ana hace fork del repositorio del profesor
- en la copia local de Ana, `origin` apunta a `ana/repositorio`

### Upstream

`upstream` apunta al repositorio original del profesor.

Esto sirve para traer cambios nuevos del docente si el material del curso se actualiza.

### Colaborador

Un colaborador es una persona a la que se le da permiso para escribir directamente en un repositorio.

En este escenario, Ana y Luis pueden colaborar de dos formas:

- revisándose por Pull Requests entre sus forks
- o definiendo un repositorio de equipo y agregándose mutuamente como colaboradores

## 👥 Escenario pedagógico correcto

Imagina este caso:

- el profesor tiene `profesor/curso-git`
- Ana hace fork a `ana/curso-git`
- Luis hace fork a `luis/curso-git`

Hasta aquí, Ana y Luis tienen dos copias separadas del repositorio del profesor. Si no hacen nada más, cada uno trabajará aislado.

Para colaborar de verdad entre ellos, necesitan elegir una estrategia de equipo.

## ✅ Estrategia recomendada para esta clase

La forma más clara de trabajo es esta:

1. ambos hacen fork del repositorio del profesor
2. el equipo decide cuál de los dos forks será el repositorio principal del grupo
3. el dueño de ese fork agrega al otro estudiante como colaborador
4. ambos trabajan sobre ese mismo repositorio del equipo, pero cada uno desde su propio workspace y sus propias ramas

Ejemplo:

- el profesor tiene `profesor/curso-git`
- Ana tiene `ana/curso-git`
- Luis tiene `luis/curso-git`
- el equipo decide usar `ana/curso-git` como repositorio del grupo
- Ana agrega a Luis como colaborador en `ana/curso-git`

Resultado:

- el repositorio del profesor permanece intacto
- Ana y Luis trabajan sobre la solución de su equipo en `ana/curso-git`
- Luis ya no necesita subir la solución final al repo del profesor

## 🖥 Tutorial paso a paso

### Paso 1. Cada estudiante hace fork del repositorio del profesor

Desde GitHub:

1. entrar al repositorio del profesor
2. hacer clic en `Fork`
3. crear la copia en su propia cuenta

Al final habrá algo así:

- `profesor/curso-git`
- `ana/curso-git`
- `luis/curso-git`

### Paso 2. El equipo define cuál fork será el repositorio compartido

Ana y Luis deben ponerse de acuerdo.

Ejemplo:

- usarán `ana/curso-git` como repositorio del equipo

### Paso 3. El dueño del fork agrega al compañero como colaborador

En GitHub, Ana hace esto:

1. entra a `ana/curso-git`
2. va a `Settings`
3. entra a `Collaborators`
4. invita a Luis

Cuando Luis acepta, ambos podrán hacer `push` a `ana/curso-git`.

### Paso 4. Cada uno abre su propio workspace

Aquí está la parte importante: aunque ambos trabajen sobre el mismo repositorio del equipo, cada uno debe trabajar en su propio workspace.

Eso significa:

- Ana abre un Codespace o una copia local
- Luis abre otro Codespace o su propia copia local

No comparten la misma terminal ni el mismo editor en vivo. Comparten el mismo repositorio remoto del equipo.

### Paso 5. Configurar remotos correctamente

#### En el workspace de Ana

Lo normal es que `origin` apunte a `ana/curso-git`.

Además, puede agregar el repositorio del profesor como `upstream`:

```bash
git remote add upstream https://github.com/profesor/curso-git.git
```

#### En el workspace de Luis

Luis tiene dos opciones.

La más clara para esta clase es clonar directamente el repositorio del equipo, no seguir trabajando sobre su fork personal.

Entonces, Luis clona `ana/curso-git` y trabaja ahí.

En ese caso:

- `origin` apunta a `ana/curso-git`
- `upstream` puede apuntar a `profesor/curso-git`

Ejemplo:

```bash
git remote add upstream https://github.com/profesor/curso-git.git
```

## 🌿 Paso 6. Cada estudiante trabaja en su propia rama

Aunque ambos usen el mismo repositorio del equipo, no deben trabajar en la misma rama.

Ejemplo:

### Ana

```bash
git switch -c feature/estructura-curso
```

### Luis

```bash
git switch -c feature/mejora-ejercicios
```

Esto evita que se pisen y facilita la revisión.

## 💾 Paso 7. Hacer cambios, commit y push

Ejemplo general:

```bash
git status
git add .
git commit -m "Agrega cambios del modulo de colaboracion"
git push origin feature/nombre-rama
```

## 🔀 Paso 8. Colaborar entre ellos con Pull Requests

Aquí el Pull Request ya no va hacia el repositorio del profesor.

Va hacia el repositorio del equipo.

Ejemplo:

- Ana abre PR desde `feature/estructura-curso` hacia `main` en `ana/curso-git`
- Luis revisa ese PR y deja comentarios
- Ana ajusta, hace commit y vuelve a hacer `push`

Después:

- Luis abre PR desde `feature/mejora-ejercicios` hacia `main` en `ana/curso-git`
- Ana revisa ese PR y deja comentarios

Así colaboran de verdad entre ellos.

## 🔁 Paso 9. Mantenerse al día con el repositorio del profesor

Si el profesor actualiza la plantilla o agrega nuevas instrucciones, el equipo puede traer esos cambios desde `upstream`.

```bash
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

Con eso:

- traen actualizaciones del profesor
- actualizan la rama `main` del repositorio del equipo
- mantienen su solución al día sin tocar el repo original del docente

## 🧭 Resumen del flujo correcto para esta clase

1. el profesor publica el repositorio base
2. Ana y Luis hacen fork
3. eligen uno de sus forks como repositorio del equipo
4. el dueño agrega al otro como colaborador
5. ambos trabajan desde workspaces separados
6. cada uno crea su rama
7. hacen commits y push al repositorio del equipo
8. se revisan mediante Pull Requests entre ellos
9. la solución final queda en el repositorio del equipo
10. el repositorio del profesor no se modifica

## ✅ Ventajas de este modelo

- protege el repositorio del profesor
- cada equipo construye su propia solución
- fomenta colaboración real entre estudiantes
- permite practicar ramas, commits, PR y revisión
- se parece al trabajo en equipos reales

## 🚫 Qué no se recomienda

- que ambos trabajen directamente en `main`
- que ambos editen la misma rama al mismo tiempo
- que uno trabaje en su fork y el otro en otro fork sin definir un repositorio común del equipo
- que intenten usar el repositorio del profesor como si fuera el repositorio de entrega

## 🧑‍🏫 Idea profesional

En este curso, el repositorio del profesor es la fuente de la tarea, no el destino del trabajo del estudiante. El destino real del trabajo es el repositorio del equipo, donde Ana y Luis organizan su solución, colaboran entre ramas y aprenden a revisar cambios entre ellos.
