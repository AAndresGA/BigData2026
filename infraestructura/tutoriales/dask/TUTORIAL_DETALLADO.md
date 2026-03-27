# Tutorial detallado de Dask

## Objetivo

Aprender a ejecutar tareas paralelas con Dask y comprender su uso en análisis de datos distribuidos.

## Requisitos

Desde la raíz del repositorio:

```bash
docker compose --profile dask up -d
docker compose ps
```

Debes ver:

- `dask-scheduler` activo
- `dask-worker` activo

## Paso 1: validar entorno

```bash
docker compose exec dask-scheduler dask --version
```

Abrir dashboard:

- `http://localhost:8787`

## Paso 2: ejecutar job de ejemplo

```bash
python dask/jobs/dask_demo.py
```

Si ejecutas desde contenedor, ajusta comando a tu imagen o usa notebook.

## Paso 3: observar ejecución en dashboard

Revisar en Dask:

- tasks
- workers
- memoria
- tiempos de ejecución

## Paso 4: ejercicio guiado

1. Cargar un CSV.
2. Hacer limpieza básica.
3. Crear agregación por categoría.
4. Exportar resultado a `data/lake/processed`.

## Entregable

- script Dask funcional
- archivo de salida
- breve explicación de por qué Dask fue útil en este caso
