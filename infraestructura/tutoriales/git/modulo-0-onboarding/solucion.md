# ✅ Solución sugerida

## Verificación de configuración

```bash
cd docker
docker compose up -d
docker compose ps
git config --global --get user.name
git config --global --get user.email
git status
git branch --show-current
docker compose exec git git --version
docker compose exec airflow airflow version
docker compose exec dask-scheduler dask --version
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

- `docker compose up -d` levanta el entorno obligatorio del curso
- `git config --get` confirma la identidad configurada
- `git status` y `git branch --show-current` validan contexto del repositorio
- la rama `feature/onboarding` asegura que no se trabaje directo sobre `main`
- el commit deja trazabilidad del alistamiento técnico del estudiante
