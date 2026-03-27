# Tutorial simple de inicio

Esta guía es corta. Sirve para arrancar rápido.

## 1) Preparar entorno

```bash
cp .env.example .env
docker compose --profile airflow --profile dask up -d
docker compose ps
```

## 2) Verificar herramientas principales

```bash
docker compose exec git git --version
docker compose exec airflow-webserver airflow version
docker compose exec dask-scheduler dask --version
```

## 3) Abrir interfaces

- Airflow: `http://localhost:8080`
- Dask Dashboard: `http://localhost:8787`

## 4) Elegir tutorial detallado

- Git: `tutoriales/git/TUTORIAL_DETALLADO.md`
- Dask: `tutoriales/dask/TUTORIAL_DETALLADO.md`
- Spark: `tutoriales/spark/TUTORIAL_DETALLADO.md`

## 5) Cerrar entorno al terminar

```bash
docker compose down
```
