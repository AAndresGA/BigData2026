# Tutorial detallado de Spark

## Objetivo

Aprender el flujo básico de procesamiento distribuido con Spark usando jobs simples y resultados verificables.

## Requisitos

Desde la raíz del repositorio:

```bash
docker compose --profile spark up -d
docker compose ps
```

Debes ver:

- `spark-master` activo
- `spark-worker` activo

UI de Spark:

- `http://localhost:8081`

## Paso 1: preparar datos

Ubicar dataset en:

- `data/lake/raw/`

## Paso 2: ejecutar job de ejemplo

Script sugerido:

- `spark/jobs/wordcount.py`

Ejecútalo según tu flujo de clase (contenedor o entorno local con Spark disponible).

## Paso 3: transformación mínima

En un job propio aplica:

1. lectura de CSV
2. selección de columnas
3. filtro por condición
4. agregación simple
5. escritura en `data/lake/processed`

## Paso 4: validar salida

Verifica:

- archivo generado
- columnas esperadas
- registros consistentes

## Entregable

- script Spark funcional
- salida procesada
- breve nota técnica: transformaciones aplicadas y resultado obtenido
