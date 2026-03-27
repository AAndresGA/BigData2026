# ✅ Solución sugerida

## Flujo técnico

```bash
git switch -c feature/readme
git status
git add README.md
git commit -m "Actualiza contenido del README"
git push origin feature/readme
```

## Qué hacer en GitHub

1. Entrar al repositorio
2. Abrir el botón para crear Pull Request desde `feature/readme`
3. Verificar que el destino sea `main`
4. Completar título y descripción
5. Crear el PR

## Ejemplo de descripción del PR

```text
## Qué hice
Actualicé el README con una explicación más clara del módulo.

## Por qué
Era necesario mejorar la comprensión del contenido para los estudiantes.

## Cómo revisarlo
Leer el README y verificar que la nueva explicación sea coherente.
```

## Explicación

- la rama aísla el cambio del README
- el commit documenta el cambio realizado
- el Pull Request presenta el trabajo para revisión antes de integrarlo
