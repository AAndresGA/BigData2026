# Proyecto final: pipeline Big Data de extremo a extremo

## Objetivo

Construir una solucion integrada que conecte ingestion, procesamiento, almacenamiento y orquestacion.

## Escenario

Trabajaras con un dataset CSV y deberas producir una salida analitica reproducible.

## Flujo esperado

1. Ingestar CSV en `data/lake/raw`.
2. Procesar con Spark o Dask.
3. Guardar resultados en MongoDB.
4. Orquestar el flujo en Airflow (`airflow/dags/` o `projects/final-project/dags/`).
5. Analizar resultado en Jupyter (`notebooks/`).

## Requisitos tecnicos

Levantar stack final:

```bash
docker compose --profile final up -d
```

## Entregables obligatorios

- DAG funcional
- script Spark o Dask funcional
- coleccion Mongo con resultados del proceso
- notebook de analisis con conclusiones
- README corto del equipo explicando arquitectura y decisiones

## Criterios de evaluacion

- correccion tecnica del pipeline
- trazabilidad (datos de entrada -> salida)
- claridad de documentacion
- capacidad de reproduccion del resultado
- buenas practicas de versionado y colaboracion
