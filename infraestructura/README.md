# Big Data Course: guía completa para principiantes

Este repositorio está organizado para personas que están empezando en Big Data y necesitan una ruta clara, práctica y ejecutable paso a paso.

## Objetivo del curso

Aprender un flujo real de ingeniería de datos usando:

- almacenamiento y procesamiento de datos
- NoSQL y búsqueda
- Spark y Dask
- orquestación con Airflow
- análisis en notebooks
- colaboración profesional con Git

## Enfoque pedagógico

Se trabaja con progresión por módulos:

1. conceptos base
2. práctica guiada
3. entregable concreto

La meta no es memorizar herramientas, sino entender cuándo usar cada una y cómo integrarlas.

## Estructura principal del repositorio

- `modules/`: contenido de Big Data por tema (01 a 07)
- `projects/final-project/`: proyecto integrador final
- `airflow/dags/`: pipelines orquestados
- `spark/jobs/`: jobs de Spark
- `dask/jobs/`: jobs de Dask
- `notebooks/`: análisis exploratorio
- `data/`: datasets de práctica
- `setup/`: notas rápidas de instalación
- `docker-compose.yml`: stack principal con servicios por módulo (`profiles`)
- `INSTALACION_DESDE_CERO.md`: instalación detallada desde cero
- `TUTORIAL_PASO_A_PASO.md`: guía simple de arranque
- `tutoriales/git/`: curso completo de Git y colaboración
- `tutoriales/dask/TUTORIAL_DETALLADO.md`: tutorial detallado de Dask
- `tutoriales/spark/TUTORIAL_DETALLADO.md`: tutorial detallado de Spark

Tutoriales detallados por tecnología:

- `tutoriales/git/TUTORIAL_DETALLADO.md`
- `tutoriales/dask/TUTORIAL_DETALLADO.md`
- `tutoriales/spark/TUTORIAL_DETALLADO.md`

## Arranque rápido (primera clase)

1. Instala Docker siguiendo `INSTALACION_DESDE_CERO.md`.
2. Copia variables:

```bash
cp .env.example .env
```

3. Levanta entorno mínimo para empezar:

```bash
docker compose --profile airflow --profile dask up -d
```

4. Verifica:

```bash
docker compose ps
docker compose exec git git --version
docker compose exec airflow-webserver airflow version
docker compose exec dask-scheduler dask --version
```

## Ejecución por módulo (recomendado para 8 GB RAM)

En equipos con 8 GB no conviene levantar todo al mismo tiempo. Usa solo lo necesario.

### Airflow

```bash
docker compose --profile airflow up -d
```

### Dask

```bash
docker compose --profile dask up -d
```

### Spark

```bash
docker compose --profile spark up -d
```

### NoSQL (Mongo)

```bash
docker compose --profile nosql up -d
```

### Search (Elasticsearch + Kibana)

```bash
docker compose --profile search up -d
```

### Notebooks (Jupyter + dependencias)

```bash
docker compose --profile notebooks --profile spark --profile dask --profile nosql up -d
```

### Proyecto final (stack integrado)

```bash
docker compose --profile final up -d
```

## Buenas prácticas del curso

- levantar solo servicios del módulo activo
- documentar cada avance técnico
- hacer commits pequeños y descriptivos
- evitar trabajar directo en `main`
- validar datos y resultados antes de entregar

## Qué revisar si algo falla

- `INSTALACION_DESDE_CERO.md`
- `setup/windows.md`
- `setup/docker.md`
- logs de servicio:

```bash
docker compose logs -f <servicio>
```

## Siguiente paso recomendado

Si estás iniciando desde cero, empieza por:

1. `INSTALACION_DESDE_CERO.md`
2. `modules/01-storage/README.md`
3. `modules/02-processing/README.md`
4. `TUTORIAL_PASO_A_PASO.md`
5. `tutoriales/git/TUTORIAL_DETALLADO.md`
