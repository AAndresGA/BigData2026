# Entrega Reto 2 - Airflow ELT con DuckDB

## DAG recuperado

Archivo:

```text
airflow/dags/elt_duckdb_incremental_pipeline.py
```

DAG:

```text
elt_duckdb_incremental_pipeline
```

## Flujo

```text
esperar_archivo_csv
  -> limpiar_staging
  -> cargar_staging
  -> transformar_e_insertar
  -> preparar_notificacion
  -> enviar_notificacion_exito
```

## Fuente de datos

El pipeline lee los CSV del material del profesor:

```text
https://raw.githubusercontent.com/jazaineam1/BigData2026/refs/heads/main/Airflow/staging/finanzas_mes_1.csv
...
https://raw.githubusercontent.com/jazaineam1/BigData2026/refs/heads/main/Airflow/staging/finanzas_mes_7.csv
```

## Cumplimiento del reto

- Conserva la tabla historica `fact_finanzas_elt`.
- Inserta solo registros nuevos por `id`.
- Controla archivos ya procesados en `processed_files`.
- Reporta archivos procesados, registros procesados, registros insertados y registros filtrados.
- Incluye tarea opcional de correo al final.

## Notificacion por correo

Remitente configurado:

```text
agonzaleza14@ucentral.edu.co
```

Destinatario configurado:

```text
jzaineam@ucentral.edu.co
```

Nota: la tarea `enviar_notificacion_exito` intenta enviar el correo. Si Airflow no tiene SMTP configurado o si la cuenta no tiene permisos de envio desde el entorno, registra la situacion en logs y no detiene el pipeline.

## Ejecucion

Desde la carpeta del proyecto:

```bash
docker compose --profile airflow up -d
docker compose exec airflow-webserver airflow dags list
```

Abrir Airflow:

```text
http://localhost:8080
```

Credenciales usadas en el entorno local:

```text
admin / admin
```

Ejecutar manualmente el DAG desde la interfaz de Airflow y tomar captura del Graph/Grid con las primeras cinco tareas exitosas.
