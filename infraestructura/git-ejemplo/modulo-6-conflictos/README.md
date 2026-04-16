# ⚔️ Módulo 6: Conflictos de Git

## 🎯 Objetivo

Entender por qué ocurren los conflictos y cómo resolverlos con calma y criterio.

## 🌍 Contexto

Los conflictos son una parte normal del trabajo colaborativo. No significan que Git falló por completo ni que el proyecto se rompió. Significan que Git encontró dos cambios incompatibles en el mismo lugar y necesita ayuda humana para decidir.

## 🧠 ¿Por qué ocurre un conflicto?

Git puede combinar muchos cambios automáticamente, pero se detiene cuando dos personas modifican la misma línea o una misma sección de un archivo y no puede inferir cuál versión debe quedar.

## 👀 Cómo se ve un conflicto

Git inserta marcas dentro del archivo:

```text
<<<<<<< HEAD
Hola, me llamo Carlos y soy de Colombia.
=======
Hola, me llamo Maria y soy de México.
>>>>>>> rama-de-maria
```

Estas marcas no son el resultado final. Son una señal para que revises y elijas qué contenido debe quedar.

## ✅ Proceso para resolverlo

1. Identificar el archivo en conflicto
2. Abrirlo y leer ambas versiones
3. Decidir si conservar una, la otra o una combinación
4. Eliminar las marcas `<<<<<<<`, `=======` y `>>>>>>>`
5. Guardar el archivo corregido
6. Marcarlo como resuelto con `git add`
7. Crear un commit de resolución

## Ejemplo de cierre

```bash
git add presentacion.txt
git commit -m "Resuelve conflicto en presentacion"
```

## 🧑‍🏫 Idea importante

Resolver conflictos no es solo una tarea técnica. También es una decisión de contenido. Debes entender qué quería lograr cada cambio antes de combinarlo.
