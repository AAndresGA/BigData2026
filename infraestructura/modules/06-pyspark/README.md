# Modulo 06: PySpark para procesamiento distribuido

## Objetivo

Ejecutar transformaciones de datos con Spark y entender su ventaja frente a procesamiento local.

## Conceptos clave

- DataFrame distribuido
- transformaciones vs acciones
- particionado y rendimiento

## Practica guiada

1. Levantar perfil `spark`:

```bash
docker compose --profile spark up -d
```

2. Leer un CSV desde `data/`.
3. Aplicar filtro, seleccion de columnas y agregacion.
4. Guardar salida procesada.

## Entregable

- script PySpark en `spark/jobs/`
- salida generada y validada
- explicacion corta de transformaciones utilizadas
