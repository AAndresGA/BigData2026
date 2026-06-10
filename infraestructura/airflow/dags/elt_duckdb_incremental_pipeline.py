from datetime import datetime, timedelta
import glob
import logging
import os

from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from airflow.utils.email import send_email


BASE_PATH = "/opt/airflow"
DB_PATH = os.path.join(BASE_PATH, "data", "dw.duckdb")
STAGING_FOLDER = os.path.join(BASE_PATH, "data", "staging")
STAGING_PATH = os.path.join(STAGING_FOLDER, "*.csv")
GITHUB_BASE_URL = "https://raw.githubusercontent.com/jazaineam1/BigData2026/refs/heads/main/Airflow/staging"
GITHUB_CSV_URLS = [
    f"{GITHUB_BASE_URL}/finanzas_mes_{mes}.csv"
    for mes in range(1, 8)
]

default_args = {
    "owner": "data_engineer",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="elt_duckdb_incremental_pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["elt", "duckdb", "incremental"],
)
def elt_pipeline():
    @task(task_id="esperar_archivo_csv")
    def esperar_archivo_csv():
        import duckdb

        conn = duckdb.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_files (
                filename VARCHAR PRIMARY KEY,
                processed_at TIMESTAMP,
                records INTEGER
            )
            """
        )
        procesados = {
            row[0] for row in conn.execute("SELECT filename FROM processed_files").fetchall()
        }
        conn.close()

        archivos_locales = [
            archivo
            for archivo in glob.glob(STAGING_PATH)
            if os.path.basename(archivo) not in procesados
        ]
        urls_remotas = [
            url
            for url in GITHUB_CSV_URLS
            if os.path.basename(url) not in procesados
        ]

        if not archivos_locales and not urls_remotas:
            raise AirflowSkipException("No hay archivos CSV nuevos para procesar.")

        return {
            "locales": archivos_locales,
            "remotos": urls_remotas,
        }

    @task()
    def limpiar_staging(archivos_detectados):
        import duckdb

        conn = duckdb.connect(DB_PATH)
        conn.execute("DROP TABLE IF EXISTS staging_raw")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_files (
                filename VARCHAR PRIMARY KEY,
                processed_at TIMESTAMP,
                records INTEGER
            )
            """
        )
        logging.info("Tabla temporal staging_raw eliminada.")
        conn.close()
        return archivos_detectados

    @task()
    def cargar_staging(archivos_detectados):
        import duckdb

        conn = duckdb.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_files (
                filename VARCHAR PRIMARY KEY,
                processed_at TIMESTAMP,
                records INTEGER
            )
            """
        )
        procesados = {
            row[0] for row in conn.execute("SELECT filename FROM processed_files").fetchall()
        }
        archivos_locales = [
            archivo
            for archivo in archivos_detectados["locales"]
            if os.path.basename(archivo) not in procesados
        ]
        urls_remotas = [
            url
            for url in archivos_detectados["remotos"]
            if os.path.basename(url) not in procesados
        ]
        fuentes = archivos_locales + urls_remotas
        archivos_nuevos_nombres = [os.path.basename(fuente) for fuente in fuentes]

        if not fuentes:
            conn.close()
            return {
                "archivos_procesados": [],
                "total_registros_staging": 0,
            }

        csv_paths = ", ".join(f"'{fuente.replace(chr(92), '/')}'" for fuente in fuentes)
        conn.execute(
            f"""
            CREATE TABLE staging_raw AS
            SELECT * FROM read_csv_auto([{csv_paths}])
            """
        )

        total_staging = conn.execute("SELECT COUNT(*) FROM staging_raw").fetchone()[0]
        conn.close()

        return {
            "archivos_procesados": archivos_nuevos_nombres,
            "total_registros_staging": total_staging,
        }

    @task()
    def transformar_e_insertar(metadata_carga):
        import duckdb

        conn = duckdb.connect(DB_PATH)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fact_finanzas_elt (
                id INTEGER,
                salario DOUBLE,
                gastos DOUBLE,
                fecha DATE,
                correo_hash VARCHAR,
                utilidad DOUBLE,
                fecha_carga TIMESTAMP
            )
            """
        )
        columnas = {
            row[1]
            for row in conn.execute("PRAGMA table_info('fact_finanzas_elt')").fetchall()
        }
        if "fecha_carga" not in columnas:
            conn.execute("ALTER TABLE fact_finanzas_elt ADD COLUMN fecha_carga TIMESTAMP")

        if metadata_carga["total_registros_staging"] == 0:
            conn.close()
            return {
                "archivos": metadata_carga["archivos_procesados"],
                "registros_procesados": 0,
                "registros_insertados": 0,
                "registros_filtrados": 0,
            }

        registros_antes = conn.execute("SELECT COUNT(*) FROM fact_finanzas_elt").fetchone()[0]

        conn.execute(
            """
            INSERT INTO fact_finanzas_elt
            SELECT DISTINCT
                id,
                salario,
                COALESCE(gastos, 0) AS gastos,
                CASE
                    WHEN regexp_matches(fecha, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') THEN CAST(fecha AS DATE)
                    WHEN regexp_matches(fecha, '^[0-9]{2}/[0-9]{2}/[0-9]{4}$') THEN STRPTIME(fecha, '%d/%m/%Y')
                    WHEN regexp_matches(fecha, '^[0-9]{2}-[0-9]{2}-[0-9]{4}$') THEN STRPTIME(fecha, '%m-%d-%Y')
                    ELSE NULL
                END AS fecha,
                CASE
                    WHEN correo IS NOT NULL THEN sha256(correo)
                    ELSE NULL
                END AS correo_hash,
                salario - COALESCE(gastos, 0) AS utilidad,
                CURRENT_TIMESTAMP AS fecha_carga
            FROM staging_raw
            WHERE id IS NOT NULL
              AND id NOT IN (SELECT id FROM fact_finanzas_elt)
              AND fecha IS NOT NULL
              AND salario > 0
              AND COALESCE(gastos, 0) >= 0
            """
        )

        registros_despues = conn.execute("SELECT COUNT(*) FROM fact_finanzas_elt").fetchone()[0]
        registros_insertados = registros_despues - registros_antes
        for archivo in metadata_carga["archivos_procesados"]:
            conn.execute(
                "DELETE FROM processed_files WHERE filename = ?",
                [archivo],
            )
            conn.execute(
                """
                INSERT INTO processed_files
                VALUES (?, CURRENT_TIMESTAMP, ?)
                """,
                [archivo, registros_insertados],
            )
        conn.close()

        total_staging = metadata_carga["total_registros_staging"]

        return {
            "archivos": metadata_carga["archivos_procesados"],
            "registros_procesados": total_staging,
            "registros_insertados": registros_insertados,
            "registros_filtrados": total_staging - registros_insertados,
        }

    @task()
    def preparar_notificacion(metricas):
        info = f"""
        Resultado del Pipeline:
        - Archivos: {metricas["archivos"]}
        - Registros en staging: {metricas["registros_procesados"]}
        - Registros insertados: {metricas["registros_insertados"]}
        - Registros filtrados: {metricas["registros_filtrados"]}
        """
        logging.info(info)
        return info

    @task()
    def enviar_notificacion_exito(metricas):
        html_content = f"""
        <h3>El proceso ha terminado.</h3>
        <p>El DAG elt_duckdb_incremental_pipeline finalizo correctamente.</p>
        <p>Entrega enviada por: agonzaleza14@ucentral.edu.co</p>
        <ul>
            <li>Archivos procesados: {metricas["archivos"]}</li>
            <li>Registros procesados: {metricas["registros_procesados"]}</li>
            <li>Registros insertados: {metricas["registros_insertados"]}</li>
            <li>Registros filtrados: {metricas["registros_filtrados"]}</li>
        </ul>
        """
        try:
            send_email(
                to=["jzaineam@ucentral.edu.co"],
                cc=["agonzaleza14@ucentral.edu.co"],
                subject="Pipeline ELT finalizado con exito",
                html_content=html_content,
                custom_headers={"Reply-To": "agonzaleza14@ucentral.edu.co"},
            )
            return "Correo enviado correctamente."
        except Exception as exc:
            logging.warning("No se pudo enviar el correo por configuracion SMTP/permisos: %s", exc)
            return "Correo no enviado por configuracion SMTP/permisos. Pipeline finalizado correctamente."

    archivos_detectados = esperar_archivo_csv()
    staging_limpio = limpiar_staging(archivos_detectados)
    datos_carga = cargar_staging(staging_limpio)
    datos_metrica = transformar_e_insertar(datos_carga)

    datos_metrica >> preparar_notificacion(datos_metrica) >> enviar_notificacion_exito(datos_metrica)


elt_dag = elt_pipeline()
