# Modulo 07: Dask para paralelismo en Python

## Objetivo

Usar Dask para paralelizar tareas y trabajar con datasets mayores a la capacidad comoda de pandas local.

## Conceptos clave

- scheduler y workers
- ejecucion diferida (lazy)
- paralelismo por particiones

## Practica guiada

1. Levantar perfil `dask`:

```bash
docker compose --profile dask up -d
```

2. Ejecutar job de ejemplo en `dask/jobs/`.
3. Revisar dashboard de Dask (`http://localhost:8787`).

## Entregable

- script Dask funcional
- evidencia de ejecucion (salida o captura de dashboard)
- comparacion breve: cuando usar Dask vs Spark
