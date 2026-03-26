# 🧪 Ejercicio 1: Primer commit

## Contexto

Vas a crear tu primer archivo dentro del repositorio y registrar ese cambio en la historia del proyecto.

## Tarea

1. Crear archivo `hola.txt`
2. Escribir dentro: `Hola Git`
3. Revisar el estado del repositorio con `git status`
4. Agregar el archivo al staging area
5. Crear el commit con un mensaje claro

## Comandos esperados

```bash
git status
git add .
git commit -m "Agrega primer archivo de saludo"
```

## Qué debes observar

- Antes de `git add`, Git mostrará el archivo como no preparado
- Después de `git add`, Git lo mostrará como listo para commit
- Después del commit, el repositorio quedará limpio si no hiciste más cambios

## Preguntas de reflexión

- ¿Qué diferencia viste entre un archivo modificado y un archivo staged?
- ¿Por qué no basta con solo crear el archivo?
