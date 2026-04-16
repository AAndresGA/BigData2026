# 📘 Cuaderno de Estudio Completo: Dominando Git y GitHub desde Cero

Bienvenido al curso. Este repositorio ya no funciona solo como una lista de tareas: ahora es un material de estudio pensado para explicar el porqué de cada comando y el flujo real de trabajo que se usa en equipos profesionales.

Si alguna vez has guardado archivos con nombres como `proyecto-final.docx`, `proyecto-final-ahora-si.docx` o `proyecto-final-definitivo-v3.docx`, ya conoces el problema que Git resuelve. Git organiza la historia de tu proyecto, te permite trabajar con seguridad y facilita la colaboración sin caos.

## 🎯 Objetivo general

Dominar Git y GitHub usando un flujo profesional de trabajo:

- Crear ramas para trabajar sin romper `main`
- Hacer commits claros y útiles
- Publicar cambios en GitHub
- Entregar trabajo mediante Pull Requests
- Colaborar, revisar cambios y corregir observaciones
- Entender y resolver conflictos de integración

## 🧠 Qué aprenderás realmente

Este curso no se limita a memorizar comandos. La meta es que entiendas cómo trabajan juntos estos conceptos:

- `Git`: el sistema de control de versiones que vive en tu entorno de trabajo
- `GitHub`: la plataforma en la nube donde compartes y revisas repositorios
- `Codespaces`: el entorno listo para usar desde el navegador
- `Branches`: espacios seguros para desarrollar sin tocar la rama principal
- `Commits`: puntos de control en la historia del proyecto
- `Pull Requests`: el mecanismo profesional para proponer cambios

## 🔍 Git vs GitHub vs Codespaces

### Git

Git es un programa que corre en la terminal. Sirve para registrar cambios en archivos, consultar historial, comparar versiones y coordinar trabajo entre varias personas.

Puedes pensar en Git como una mezcla de:

- máquina del tiempo, porque te deja volver a versiones anteriores
- auditor, porque muestra qué cambió y quién lo hizo
- sistema de ramas, porque permite experimentar sin arriesgar el trabajo estable

### GitHub

GitHub es la plataforma web donde alojas repositorios Git. Allí puedes:

- guardar tu proyecto en la nube
- colaborar con otras personas
- abrir Pull Requests
- revisar código
- mostrar tu portafolio profesional

GitHub no reemplaza a Git. Git hace el control de versiones; GitHub facilita compartirlo y revisarlo.

### GitHub Codespaces

Codespaces es un entorno de desarrollo en la nube. En lugar de configurar todo en tu computador desde cero, abres un editor parecido a VS Code directamente en el navegador.

Esto reduce errores de instalación y permite que todo el grupo trabaje en un entorno similar.

## ⚙️ Reglas del curso

- No trabajar directamente en `main`
- Siempre usar ramas descriptivas
- Hacer commits claros
- Entregar cambios mediante Pull Request
- Mantener cambios pequeños y fáciles de revisar
- Leer los mensajes de error antes de pedir ayuda

## 🔁 Flujo profesional base

Este será el patrón repetido a lo largo del curso:

1. Crear una rama

```bash
git switch -c feature/xxx
```

2. Hacer cambios en archivos
3. Revisar el estado del repositorio

```bash
git status
```

4. Agregar cambios al área de preparación

```bash
git add .
```

5. Crear un commit con mensaje claro

```bash
git commit -m "Agrega descripcion del cambio"
```

6. Enviar la rama a GitHub

```bash
git push origin feature/xxx
```

7. Crear Pull Request en GitHub

## 🧭 Ruta del curso

### Módulo 0. Onboarding

Aprenderás cómo entrar al repositorio de la clase, abrir Codespaces y configurar Git para evitar los errores más comunes del primer día.

### Módulo 1. Fundamentos

Aprenderás qué es Git, qué problema resuelve y cómo guardar cambios correctamente.

### Módulo 2. Commits

Aprenderás a escribir mensajes de commit claros, profesionales y útiles para el historial.

### Módulo 3. Ramas

Aprenderás a trabajar sin afectar la rama principal y a usar el flujo estándar de desarrollo.

### Módulo 4. Pull Requests

Aprenderás a entregar cambios como se hace en equipos reales y a documentar bien un PR.

### Módulo 5. Colaboración

Practicarás revisión de código, comentarios en PR, trabajo con `fork`, sincronización y mejoras iterativas.

### Módulo 6. Conflictos

Entenderás por qué ocurren los conflictos y cómo resolverlos sin pánico.

### Proyecto final

Aplicarás el flujo completo: rama, cambios, commits, push, PR y revisión.

## 🗂 Mapa de contenidos

- `modulo-0-onboarding/README.md` Introducción operativa para arrancar el curso
- `modulo-1-basico/README.md` Fundamentos de Git
- `modulo-2-commits/README.md` Commits profesionales
- `modulo-3-ramas/README.md` Trabajo por ramas
- `modulo-4-pr/README.md` Pull Requests
- `modulo-5-colaboracion/README.md` Colaboración entre forks
- `modulo-6-conflictos/README.md` Resolución de conflictos
- `proyecto-final/README.md` Cierre integrador del curso

## 🧪 Navegación por módulo

Cada módulo usa el mismo patrón:

- `README.md` explicación teórica y contexto
- `ejercicio.md` actividad guiada
- `solucion.md` propuesta de resolución

## 📦 Entregas y evaluación

Todas las entregas del curso deben hacerse mediante Pull Request.

Se evaluará:

- uso correcto de Git
- claridad de commits
- uso de ramas
- calidad del Pull Request
- comprensión del flujo con `fork`
- capacidad de iterar después de una revisión
- orden y criterio al resolver conflictos

## ✅ Checklist antes de entregar

Antes de pedir revisión, verifica esto:

- Estoy en la rama correcta y no en `main`
- Entiendo qué archivos cambié
- Mi commit explica qué hice
- Hice `push` de mi rama
- Abrí el Pull Request
- La descripción del PR no está vacía
- Si hubo comentarios, los atendí con nuevos commits

## 🧑‍🏫 Cultura del curso

Aprender Git implica equivocarse. Los errores no son señal de fracaso; son parte del proceso. Lo importante es desarrollar criterio:

- leer la salida de la terminal
- entender qué estado tiene el repositorio
- hacer cambios pequeños
- pedir ayuda con evidencia clara cuando sea necesario

Si Git muestra un error en rojo, no asumas que todo se dañó. Normalmente Git está diciendo exactamente qué problema encontró y, muchas veces, también sugiere cómo corregirlo.

## 📚 Bibliografía adicional

Para profundizar después del curso, estas son referencias recomendadas:

- Chacon, Scott, y Ben Straub. *Pro Git*. Apress. Libro de referencia muy completo sobre Git, disponible gratuitamente en línea: https://git-scm.com/book/es/v2
- Sitio oficial de Git. Documentación, descargas y libro oficial: https://git-scm.com/
- Documentación de referencia de Git. Útil para consultar comandos específicos: https://git-scm.com/docs
- Documentación oficial de GitHub. Guías prácticas sobre repositorios, ramas, Pull Requests y colaboración: https://docs.github.com/es
- GitHub Skills. Ejercicios guiados para practicar GitHub con repositorios interactivos: https://skills.github.com/
- Documentación de GitHub Codespaces. Referencia para entornos de desarrollo en la nube: https://docs.github.com/es/codespaces
- Atlassian Git Tutorials. Material complementario con explicaciones visuales sobre ramas, merge y flujos de trabajo: https://www.atlassian.com/git/tutorials
- Software Carpentry, *Version Control with Git*. Recurso didáctico muy útil para enseñanza y aprendizaje paso a paso: https://swcarpentry.github.io/git-novice/
