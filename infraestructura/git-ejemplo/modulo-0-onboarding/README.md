# 🧭 Módulo 0: Onboarding (arranque del curso)

## 🎯 Objetivo

Dejar el entorno listo para trabajar desde el primer ejercicio, evitando bloqueos típicos de estudiantes que recién empiezan.

## 🌍 Contexto

Muchos errores de Git al inicio no son conceptuales, sino de entorno:

- abrir el repositorio equivocado
- no saber en qué rama se está trabajando
- no tener configurado nombre/correo en Git
- no entender dónde ejecutar los comandos

Este módulo corrige eso antes de entrar a contenidos técnicos.

## ✅ Checklist de inicio

Antes de comenzar el curso, cada estudiante debe confirmar:

- tiene cuenta de GitHub activa
- entró al repositorio correcto de la clase
- abrió su workspace (Codespaces o local)
- ve la terminal y puede ejecutar comandos
- configuró identidad de Git (`user.name`, `user.email`)

## 🖥 Flujo recomendado para clase

### 1. Entrar al repositorio asignado

El estudiante debe entrar por el enlace entregado por el profesor.

### 2. Abrir Codespaces

Desde GitHub:

1. botón `Code`
2. pestaña `Codespaces`
3. opción `Create codespace`

### 3. Verificar identidad en Git

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

### 4. Confirmar configuración

```bash
git config --global --get user.name
git config --global --get user.email
```

### 4.5. 🔐 Conectar a GitHub con SSH (Importante)

Para hacer push y pull sin escribir contraseña, necesitas una clave SSH.

#### Generar clave SSH:

```bash
ssh-keygen -t rsa -b 4096 -C "tu-correo@ejemplo.com"
```

Presiona `Enter` tres veces (sin agregar passphrase es más simple para empezar).

#### Ver tu clave pública:

```bash
cat ~/.ssh/id_rsa.pub
```

**Copia TODA la salida** (empieza con `ssh-rsa` y termina con tu correo).

#### Agregar clave a GitHub:

1. Ve a: https://github.com/settings/keys
2. Click en **"New SSH key"**
3. Título: `Mi computadora` o `Docker Git`
4. Pega tu clave pública en el campo **Key**
5. Click en **"Add SSH key"**

#### Verificar que funcionó:

```bash
ssh -T git@github.com
```

Deberías ver algo como:
```
Hi jazaineam1! You've successfully authenticated...
```

### 5. Revisar estado del repositorio

```bash
git status
git branch --show-current
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

### Error: "Permission denied (publickey)" en push

Causa: SSH no está configurado o no está agregada en GitHub.

Solución:

```bash
# Crear clave SSH si no la tienes
ssh-keygen -t rsa -b 4096 -C "tu-correo@ejemplo.com"

# Ver tu clave pública
cat ~/.ssh/id_rsa.pub

# Agregar en https://github.com/settings/keys

# Verificar conexión
ssh -T git@github.com
```

### Error: "Key is invalid. You must supply a key in OpenSSH public key format"

Causa: copiaste solo parte de la clave o formato incorrecto.

Solución: copia TODA la salida de `cat ~/.ssh/id_rsa.pub` (desde `ssh-rsa` hasta el correo).

## 🧠 Resultado esperado del módulo

Al finalizar, el estudiante puede:

- ubicarse en el repositorio correcto
- usar terminal sin bloqueo inicial
- verificar su configuración de Git
- comenzar los ejercicios del curso con flujo ordenado
