# 🌿 Módulo 3: Ramas

## 🎯 Objetivo

Aprender a trabajar sin afectar la rama principal del proyecto.

## 🌍 Contexto

En proyectos reales, `main` representa la versión estable del trabajo. En muchos equipos, esa rama está asociada al código que eventualmente llega a producción.

Por eso no se recomienda trabajar directamente allí. En cambio, cada tarea se desarrolla en una rama propia.

## 🌳 La metáfora del árbol

Imagina que `main` es el tronco. Cada nueva funcionalidad o cambio sale como una rama lateral.

Eso permite:

- trabajar con seguridad
- probar ideas sin arriesgar la base estable
- aislar cambios por tarea
- revisar mejor el trabajo antes de integrarlo

## 🔧 Comando clave

```bash
git switch -c feature/nombre
```

### Qué hace exactamente

- `switch`: cambia de rama
- `-c`: crea la rama si no existe

Ejemplo:

```bash
git switch -c feature/perfil
```

## 🏷 Convenciones útiles para nombres de ramas

No existe una única regla universal, pero estas convenciones ayudan:

- `feature/perfil`
- `feature/login`
- `fix/error-formulario`
- `docs/actualiza-readme`

El objetivo es que el nombre permita entender la intención del trabajo.

## 🧠 Idea clave

Trabajar en una rama no significa duplicar todo el proyecto manualmente. Git administra esa separación internamente y luego puede integrar los cambios cuando estén listos.

## 🚫 Error común

Crear la rama, pero olvidar en cuál estás trabajando. Por eso conviene revisar con frecuencia el estado del repositorio y confirmar que no estás en `main`.
