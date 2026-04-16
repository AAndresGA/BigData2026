# ✅ Solución sugerida

## Verificación de configuración

```bash
git config --global --get user.name
git config --global --get user.email
git status
git branch --show-current
```

Si falta nombre o correo, configurar:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

## Flujo de entrega del ejercicio

```bash
git switch -c feature/onboarding
git add .
git commit -m "Valida entorno inicial del curso"
git push origin feature/onboarding
```

## Explicación

- `git config --get` confirma la identidad configurada
- `git status` y `git branch --show-current` validan contexto del repositorio
- la rama `feature/onboarding` asegura que no se trabaje directo sobre `main`
- el commit deja trazabilidad del alistamiento técnico del estudiante
