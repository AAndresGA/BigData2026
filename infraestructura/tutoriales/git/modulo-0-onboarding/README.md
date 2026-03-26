# 🧭 Módulo 0: Onboarding (arranque del curso)

## 🎯 Objetivo

Dejar el entorno listo para trabajar desde el primer ejercicio, evitando bloqueos típicos de estudiantes que recién empiezan.

Si todavía no instalaste Docker, inicia por `INSTALACION_DESDE_CERO.md` y `docker/README.md`.

## 🌍 Contexto

Muchos errores de Git al inicio no son conceptuales, sino de entorno:

- abrir el repositorio equivocado
- no saber en qué rama se está trabajando
- no tener configurado nombre/correo en Git
- no entender dónde ejecutar los comandos

Este módulo corrige eso antes de entrar a contenidos técnicos.

## ✅ Checklist de inicio

Antes de comenzar el curso, cada estudiante debe confirmar:

- tiene Docker Desktop funcionando
- levantó contenedores del curso (`airflow`, `dask`, `git`)
- tiene cuenta de GitHub activa
- entró al repositorio correcto de la clase
- abrió su workspace (Codespaces o local)
- ve la terminal y puede ejecutar comandos
- configuró identidad de Git (`user.name`, `user.email`)

## 🖥 Flujo recomendado para clase

### 1. Levantar entorno Docker del curso

```bash
cd docker
docker compose up -d
docker compose ps
```

Si `docker compose` no funciona, vuelve a la guía de instalación en `docker/README.md`.

### 2. Entrar al repositorio asignado

El estudiante debe entrar por el enlace entregado por el profesor.

### 3. Abrir Codespaces

Desde GitHub:

1. botón `Code`
2. pestaña `Codespaces`
3. opción `Create codespace`

### 4. Verificar identidad en Git

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

### 5. Confirmar configuración

```bash
git config --global --get user.name
git config --global --get user.email
```

### 6. Revisar estado del repositorio

```bash
git status
git branch --show-current
```

### 7. Validar herramientas dentro de contenedor

```bash
docker compose exec git git --version
docker compose exec airflow airflow version
docker compose exec dask-scheduler dask --version
```

## ⚠️ Errores comunes y solución

### Error: "Please tell me who you are"

Causa: Git no tiene nombre/correo configurado.

Solución:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

### Error: "not a git repository"

Causa: la terminal está abierta en la carpeta equivocada.

Solución: moverse a la carpeta del repositorio correcto.

### Error: cambios en `main` por accidente

Causa: no se creó rama antes de trabajar.

Solución: crear rama de trabajo antes de editar archivos.

### Error: "Cannot connect to the Docker daemon"

Causa: Docker Desktop no está iniciado o el daemon no está disponible.

Solución: iniciar Docker Desktop y volver a ejecutar `docker compose up -d`.

## 🧠 Resultado esperado del módulo

Al finalizar, el estudiante puede:

- ubicarse en el repositorio correcto
- usar terminal sin bloqueo inicial
- verificar su configuración de Git
- comenzar los ejercicios del curso con flujo ordenado
