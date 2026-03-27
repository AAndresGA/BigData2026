# Docker setup (resumen rapido)

Este archivo es un atajo. La referencia completa esta en `INSTALACION_DESDE_CERO.md`.

## Verificar Docker

```bash
docker --version
docker compose version
```

## Levantar modulo Airflow + Dask

```bash
docker compose --profile airflow --profile dask up -d
```

## Levantar modulo Spark

```bash
docker compose --profile spark up -d
```

## Levantar modulo NoSQL

```bash
docker compose --profile nosql up -d
```

## Detener todo

```bash
docker compose down
```
