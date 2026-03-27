# Docker del proyecto Big Data

Este directorio contiene Dockerfiles de imagenes personalizadas:

- `docker/airflow/Dockerfile`
- `docker/jupyter/Dockerfile`

El archivo principal para levantar servicios es:

- `../docker-compose.yml`

## Como usar por modulo (perfil)

Desde la raiz del repositorio:

```bash
docker compose --profile airflow up -d
docker compose --profile dask up -d
docker compose --profile spark up -d
docker compose --profile nosql up -d
docker compose --profile search up -d
docker compose --profile notebooks --profile spark --profile dask --profile nosql up -d
docker compose --profile final up -d
```

## Buenas practicas para equipos con 8 GB RAM

- no levantar todos los perfiles al mismo tiempo
- apagar perfiles que no uses (`docker compose down`)
- evitar `search` (Elasticsearch/Kibana) cuando no sea necesario

## Comando de verificacion

```bash
docker compose ps
```

## Referencia principal

Para instalacion paso a paso desde cero usa:

- `../INSTALACION_DESDE_CERO.md`
