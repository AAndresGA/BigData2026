# 📦 Módulo 2: Commits profesionales

## 🎯 Objetivo

Aprender a escribir commits claros, útiles y alineados con prácticas reales de trabajo.

## 🌍 Contexto

En equipos profesionales, el historial de Git no es decoración. Se usa para:

- entender qué cambió
- encontrar cuándo apareció un error
- revisar decisiones pasadas
- preparar releases
- auditar trabajo

Un mal commit complica todo eso. Un buen commit vuelve el historial legible y confiable.

## 🧠 Qué debe comunicar un commit

Un commit responde, de forma breve, esta pregunta:

"¿Qué cambio se hizo?"

En algunos casos, también deja entrever el propósito.

Ejemplos buenos:

- `Agrega validación de login`
- `Corrige error en cálculo de impuestos`
- `Actualiza estilos del formulario de registro`

Ejemplos malos:

- `fix`
- `cambios`
- `prueba`
- `asdf`

## ✍️ Reglas prácticas para escribir mejores commits

- Usa mensajes concretos
- Describe el cambio principal
- Evita mensajes vagos
- Piensa en alguien que leerá esto semanas después

## 🧩 Qué no hacer

Un error común es meter demasiadas cosas distintas en un solo commit. Si arreglas estilos, cambias texto y además refactorizas lógica, el commit se vuelve difícil de revisar y revertir.

La recomendación es hacer commits pequeños y temáticos.

## ✅ Ejemplo comparativo

### Malo

```text
fix
```

No explica nada.

### Mejor

```text
Corrige validación de email en formulario de registro
```

Ahora sí queda claro qué se hizo.

## 🧑‍💻 Relación entre commits y PR

Un Pull Request bueno suele empezar con commits buenos. Si los commits son claros, el PR se entiende mejor y la revisión es más rápida.
