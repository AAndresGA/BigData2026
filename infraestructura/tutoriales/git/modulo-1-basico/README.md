# 📦 Módulo 1: Fundamentos

## 🎯 Objetivo

Entender qué es Git, por qué existe y cómo registrar cambios de forma consciente.

## 🌍 Contexto

Antes de Git, muchas personas trabajaban duplicando carpetas o renombrando archivos una y otra vez. Eso generaba problemas:

- no era claro cuál era la versión correcta
- era fácil sobrescribir trabajo importante
- no había una historia ordenada de cambios
- colaborar con otras personas era confuso

Git aparece para resolver exactamente eso. En lugar de guardar versiones manuales, Git convierte tu proyecto en un repositorio con memoria.

## 🧠 Conceptos clave

### Repositorio

Es la carpeta del proyecto controlada por Git. Ahí se guarda no solo el contenido actual de los archivos, sino también el historial de cambios.

### Commit

Un commit es un punto de control. No es solo "guardar"; es registrar una versión con contexto. Permite saber qué cambió y por qué.

### Historial

Es la línea de tiempo del proyecto. Cuando haces commits claros, el historial se vuelve una herramienta de trabajo, no solo un registro técnico.

## 🛒 La analogía del supermercado

Para entender Git, imagina este flujo:

- `git status`: miras qué productos están en el estante
- `git add`: pones productos en el carrito
- `git commit`: pasas por caja y guardas un recibo permanente

Eso significa que modificar un archivo no crea automáticamente un commit. Git separa el proceso en etapas para darte control.

## 🔧 Comandos esenciales

### `git status`

Te dice en qué estado está tu repositorio:

- qué archivos cambiaste
- cuáles todavía no has agregado
- cuáles están listos para commit

Es uno de los comandos más importantes del curso. Úsalo antes y después de hacer cambios.

### `git add`

Mueve cambios al área de preparación, también llamada staging area. Es una forma de decirle a Git: "esto sí quiero incluirlo en el próximo commit".

Ejemplos:

```bash
git add hola.txt
git add .
```

`git add .` agrega todos los cambios detectados en la carpeta actual.

### `git commit -m`

Crea un registro permanente en la historia del proyecto.

Ejemplo:

```bash
git commit -m "Agrega archivo de saludo inicial"
```

## ✅ Buenas prácticas desde el inicio

- Haz cambios pequeños
- Revisa `git status` con frecuencia
- No hagas commits gigantes si puedes evitarlos
- Escribe mensajes que ayuden a otra persona a entender el cambio

## ⚠️ Error común del principiante

Pensar que editar un archivo ya significa "guardarlo en Git". No. Hasta que no haces `git add` y `git commit`, Git no registra ese cambio como una versión formal.
