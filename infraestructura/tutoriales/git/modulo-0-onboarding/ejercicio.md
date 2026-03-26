# 🧪 Ejercicio 0: Validar entorno de trabajo

## Objetivo

Comprobar que tu entorno está listo para iniciar el curso sin errores de configuración.

## Pasos

1. Levantar servicios Docker:

```bash
cd docker
docker compose up -d
docker compose ps
```

2. Verificar nombre en Git:

```bash
git config --global --get user.name
```

3. Verificar correo en Git:

```bash
git config --global --get user.email
```

4. Revisar estado del repositorio:

```bash
git status
```

5. Confirmar rama actual:

```bash
git branch --show-current
```

6. Validar herramientas en contenedores:

```bash
docker compose exec git git --version
docker compose exec airflow airflow version
docker compose exec dask-scheduler dask --version
```

7. Crear archivo `entorno-listo.txt` con tu nombre y fecha.
8. Crear una rama para este ejercicio:

```bash
git switch -c feature/onboarding
```

9. Hacer commit y push:

```bash
git add .
git commit -m "Valida entorno inicial del curso"
git push origin feature/onboarding
```

## Qué se evalúa

- entorno Docker levantado
- entorno configurado correctamente
- uso de rama de trabajo
- commit claro
- push exitoso
