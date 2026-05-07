# -*- coding: utf-8 -*-
"""
Genera Cuadernos/9_Databricks_Serverless_Completo.ipynb

Sesion 9: primera introduccion guiada a Databricks Community Edition.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, section_header


TOTAL_Q = 14


def pregunta(num, tema, contexto, pregunta_texto, opciones, correcta, explicacion):
    opciones_html = "\n".join(
        f'<label style="display:block; margin:8px 0;"><input type="radio" name="q{num}" value="{chr(65+i)}"> {chr(65+i)}. {op}</label>'
        for i, op in enumerate(opciones)
    )
    return code(f"""
# Pregunta interactiva {num} de {TOTAL_Q}
# Estilo IRdisplay adaptado a Databricks/Python: caja HTML con displayHTML.
html = '''
<div style="border:2px solid #2563eb; background:#eff6ff; border-radius:8px; padding:16px; margin:12px 0; font-family:Arial, sans-serif;">
  <h3 style="margin:0 0 10px 0; color:#1d4ed8;">Pregunta {num} de {TOTAL_Q} -- {tema}</h3>
  <div style="background:#fef3c7; border-left:5px solid #f59e0b; padding:10px; margin:10px 0;">
    <strong>Contexto.</strong> {contexto}
  </div>
  <p><strong>{pregunta_texto}</strong></p>
  {opciones_html}
  <button onclick="
    var marcado = document.querySelector('input[name=q{num}]:checked');
    var out = document.getElementById('fb_q{num}');
    if (!marcado) {{
      out.innerHTML = 'Selecciona una opcion antes de verificar.';
      out.style.background = '#fef3c7';
      out.style.color = '#92400e';
      return;
    }}
    if (marcado.value === '{correcta}') {{
      out.innerHTML = 'Correcto. {explicacion}';
      out.style.background = '#dcfce7';
      out.style.color = '#166534';
    }} else {{
      out.innerHTML = 'Incorrecto. {explicacion}';
      out.style.background = '#fee2e2';
      out.style.color = '#991b1b';
    }}
  " style="background:#2563eb; color:white; border:0; border-radius:6px; padding:8px 12px; cursor:pointer;">
    Verificar respuesta
  </button>
  <div id="fb_q{num}" style="margin-top:10px; padding:10px; border-radius:6px;"></div>
</div>
'''

try:
    displayHTML(html)
except NameError:
    from IPython.display import HTML, display
    display(HTML(html))
    """, warn_on_triple_quotes=False)


def interp(titulo, puntos):
    return md(
        "### Como interpretar el resultado -- " + titulo + "\n\n" +
        "\n".join(f"- {p}" for p in puntos)
    )


def _proposito():
    return md("""
## Proposito pedagogico

Esta sesion es una **primera introduccion guiada a Databricks Community Edition** despues
de haber estudiado Hadoop, YARN y Spark en la sesion anterior. La meta no es
memorizar comandos aislados: la meta es entender donde viven los datos, como se
ejecuta Spark dentro de Databricks y como se construye un flujo reproducible.

## Alcance de la sesion

Trabajaremos con Databricks Community Edition, clusters clasicos, `dbutils`,
Spark SQL, PySpark DataFrames, Parquet y Delta Lake. Tambien veremos, como
panorama, conceptos modernos de Databricks como Unity Catalog, Volumes,
Lakeflow y Workflows, aclarando cuando no esten disponibles en Community Edition.

## Agenda sugerida

1. Entender la interfaz de Databricks Community Edition y el cluster clasico.
2. Aprender comandos magicos, `dbutils`, DBFS y la idea moderna de Volumes.
3. Leer, transformar y escribir datos con CSV, JSON, Parquet y Delta.
4. Comprender Spark: schemas, SQL, funciones, lazy evaluation y planes.
5. Comparar Spark con Pandas y Dask.
6. Introducir Delta Lake, Lakeflow y Workflows.
7. Cerrar con un taller aplicado.

## Por que importa

Databricks permite pasar de un notebook exploratorio a una plataforma de datos:
tablas gobernadas, permisos, lineage, ejecuciones programadas, optimizacion y
pipelines. Ese cambio es central en Big Data moderno.
    """)


def _toc():
    return md("""
## Contenido

- 0. Databricks Community Edition y panorama moderno 2025-2026
- 1. Magic commands y dbutils
- 2. SparkSession, SparkContext y Spark Connect como panorama
- 3. Catalogos, tablas, DBFS y Volumes
- 4. Spark SQL completo: TempViews, DDL y DML
- 5. Tipos de datos y schemas
- 6. Lectura y escritura: CSV, JSON, Parquet y Delta
- 7. Lazy evaluation, Catalyst, Jobs, Stages y repartition
- 8. Photon y Liquid Clustering
- 9. Funciones de cadenas, fechas y colecciones
- 10. Transformaciones completas de la API PySpark
- 11. Por que Spark sobre Pandas, y cuando no
- 12. Por que Spark sobre Dask, y cuando no
- 13. Delta Lake avanzado
- 14. Lakeflow / Delta Live Tables
- 15. Databricks Workflows y Jobs
- 16. Taller end-to-end
    """)


def _correspondencia():
    return md("""
## Correspondencia con la sesion anterior

| Sesion 7 | En esta sesion |
|---|---|
| Hadoop y YARN explican la administracion de recursos | Community Edition usa un cluster administrado sencillo para practicar |
| Spark como motor distribuido | Spark se usa con SQL, DataFrames y PySpark |
| Clusters y ejecucion distribuida | SparkSession, SparkContext, Jobs, Stages y Tasks |
| Archivos y almacenamiento | DBFS en CE; Unity Catalog y Volumes como panorama moderno |

Conservamos la intuicion distribuida de la sesion 7, pero la llevamos al flujo
actual de Databricks.
    """)


def _seccion_0():
    return [
        section_header("0", "Databricks Community Edition y panorama moderno 2025-2026"),
        md("""
## Definicion formal

**Databricks Community Edition** es una version gratuita y limitada de Databricks
para aprender notebooks, clusters clasicos, Spark SQL, PySpark y tablas Delta.
No incluye todas las capacidades empresariales modernas, pero es suficiente para
una primera clase muy completa.

## Intuicion

En Community Edition el estudiante crea o conecta un cluster clasico. Ese flujo
es perfecto para aprender que existe un driver, un SparkContext, jobs y stages.
Luego, como panorama, compararemos con el modelo moderno serverless que se usa
en workspaces pagos.

| Aspecto | Community Edition / Classic cluster | Serverless moderno |
|---|---|---|
| Arranque | Minutos | Segundos o muy poco tiempo |
| Infraestructura | Manual | Administrada |
| `sparkContext` | Normalmente disponible | Puede no estar disponible |
| Archivos | DBFS/FileStore para clase | Preferir Unity Catalog y Volumes |
| Spark UI | Clasica | Query Profile / query insights |
| Actualizaciones | Manuales | Administradas |

## Ecosistema actual

Databricks hoy no es solo "Spark en la nube". En la plataforma completa incluye
notebooks, SQL warehouses, Workflows, Unity Catalog, Volumes, Delta Lake, Photon,
Liquid Clustering, Lakeflow, Model Serving y herramientas AI/BI como Genie. En
Community Edition veremos lo esencial y marcaremos lo que pertenece al panorama
empresarial.
        """),
        code("""
# Deteccion inicial del entorno Databricks
import sys

print(f"Python: {sys.version}")
print(f"Spark : {spark.version}")

IS_SERVERLESS = False
HAS_SPARK_CONTEXT = False
HAS_UNITY_CATALOG = False

try:
    print("sparkContext.master:", spark.sparkContext.master)
    HAS_SPARK_CONTEXT = True
except Exception as exc:
    IS_SERVERLESS = True
    print("sparkContext no disponible directamente. Probable Spark Connect / Serverless.")
    print(f"Detalle: {type(exc).__name__}: {exc}")

try:
    current_cat = "hive_metastore"
    current_schema = "default"
    current_cat = spark.sql("SELECT current_catalog()").first()[0]
    current_schema = spark.sql("SELECT current_schema()").first()[0]
    HAS_UNITY_CATALOG = current_cat not in ("", None, "hive_metastore")
    print(f"Catalogo actual: {current_cat}")
    print(f"Schema actual  : {current_schema}")
    print(f"Unity Catalog : {HAS_UNITY_CATALOG}")
except Exception as exc:
    print(f"No fue posible detectar catalogo: {exc}")

try:
    photon = spark.conf.get("spark.databricks.photon.enabled", "false")
except Exception:
    photon = "no detectable"

IS_COMMUNITY_STYLE = HAS_SPARK_CONTEXT and not HAS_UNITY_CATALOG
print(f"IS_SERVERLESS={IS_SERVERLESS}, COMMUNITY_STYLE={IS_COMMUNITY_STYLE}, UC={HAS_UNITY_CATALOG}, Photon={photon}")

def nombre_tabla(nombre):
    if HAS_UNITY_CATALOG:
        return f"{current_cat}.{current_schema}.{nombre}"
    return f"{current_schema}.{nombre}"
        """),
        interp("deteccion del entorno", [
            "En Community Edition normalmente `sparkContext` esta disponible.",
            "Si el catalogo es `hive_metastore`, estamos en un esquema clasico sin Unity Catalog.",
            "La funcion `nombre_tabla` permite usar dos o tres niveles segun el entorno."
        ]),
        code("""
# Instalar dependencias de apoyo
# Regla Databricks moderna: usar %pip, no %sh pip.
%pip install "dask[dataframe]>=2024.1" pyarrow -q
        """),
        md("""
## Advertencia comun

`%sh pip install paquete` instala en el entorno del sistema operativo de la sesion,
pero el interprete Python del notebook puede no ver esa instalacion. `%pip`
instala en el entorno activo del notebook y es el patron recomendado.
        """),
    ]


def _seccion_1():
    return [
        section_header("1", "Magic commands y dbutils"),
        md("""
## Definicion formal

Los **magic commands** son comandos especiales de notebook que cambian el modo de
ejecucion de una celda. `dbutils` es una utilidad propia de Databricks para
interactuar con archivos, widgets, secretos y ejecuciones de notebooks.

| Magic | Uso |
|---|---|
| `%python` | Ejecutar Python |
| `%sql` | Ejecutar SQL |
| `%md` | Escribir Markdown |
| `%pip` | Instalar librerias en el entorno del notebook |
| `%run` | Incluir otro notebook |
| `%fs` | Comandos de archivos Databricks |
| `%sh` | Shell del entorno; util con cuidado en clusters clasicos |

## Intuicion

Un notebook puede combinar explicacion, SQL y Python. Para una primera clase,
conviene aprender el equivalente Python de casi todo, porque permite copiar el
codigo dentro de funciones o jobs.
        """),
        code("""
# SQL desde Python: equivalente portable a una celda %sql
consulta = spark.sql('''
SELECT
  current_catalog() AS catalogo,
  current_schema()  AS schema,
  current_date()    AS fecha_actual
''')
consulta.show(truncate=False)
        """),
        interp("magic SQL desde Python", [
            "La salida confirma el catalogo y schema activos.",
            "`spark.sql` permite usar SQL multi-linea dentro de una celda Python.",
            "Esto sera util cuando necesitemos DDL, DML o consultas con CTEs."
        ]),
        md("""
## Modulos frecuentes de `dbutils`

| Modulo | Para que sirve |
|---|---|
| `dbutils.fs` | Listar y manipular archivos accesibles por Databricks |
| `dbutils.widgets` | Parametrizar notebooks |
| `dbutils.secrets` | Leer credenciales almacenadas en secret scopes |
| `dbutils.notebook` | Ejecutar o terminar notebooks desde codigo |

En Community Edition se usa con frecuencia DBFS/FileStore para datos de clase.
En Databricks empresarial moderno, se prefieren **Volumes** de Unity Catalog.
        """),
        code("""
# Listar ubicaciones conocidas con dbutils.fs
for ruta in ["dbfs:/", "dbfs:/FileStore/", "/Volumes/"]:
    print(f"\\nListado de {ruta}")
    try:
        for item in dbutils.fs.ls(ruta)[:10]:
            print(f"  {item.path} | {item.size} bytes")
    except Exception as exc:
        print(f"  No disponible o sin permisos: {exc}")
        """),
        code("""
# Widgets: parametros simples para notebooks y jobs
dbutils.widgets.text("catalogo_param", "samples", "Catalogo")
dbutils.widgets.dropdown("modo_ejecucion", "demo", ["demo", "produccion"], "Modo")

catalogo_param = dbutils.widgets.get("catalogo_param")
modo_ejecucion = dbutils.widgets.get("modo_ejecucion")

print(f"catalogo_param={catalogo_param}")
print(f"modo_ejecucion={modo_ejecucion}")
        """),
        code("""
# Secrets y ejecucion de notebooks: patrones seguros
try:
    scopes = dbutils.secrets.listScopes()
    print("Secret scopes disponibles:")
    for s in scopes:
        print(" ", s.name)
except Exception as exc:
    print(f"No fue posible listar secret scopes: {exc}")

print("\\nPatron correcto para credenciales:")
print("token = dbutils.secrets.get(scope='mi_scope', key='mi_token')")
print("\\nPatron para invocar otro notebook desde un workflow:")
print("dbutils.notebook.run('/Repos/proyecto/otro_notebook', 300, {'fecha': '2026-01-01'})")
        """),
    ]


def _seccion_2():
    return [
        section_header("2", "SparkSession, SparkContext y Spark Connect como panorama"),
        md("""
## Definicion formal

**SparkSession** es la puerta principal para usar Spark desde PySpark. En
Community Edition tambien suele estar disponible **SparkContext**, la API de
nivel mas bajo que conecta con el cluster. **Spark Connect** es el modelo moderno
cliente-servidor usado en varios entornos serverless.

## Intuicion

En Community Edition puedes ver `sparkContext`, lo cual ayuda a entender el
cluster. Aun asi, para aprender bien Databricks conviene trabajar principalmente
con `SparkSession`, DataFrames y SQL.

| API | Recomendacion para esta clase |
|---|---|
| `spark.sql(...)` | Usar |
| `spark.read.table(...)` | Usar |
| DataFrame API | Usar |
| `spark.sparkContext.parallelize(...)` | Conocer, pero no usar como patron principal |
| RDDs | Panorama historico; preferir DataFrames |
| Global temp views | Evitar en clase; usar temp views o tablas |
        """),
        code("""
# Lo que funciona bien: SparkSession, SQL y DataFrames
from pyspark.sql import functions as F

df = spark.range(10).withColumn("cuadrado", F.col("id") * F.col("id"))
df.show()

spark.sql("SELECT 1 + 1 AS suma").show()

# Alternativa moderna a sparkContext.parallelize(...)
df_local = spark.createDataFrame([(1,), (2,), (3,)], ["valor"])
df_local.show()
        """),
        interp("SparkSession y SparkContext", [
            "El ejemplo muestra tres patrones compatibles: `spark.range`, `spark.sql` y `spark.createDataFrame`.",
            "Para una introduccion, basta pensar que Python describe un plan y Spark lo ejecuta en el cluster.",
            "Aunque Community Edition permita RDDs, los DataFrames son el patron central del curso."
        ]),
    ]


def _seccion_3():
    return [
        section_header("3", "Catalogos, tablas, DBFS y Volumes"),
        md("""
## Definicion formal

Databricks organiza tablas en catalogos y schemas. En Community Edition lo mas
comun es trabajar con `hive_metastore.default.tabla` o simplemente
`default.tabla`. En Databricks empresarial moderno, **Unity Catalog** formaliza
el patron `catalog.schema.table` y agrega gobierno, lineage, auditoria y Volumes.

```
catalog
  schema
    table | view | function | volume
```

## Intuicion

En Community Edition preguntamos: "en que database/schema o ruta DBFS esta el
dato". En la plataforma moderna preguntamos: "en que catalogo, schema, tabla o
Volume vive el dato".
        """),
        code("""
# Explorar catalogos, schema y tablas de ejemplo
spark.sql("SHOW CATALOGS").show(truncate=False)

CATALOG = spark.sql("SELECT current_catalog()").first()[0]
SCHEMA = spark.sql("SELECT current_schema()").first()[0]
print(f"Catalogo activo: {CATALOG}")
print(f"Schema activo  : {SCHEMA}")

try:
    spark.sql("SHOW TABLES IN samples.nyctaxi").show(truncate=False)
except Exception as exc:
    print("La tabla samples.nyctaxi no esta disponible en este entorno.")
    print("Usaremos un dataset sintetico de taxis para Community Edition.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
        """),
        code("""
# Leer tabla de muestra si existe; si no, crear dataset sintetico compatible con CE
from pyspark.sql import functions as F

TAXI_TABLE = "samples.nyctaxi.trips"

try:
    sdf = spark.read.table(TAXI_TABLE)
    print(f"Tabla externa disponible: {TAXI_TABLE}")
except Exception:
    print("Creando dataset sintetico de taxis para Community Edition.")
    taxi_rows = [
        ("2026-01-01 08:00:00", "2026-01-01 08:18:00", 10001, 10002, 18.5, 3.2, 2.4, 1),
        ("2026-01-01 09:10:00", "2026-01-01 09:25:00", 10002, 10003, 15.0, 2.0, 1.8, 2),
        ("2026-01-01 10:20:00", "2026-01-01 10:55:00", 11201, 10001, 42.0, 8.0, 7.5, 1),
        ("2026-01-02 14:05:00", "2026-01-02 14:35:00", 11377, 11201, 30.0, 4.5, 5.2, 3),
        ("2026-01-02 18:40:00", "2026-01-02 19:05:00", 10001, 11377, 25.0, 5.0, 3.6, 1),
        ("2026-01-03 21:00:00", "2026-01-03 21:45:00", 11201, 10002, 55.0, 10.0, 9.1, 2),
    ]
    sdf = spark.createDataFrame(
        taxi_rows,
        ["tpep_pickup_datetime", "tpep_dropoff_datetime", "pickup_zip", "dropoff_zip",
         "fare_amount", "tip_amount", "trip_distance", "passenger_count"]
    )
    sdf = (
        sdf
        .withColumn("tpep_pickup_datetime", F.to_timestamp("tpep_pickup_datetime"))
        .withColumn("tpep_dropoff_datetime", F.to_timestamp("tpep_dropoff_datetime"))
    )

sdf.createOrReplaceTempView("taxi_source_v")

def leer_taxi():
    return spark.table("taxi_source_v")

print(f"Filas: {sdf.count():,}")
print(f"Columnas: {len(sdf.columns)}")
sdf.printSchema()
        """),
        interp("tabla de muestra", [
            "Si `samples.nyctaxi.trips` existe se usa; si no, el notebook crea un dataset sintetico para Community Edition.",
            "El schema nos dice tipos de columnas antes de transformar datos.",
            "El conteo confirma que ya tenemos una fuente de taxis disponible para el resto de la clase."
        ]),
        code("""
# DBFS y Volumes
try:
    spark.sql("SHOW VOLUMES IN samples.nyctaxi").show(truncate=False)
except Exception as exc:
    print("Volumes no disponibles en Community Edition o sin permisos.")
    print(f"Detalle: {exc}")

print("Ruta DBFS comun en Community Edition:")
print("dbfs:/FileStore/archivo.csv")
print("\\nRuta de Volume en Databricks con Unity Catalog:")
print("/Volumes/<catalog>/<schema>/<volume>/<archivo>")
print("Ejemplo: /Volumes/main/bronze/raw_files/ventas.parquet")
        """),
        md("""
## Error comun

No uses `C:\\Users\\estudiante\\Downloads\\archivo.csv` dentro de Databricks.
Esa ruta existe en el computador local, no en el compute de Databricks. Primero
sube el archivo a un Volume o crea una tabla.
        """),
    ]


def _seccion_4():
    return [
        section_header("4", "Spark SQL completo: TempViews, DDL y DML"),
        md("""
## Definicion formal

**Spark SQL** permite consultar DataFrames y tablas usando SQL. Una **TempView**
es una vista temporal de sesion creada desde un DataFrame. **DDL** crea o modifica
objetos; **DML** inserta, actualiza o elimina datos.

| Concepto | Ejemplo |
|---|---|
| TempView | `df.createOrReplaceTempView('v')` |
| DDL | `CREATE TABLE`, `DROP TABLE`, `DESCRIBE TABLE` |
| DML | `INSERT INTO`, `MERGE`, `DELETE`, `UPDATE` |

Para compartir resultados entre sesiones, prefiere tablas en el metastore
(`default.mi_tabla` en Community Edition). En workspaces con Unity Catalog,
usa nombres de tres niveles.
        """),
        code("""
# Crear TempView desde un DataFrame y consultarla con SQL
taxi_sample = (
    leer_taxi()
    .select("tpep_pickup_datetime", "fare_amount", "tip_amount", "trip_distance")
    .where("fare_amount > 0 AND trip_distance > 0")
    .limit(10000)
)

taxi_sample.createOrReplaceTempView("taxi_sample_v")

spark.sql('''
SELECT
  COUNT(*) AS viajes,
  ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
  ROUND(AVG(tip_amount), 2) AS propina_promedio
FROM taxi_sample_v
''').show()
        """),
        interp("TempView", [
            "La vista temporal no crea una tabla permanente.",
            "Permite mezclar PySpark y SQL sin duplicar datos.",
            "Desaparece al terminar la sesion del notebook."
        ]),
        code("""
# DDL: crear, describir y eliminar una tabla de practica
SQL_TABLE = nombre_tabla("sesion9_sql_demo")

spark.sql(f"DROP TABLE IF EXISTS {SQL_TABLE}")
spark.sql(f'''
CREATE TABLE IF NOT EXISTS {SQL_TABLE} (
  id BIGINT,
  ciudad STRING,
  valor DOUBLE
)
USING DELTA
''')

if HAS_UNITY_CATALOG:
    spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").show(truncate=False)
else:
    spark.sql(f"SHOW TABLES IN {SCHEMA}").show(truncate=False)
spark.sql(f"DESCRIBE TABLE {SQL_TABLE}").show(truncate=False)
        """),
        code("""
# DML: INSERT INTO y consultas de verificacion
spark.sql(f'''
INSERT INTO {SQL_TABLE} VALUES
  (1, 'Bogota', 120.5),
  (2, 'Cali', 95.0),
  (3, 'Medellin', 150.0)
''')

spark.sql(f"SELECT * FROM {SQL_TABLE} ORDER BY id").show()
spark.sql(f"SHOW COLUMNS IN {SQL_TABLE}").show(truncate=False)
spark.sql(f"SHOW CREATE TABLE {SQL_TABLE}").show(truncate=False)
        """),
        code("""
# CTEs: consultas legibles en varios pasos
spark.sql(f'''
WITH base AS (
  SELECT ciudad, valor
  FROM {SQL_TABLE}
  WHERE valor > 0
),
resumen AS (
  SELECT ciudad, COUNT(*) AS n, ROUND(AVG(valor), 2) AS promedio
  FROM base
  GROUP BY ciudad
)
SELECT *
FROM resumen
ORDER BY promedio DESC
''').show()
        """),
    ]


def _seccion_5():
    return [
        section_header("5", "Tipos de datos y schemas"),
        md("""
## Definicion formal

Un **schema** describe las columnas de un DataFrame: nombre, tipo y nulabilidad.
Spark puede inferirlo, pero en pipelines reales conviene declararlo.

| Tipo | Uso |
|---|---|
| `IntegerType`, `LongType` | Enteros |
| `DoubleType` | Numeros decimales |
| `StringType` | Texto |
| `BooleanType` | Verdadero/falso |
| `DateType`, `TimestampType` | Fechas y tiempos |
| `ArrayType`, `MapType`, `StructType` | Datos semiestructurados |

## Intuicion

El schema es el contrato del dato. Si el contrato cambia sin control, los
resultados dejan de ser confiables.
        """),
        code("""
# Schema explicito con StructType
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, DateType, TimestampType
)
from pyspark.sql import functions as F

schema_ventas = StructType([
    StructField("ciudad", StringType(), False),
    StructField("categoria", StringType(), True),
    StructField("valor", DoubleType(), True),
    StructField("unidades", IntegerType(), True),
    StructField("fecha_txt", StringType(), True),
])

datos_ventas = [
    ("Bogota", "tecnologia", 1200000.0, 2, "2026-01-05"),
    ("Cali", "hogar", 380000.0, 1, "2026-01-06"),
    ("Medellin", "salud", 210000.0, 3, "2026-01-07"),
]

ventas = spark.createDataFrame(datos_ventas, schema_ventas)
ventas.printSchema()
print(ventas.schema)
print(ventas.dtypes)
ventas.show()
        """),
        code("""
# Conversiones con cast, to_date, to_timestamp y try_cast en SQL
ventas_cast = (
    ventas
    .withColumn("valor_int", F.col("valor").cast("long"))
    .withColumn("fecha", F.to_date("fecha_txt"))
    .withColumn("fecha_ts", F.to_timestamp("fecha_txt"))
)
ventas_cast.show()

ventas_cast.createOrReplaceTempView("ventas_cast_v")
spark.sql('''
SELECT
  ciudad,
  valor,
  try_cast(valor AS INT) AS valor_try_int,
  try_cast('texto_no_numerico' AS INT) AS ejemplo_falla_controlada
FROM ventas_cast_v
''').show()
        """),
        interp("schemas y conversiones", [
            "`printSchema` permite verificar el contrato antes de analizar.",
            "`cast` transforma tipos; `try_cast` evita que una conversion imposible rompa toda la consulta.",
            "En pipelines reales, declarar schema reduce errores silenciosos."
        ]),
        code("""
# Schema enforcement en Delta: escribir con contrato controlado
SCHEMA_TABLE = nombre_tabla("sesion9_schema_demo")

spark.sql(f"DROP TABLE IF EXISTS {SCHEMA_TABLE}")
ventas_cast.write.format("delta").mode("overwrite").saveAsTable(SCHEMA_TABLE)

print("Tabla inicial:")
spark.read.table(SCHEMA_TABLE).printSchema()

ventas_extra = ventas_cast.withColumn("canal", F.lit("online"))

try:
    ventas_extra.write.format("delta").mode("append").saveAsTable(SCHEMA_TABLE)
except Exception as exc:
    print("Append con columna extra fallo por schema enforcement.")
    print(f"Detalle: {type(exc).__name__}: {exc}")

print("Para evolucion controlada del schema se usa mergeSchema u operaciones ALTER TABLE.")
        """),
    ]


def _seccion_6():
    return [
        section_header("6", "Lectura y escritura: CSV, JSON, Parquet y Delta"),
        md("""
## Definicion formal

Spark puede leer y escribir multiples formatos. Para una introduccion, los mas
importantes son CSV, JSON, Parquet y Delta.

| Formato | Uso tipico |
|---|---|
| CSV | Intercambio simple, datos pequenos o fuentes legacy |
| JSON | Datos semiestructurados |
| Parquet | Analitica columnar eficiente |
| Delta | Tablas ACID sobre Parquet con historial |

## Modos de escritura

`overwrite` reemplaza, `append` agrega, `ignore` no hace nada si existe,
`error` falla si ya existe.
        """),
        code("""
# Crear datasets sinteticos para mostrar lectura/escritura sin depender de archivos locales
from pyspark.sql import functions as F

io_base = spark.createDataFrame([
    (1, "Bogota", "2026-01-01", 120.0),
    (2, "Cali", "2026-01-02", 90.5),
    (3, "Medellin", "2026-01-03", 150.2),
], ["id", "ciudad", "fecha_txt", "valor"])

io_base = io_base.withColumn("fecha", F.to_date("fecha_txt")).drop("fecha_txt")
io_base.show()
        """),
        code("""
# Parquet en Volume si existe permiso; si no, seguir con tabla Delta
VOLUME_NAME = "sesion9_archivos"
if HAS_UNITY_CATALOG:
    BASE_IO_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}"
else:
    BASE_IO_PATH = "dbfs:/FileStore/sesion9_archivos"

PARQUET_PATH = f"{BASE_IO_PATH}/io_demo_parquet"
JSON_PATH = f"{BASE_IO_PATH}/io_demo_json"
CSV_PATH = f"{BASE_IO_PATH}/io_demo_csv"

try:
    if HAS_UNITY_CATALOG:
        spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME_NAME}")
    io_base.write.mode("overwrite").parquet(PARQUET_PATH)
    io_base.write.mode("overwrite").json(JSON_PATH)
    io_base.write.mode("overwrite").option("header", True).csv(CSV_PATH)

    print("Lectura Parquet:")
    spark.read.parquet(PARQUET_PATH).show()

    print("Lectura JSON:")
    spark.read.json(JSON_PATH).show()

    print("Lectura CSV con opciones:")
    spark.read.option("header", True).option("inferSchema", True).csv(CSV_PATH).show()
except Exception as exc:
    print("No fue posible escribir en la ruta configurada. En Community Edition revisa DBFS/FileStore.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
        """),
        interp("datos locales, DBFS/Volumes y formatos", [
            "Databricks no lee directamente `C:\\Users`; necesita rutas accesibles al workspace.",
            "Parquet conserva schema y es columnar; CSV necesita opciones e inferencia.",
            "Para Community Edition, DBFS/FileStore es suficiente; en entornos empresariales, Volumes es el patron moderno."
        ]),
        md("""
## `saveAsTable()` vs `write.save()`

- `saveAsTable("default.tabla")` crea una tabla en Community Edition.
- `saveAsTable("catalog.schema.tabla")` es el patron con Unity Catalog.
- `write.save("dbfs:/FileStore/...")` o `write.save("/Volumes/...")` escribe archivos en una ruta.
- Para analitica repetible, prefiere tablas Delta.
        """),
        code("""
# Leer, transformar y escribir como tabla Delta
DESTINO_IO = nombre_tabla("sesion9_io_delta")

resultado_io = (
    io_base
    .withColumn("valor_con_iva", F.round(F.col("valor") * 1.19, 2))
    .withColumn("anio", F.year("fecha"))
)

(
    resultado_io.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(DESTINO_IO)
)

spark.read.table(DESTINO_IO).show()
        """),
        code("""
# COPY INTO y Auto Loader: patrones de ingesta
print("COPY INTO para ingesta incremental desde archivos:")
print(f'''
COPY INTO {DESTINO_IO}
FROM 'dbfs:/FileStore/sesion9_archivos/nuevos_archivos/'
FILEFORMAT = PARQUET
COPY_OPTIONS ('mergeSchema' = 'true')
''')

print("Auto Loader para streaming de archivos:")
print('''
df_stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load("dbfs:/FileStore/sesion9_archivos/raw/")
)
''')
        """),
    ]


def _seccion_7():
    return [
        section_header("7", "Lazy evaluation, Catalyst, Jobs, Stages y repartition"),
        md("""
## Definicion formal

Spark usa **lazy evaluation**: las transformaciones construyen un plan, pero no
ejecutan trabajo hasta que aparece una accion. **Catalyst** optimiza ese plan.

```
Codigo PySpark -> Logical plan -> Optimized plan -> Physical plan -> Jobs/Stages/Tasks
```

## Intuicion

Cuando escribes `filter`, `select` o `withColumn`, Spark todavia esta planeando.
Cuando escribes `count`, `show`, `collect`, `toPandas` o `write`, Spark ejecuta.
        """),
        code("""
# Lazy evaluation: construir un plan es rapido porque aun no lee todos los datos
import time
from pyspark.sql import functions as F

t0 = time.perf_counter()
pipeline = (
    sdf
    .filter(F.col("fare_amount") > 0)
    .filter(F.col("trip_distance") > 0.1)
    .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
    .withColumn("tip_pct", F.col("tip_amount") / F.col("fare_amount") * 100)
)
print(f"Construir plan: {(time.perf_counter() - t0) * 1000:.2f} ms")
print(pipeline)
        """),
        code("""
# explain en varios modos
print("PLAN SIMPLE")
pipeline.explain(False)

print("\\nPLAN EXTENDED")
pipeline.explain("extended")

print("\\nPLAN FORMATTED")
pipeline.explain("formatted")
        """),
        interp("planes de Spark", [
            "`Project` suele indicar seleccion o columnas derivadas.",
            "`Filter` representa filtros.",
            "`Exchange` normalmente indica shuffle, una redistribucion costosa."
        ]),
        md("""
## Jobs, Stages y Tasks

- Una **accion** dispara normalmente un Job.
- Un **Stage** es una secuencia de operaciones que puede ejecutarse sin shuffle.
- Un **Task** es la unidad de trabajo paralela sobre una particion.
- Cada `Exchange` suele partir el DAG en nuevos stages.
        """),
        code("""
# Predicate pushdown: seleccionar columnas y filtrar temprano
plan_con_filtro = (
    leer_taxi()
    .select("fare_amount", "trip_distance", "tip_amount")
    .filter(F.col("fare_amount").between(10, 50))
    .filter(F.col("trip_distance") > 1)
)

plan_con_filtro.explain("formatted")
print(f"Filas resultantes: {plan_con_filtro.count():,}")
        """),
        code("""
# repartition vs coalesce
pequeno = spark.range(0, 1000)

try:
    print("Particiones iniciales:", pequeno.rdd.getNumPartitions())
    print("repartition(8):", pequeno.repartition(8).rdd.getNumPartitions())
    print("coalesce(1):", pequeno.coalesce(1).rdd.getNumPartitions())
except Exception as exc:
    print("En Spark Connect algunas APIs RDD pueden no estar disponibles.")
    print("Concepto: repartition hace shuffle balanceado; coalesce reduce particiones con menor costo pero puede desbalancear.")
    print(f"Detalle: {exc}")
        """),
        code("""
# Cache: demo conceptual compatible con entornos donde cache puede estar limitado
base = pipeline.select("pickup_hour", "fare_amount", "tip_pct")

try:
    base.cache()
    print("Primera accion materializa cache:")
    print(base.count())
    print("Segunda accion puede reutilizar cache:")
    base.groupBy("pickup_hour").count().show(5)
    base.unpersist()
except Exception as exc:
    print("Cache no disponible o limitado en este compute.")
    print("En algunos entornos administrados pueden existir restricciones de cache DataFrame/SQL.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
        """),
    ]


def _seccion_8():
    return [
        section_header("8", "Photon y Liquid Clustering"),
        md("""
## Photon

**Photon** es un motor de ejecucion vectorizado de Databricks. Acelera muchas
consultas SQL/DataFrame sin cambiar el codigo.

## Liquid Clustering

**Liquid Clustering** organiza tablas Delta segun columnas de consulta frecuentes.
Es el reemplazo moderno de muchos patrones basados en `PARTITION BY` y `ZORDER`.
        """),
        code("""
# Crear tabla Delta con Liquid Clustering
LC_TABLE = nombre_tabla("taxi_liquid_sesion9")

try:
    spark.sql(f'''
    CREATE OR REPLACE TABLE {LC_TABLE}
    CLUSTER BY (tpep_pickup_datetime, fare_amount)
    AS
    SELECT *
    FROM taxi_source_v
    WHERE fare_amount > 0
    ''')
except Exception as exc:
    print("Liquid Clustering no esta disponible en este entorno; creando tabla Delta normal.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
    spark.sql(f'''
    CREATE OR REPLACE TABLE {LC_TABLE}
    USING DELTA
    AS
    SELECT *
    FROM taxi_source_v
    WHERE fare_amount > 0
    ''')

spark.sql(f"DESCRIBE DETAIL {LC_TABLE}").select(
    "format", "clusteringColumns", "numFiles", "sizeInBytes"
).show(truncate=False)
        """),
        code("""
# OPTIMIZE aplica fisicamente la organizacion
try:
    spark.sql(f"OPTIMIZE {LC_TABLE}")
except Exception as exc:
    print("OPTIMIZE no esta disponible en este entorno o runtime.")
    print(f"Detalle: {type(exc).__name__}: {exc}")

spark.sql(f"DESCRIBE HISTORY {LC_TABLE}").select(
    "version", "timestamp", "operation"
).show(5, truncate=False)
        """),
        md("""
## Predictive Optimization

En workspaces que lo tienen habilitado, Databricks puede ejecutar mantenimiento
como `OPTIMIZE` y `VACUUM` automaticamente segun patrones de uso.
        """),
    ]


def _seccion_9():
    return [
        section_header("9", "Funciones de cadenas, fechas y colecciones"),
        md("""
## Definicion formal

`pyspark.sql.functions` contiene funciones nativas que Spark puede optimizar.
Para una primera introduccion, es mejor preferir estas funciones antes que UDFs.
        """),
        code("""
# Funciones de cadenas
from pyspark.sql import functions as F

texto_df = spark.createDataFrame([
    (1, "  Bogota Norte  ", "factura-2026-0001"),
    (2, "cali sur", "factura-2026-0002"),
    (3, "MEDELLIN centro", "recibo-2025-0099"),
], ["id", "zona", "documento"])

texto_res = (
    texto_df
    .withColumn("zona_limpia", F.trim("zona"))
    .withColumn("zona_upper", F.upper("zona_limpia"))
    .withColumn("largo", F.length("zona_limpia"))
    .withColumn("tipo_doc", F.regexp_extract("documento", r"^([a-z]+)", 1))
    .withColumn("anio_doc", F.regexp_extract("documento", r"(\\d{4})", 1))
    .withColumn("zona_partes", F.split(F.lower("zona_limpia"), " "))
    .withColumn("etiqueta", F.concat_ws(" | ", "zona_upper", "documento"))
)
texto_res.show(truncate=False)
        """),
        code("""
# Funciones de fechas y tiempo
fechas_df = spark.createDataFrame([
    ("2026-01-05 08:30:00",),
    ("2026-02-10 14:45:00",),
    ("2026-03-20 23:05:00",),
], ["ts_txt"])

fechas_res = (
    fechas_df
    .withColumn("ts", F.to_timestamp("ts_txt"))
    .withColumn("fecha", F.to_date("ts"))
    .withColumn("anio", F.year("ts"))
    .withColumn("mes", F.month("ts"))
    .withColumn("dia", F.dayofmonth("ts"))
    .withColumn("hora", F.hour("ts"))
    .withColumn("fecha_mas_7", F.date_add("fecha", 7))
    .withColumn("inicio_mes", F.date_trunc("month", "ts"))
    .withColumn("dias_desde_hoy", F.datediff(F.current_date(), F.col("fecha")))
)
fechas_res.show(truncate=False)
        """),
        code("""
# Arrays y maps
colecciones = spark.createDataFrame([
    (1, ["spark", "delta", "spark"], {"nivel": "intro", "motor": "spark"}),
    (2, ["sql", "parquet"], {"nivel": "intro", "motor": "sql"}),
], ["id", "temas", "meta"])

colecciones_res = (
    colecciones
    .withColumn("n_temas", F.size("temas"))
    .withColumn("temas_unicos", F.array_distinct("temas"))
    .withColumn("incluye_spark", F.array_contains("temas", "spark"))
    .withColumn("meta_keys", F.map_keys("meta"))
    .withColumn("meta_values", F.map_values("meta"))
)
colecciones_res.show(truncate=False)

colecciones_res.select("id", F.explode("temas_unicos").alias("tema")).show()
        """),
        code("""
# Operaciones de conjuntos entre DataFrames
a = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")], ["id", "letra"])
b = spark.createDataFrame([(3, "C"), (4, "D"), (5, "E")], ["id", "letra"])

print("unionByName")
a.unionByName(b).show()

print("intersect")
a.intersect(b).show()

print("subtract")
a.subtract(b).show()

print("distinct despues de union")
a.unionByName(b).distinct().show()
        """),
        interp("funciones nativas", [
            "Las funciones nativas permanecen dentro del plan de Spark.",
            "Spark puede optimizar filtros, proyecciones y expresiones mejor que una UDF Python.",
            "Estas funciones cubren gran parte del trabajo cotidiano de limpieza."
        ]),
    ]


def _seccion_10():
    return [
        section_header("10", "Transformaciones completas de la API PySpark"),
        md("""
## Mapa mental

| Tipo | Operaciones |
|---|---|
| Narrow | `select`, `filter`, `withColumn`, `drop` |
| Wide | `groupBy`, `join`, `distinct`, `orderBy` |
| Analiticas | `Window`, `pivot`, percentiles |
| Calidad | `na.drop`, `na.fill`, `dropDuplicates` |
        """),
        code("""
# Base enriquecida para el tour PySpark
from pyspark.sql.window import Window

enriquecido = (
    sdf
    .select(
        "tpep_pickup_datetime", "tpep_dropoff_datetime",
        "fare_amount", "tip_amount", "trip_distance",
        "passenger_count", "pickup_zip"
    )
    .filter(F.col("fare_amount").between(1, 200))
    .filter(F.col("trip_distance") > 0)
    .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
    .withColumn(
        "duracion_min",
        (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / 60
    )
    .withColumn("tip_pct", F.col("tip_amount") / F.col("fare_amount") * 100)
    .withColumn(
        "categoria_viaje",
        F.when(F.col("trip_distance") < 1, "micro")
         .when(F.col("trip_distance") < 3, "corto")
         .when(F.col("trip_distance") < 10, "medio")
         .otherwise("largo")
    )
    .filter(F.col("duracion_min").between(1, 180))
)
enriquecido.show(5, truncate=False)
        """),
        code("""
# groupBy + agg
metricas = (
    enriquecido
    .groupBy("pickup_hour", "categoria_viaje")
    .agg(
        F.count("*").alias("viajes"),
        F.round(F.avg("fare_amount"), 2).alias("tarifa_prom"),
        F.round(F.avg("tip_pct"), 2).alias("tip_pct_prom"),
        F.round(F.stddev("fare_amount"), 2).alias("tarifa_std"),
        F.round(F.percentile_approx("fare_amount", 0.9), 2).alias("tarifa_p90"),
    )
    .orderBy("pickup_hour", "categoria_viaje")
)
metricas.show(10, truncate=False)
metricas.explain("formatted")
        """),
        code("""
# Window functions
w_hora = Window.partitionBy("pickup_hour").orderBy(F.desc("viajes"))

top_hora = (
    metricas
    .withColumn("rank_en_hora", F.rank().over(w_hora))
    .filter(F.col("rank_en_hora") <= 2)
    .orderBy("pickup_hour", "rank_en_hora")
)
top_hora.show(20, truncate=False)
        """),
        code("""
# Join con broadcast
zip_ref = (
    enriquecido.select("pickup_zip")
    .where(F.col("pickup_zip").isNotNull())
    .distinct()
    .limit(500)
    .withColumn(
        "zona",
        F.when(F.col("pickup_zip").between(10001, 10099), "Manhattan")
         .otherwise("Otra")
    )
)

joined = (
    enriquecido
    .join(F.broadcast(zip_ref), on="pickup_zip", how="left")
    .groupBy("zona")
    .agg(F.count("*").alias("viajes"), F.round(F.avg("fare_amount"), 2).alias("tarifa_prom"))
)
joined.show()
joined.explain("formatted")
        """),
        code("""
# Pivot
pivot_categoria = (
    enriquecido
    .groupBy("pickup_hour")
    .pivot("categoria_viaje", ["micro", "corto", "medio", "largo"])
    .agg(F.count("*"))
    .orderBy("pickup_hour")
)
pivot_categoria.show()
        """),
        code("""
# Calidad de datos
sdf.select([
    F.round(F.sum(F.col(c).isNull().cast("int")) / F.count("*") * 100, 2).alias(c)
    for c in ["fare_amount", "tip_amount", "trip_distance", "pickup_zip", "passenger_count"]
]).show(truncate=False)

limpio = (
    sdf.na.drop(subset=["fare_amount", "trip_distance"])
       .na.fill({"tip_amount": 0.0, "passenger_count": 1})
       .filter(F.col("fare_amount") > 0)
       .filter(F.col("trip_distance") > 0)
       .dropDuplicates(["tpep_pickup_datetime", "tpep_dropoff_datetime", "fare_amount"])
)
print(f"Filas limpias: {limpio.count():,}")
        """),
        code("""
# UDF vs pandas_udf vs funcion nativa: patron pedagogico
print("Orden recomendado:")
print("1. Funcion nativa de pyspark.sql.functions")
print("2. pandas_udf si la logica vectorizada en Python es inevitable")
print("3. udf clasica solo cuando no haya alternativa")

clasificacion_nativa = (
    enriquecido
    .withColumn(
        "tipo_duracion",
        F.when(F.col("duracion_min") < 5, "rapido")
         .when(F.col("duracion_min") < 20, "normal")
         .otherwise("largo")
    )
    .groupBy("tipo_duracion")
    .count()
)
clasificacion_nativa.show()
        """),
        interp("API PySpark", [
            "La API DataFrame permite escribir transformaciones legibles y optimizables.",
            "Los shuffles aparecen en agregaciones, joins y pivots.",
            "Despues de cada salida, interpreta patron descriptivo y limitaciones."
        ]),
    ]


def _seccion_11():
    return [
        section_header("11", "Por que Spark sobre Pandas, y cuando no"),
        md("""
## Idea clave

Pandas no es "malo" y Spark no es "siempre mejor". Pandas gana cuando el dataset
cabe comodamente en memoria y se necesita iterar rapido. Spark gana cuando el
volumen crece, se requieren pipelines reproducibles, SQL distribuido, observabilidad
y tablas gobernadas.
        """),
        code("""
# Comparacion representativa: Spark vs Pandas
import time
import pandas as pd

MUESTRA = leer_taxi().limit(500000)

t0 = time.perf_counter()
spark_res = (
    MUESTRA
    .filter(F.col("fare_amount") > 0)
    .withColumn("hora", F.hour("tpep_pickup_datetime"))
    .groupBy("hora")
    .agg(F.count("*").alias("viajes"), F.round(F.avg("fare_amount"), 2).alias("tarifa_prom"))
    .orderBy("hora")
)
spark_res.show(5)
t_spark = time.perf_counter() - t0

t0 = time.perf_counter()
pdf = MUESTRA.select("fare_amount", "tpep_pickup_datetime").toPandas()
pdf = pdf[pdf["fare_amount"] > 0].copy()
pdf["hora"] = pd.to_datetime(pdf["tpep_pickup_datetime"]).dt.hour
pdf_res = pdf.groupby("hora")["fare_amount"].agg(["count", "mean"]).sort_index()
print(pdf_res.head())
t_pandas = time.perf_counter() - t0

print(f"Spark : {t_spark:.2f}s")
print(f"Pandas: {t_pandas:.2f}s")
print("Nota: el tiempo Pandas incluye toPandas(), que mueve datos al driver.")
        """),
        md("""
## Tabla de decision

| Criterio | Elige Pandas | Elige Spark |
|---|---|---|
| Tamano | Cabe en RAM | Puede superar la RAM |
| Iteracion | Muy rapida | Pipeline estable |
| SQL distribuido | No necesario | Necesario |
| Observabilidad | Baja prioridad | Query Profile / Jobs |
| Tablas Delta | No nativo | Integrado |
        """),
    ]


def _seccion_12():
    return [
        section_header("12", "Por que Spark sobre Dask, y cuando no"),
        md("""
## Diferencia arquitectural

Dask escala Python y se integra muy bien con numpy, scipy y scikit-learn. Spark
trabaja con un optimizador SQL/DataFrame maduro: Catalyst. Por eso Spark suele
ser mas fuerte en data engineering, joins grandes, SQL distribuido y lakehouse.
        """),
        code("""
# Dask vs Spark: ejemplo pequeno sobre la misma muestra
import dask.dataframe as dd

pdf_base = (
    leer_taxi()
    .select("fare_amount", "tpep_pickup_datetime", "pickup_zip")
    .limit(100000)
    .toPandas()
)
pdf_base = pdf_base[pdf_base["fare_amount"] > 0].copy()

ddf = dd.from_pandas(pdf_base, npartitions=8)
sdf_bench = spark.createDataFrame(pdf_base)

t0 = time.perf_counter()
dask_res = (
    ddf.assign(hora=dd.to_datetime(ddf["tpep_pickup_datetime"]).dt.hour)
       .groupby("hora")["fare_amount"]
       .agg(["count", "mean"])
       .compute()
)
t_dask = time.perf_counter() - t0

t0 = time.perf_counter()
spark_bench = (
    sdf_bench
    .withColumn("hora", F.hour("tpep_pickup_datetime"))
    .groupBy("hora")
    .agg(F.count("*").alias("count"), F.avg("fare_amount").alias("mean"))
)
spark_bench.show(5)
t_spark = time.perf_counter() - t0

print(f"Dask : {t_dask:.2f}s")
print(f"Spark: {t_spark:.2f}s")
        """),
        code("""
# Join con broadcast en Spark
ref_pdf = pdf_base[["pickup_zip"]].dropna().drop_duplicates().head(100).copy()
ref_pdf["zona"] = "referencia"

ref_sdf = spark.createDataFrame(ref_pdf)
join_spark = sdf_bench.join(F.broadcast(ref_sdf), on="pickup_zip", how="inner")
print(f"Filas join Spark: {join_spark.count():,}")
join_spark.explain("formatted")
        """),
        md("""
## Tabla de decision

| Criterio | Elige Dask | Elige Spark |
|---|---|---|
| Ecosistema numpy/scipy | Prioritario | Secundario |
| Migracion desde Pandas | Gradual | Requiere nueva mentalidad |
| SQL distribuido | Limitado | Nativo |
| Optimizacion de joins | Menor | Catalyst |
| Lakehouse/Delta | No nativo | Integrado |
        """),
    ]


def _seccion_13():
    return [
        section_header("13", "Delta Lake avanzado"),
        md("""
## Definicion formal

**Delta Lake** guarda datos en archivos Parquet y agrega un transaction log
`_delta_log`. Ese log permite ACID, historial, MERGE, time travel, schema
enforcement y schema evolution.

## Parquet vs Delta

Parquet es formato de archivo. Delta es una capa transaccional sobre Parquet.
        """),
        code("""
# Crear tabla Delta base
DELTA_MAIN = nombre_tabla("taxi_sesion9_main")

try:
    spark.sql(f'''
    CREATE OR REPLACE TABLE {DELTA_MAIN}
    CLUSTER BY (tpep_pickup_datetime, pickup_zip)
    AS
    SELECT
      CAST(row_number() OVER (ORDER BY tpep_pickup_datetime) AS BIGINT) AS trip_id,
      tpep_pickup_datetime,
      tpep_dropoff_datetime,
      pickup_zip,
      dropoff_zip,
      fare_amount,
      tip_amount,
      trip_distance,
      CAST(1 AS INT) AS es_valido
    FROM taxi_source_v
    WHERE fare_amount > 0 AND trip_distance > 0
    ''')
except Exception as exc:
    print("CLUSTER BY no disponible; creando tabla Delta normal.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
    spark.sql(f'''
    CREATE OR REPLACE TABLE {DELTA_MAIN}
    USING DELTA
    AS
    SELECT
      CAST(row_number() OVER (ORDER BY tpep_pickup_datetime) AS BIGINT) AS trip_id,
      tpep_pickup_datetime,
      tpep_dropoff_datetime,
      pickup_zip,
      dropoff_zip,
      fare_amount,
      tip_amount,
      trip_distance,
      CAST(1 AS INT) AS es_valido
    FROM taxi_source_v
    WHERE fare_amount > 0 AND trip_distance > 0
    ''')

spark.sql(f"DESCRIBE DETAIL {DELTA_MAIN}").select("format", "numFiles", "sizeInBytes").show()
        """),
        code("""
# MERGE: upsert
from delta.tables import DeltaTable

updates = spark.createDataFrame([
    (1, 0),
    (2, 0),
    (999999999, 1),
], ["trip_id", "es_valido"])

target = DeltaTable.forName(spark, DELTA_MAIN)

(
    target.alias("t")
    .merge(updates.alias("s"), "t.trip_id = s.trip_id")
    .whenMatchedUpdate(set={"es_valido": "s.es_valido"})
    .whenNotMatchedInsert(values={
        "trip_id": "s.trip_id",
        "tpep_pickup_datetime": "CAST(NULL AS TIMESTAMP)",
        "tpep_dropoff_datetime": "CAST(NULL AS TIMESTAMP)",
        "pickup_zip": "CAST(NULL AS INT)",
        "dropoff_zip": "CAST(NULL AS INT)",
        "fare_amount": "CAST(0 AS DOUBLE)",
        "tip_amount": "CAST(0 AS DOUBLE)",
        "trip_distance": "CAST(0 AS DOUBLE)",
        "es_valido": "s.es_valido",
    })
    .execute()
)

spark.sql(f"DESCRIBE HISTORY {DELTA_MAIN}").select(
    "version", "timestamp", "operation", "operationMetrics"
).show(5, truncate=False)
        """),
        code("""
# Time Travel y RESTORE
version_0 = spark.read.format("delta").option("versionAsOf", 0).table(DELTA_MAIN).count()
actual = spark.read.table(DELTA_MAIN).count()

print(f"Version 0: {version_0:,}")
print(f"Actual   : {actual:,}")

spark.sql(f"RESTORE TABLE {DELTA_MAIN} TO VERSION AS OF 0")
spark.sql(f"DESCRIBE HISTORY {DELTA_MAIN}").select("version", "timestamp", "operation").show(5, truncate=False)
        """),
        md("""
## Schema evolution, CONVERT y CLONE

- **Schema enforcement** evita escribir columnas inesperadas.
- **Schema evolution** permite agregar columnas de forma controlada.
- **CONVERT TO DELTA** convierte Parquet existente a Delta.
- **SHALLOW CLONE** copia metadatos y apunta a los mismos archivos.
- **DEEP CLONE** copia tambien archivos fisicos.
        """),
        code("""
# Schema evolution con ALTER TABLE y mergeSchema
spark.sql(f"ALTER TABLE {DELTA_MAIN} ADD COLUMNS (comentario_calidad STRING)")

df_nueva_col = spark.read.table(DELTA_MAIN).limit(10).withColumn("fuente_lote", F.lit("demo"))
(
    df_nueva_col.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(DELTA_MAIN)
)

spark.read.table(DELTA_MAIN).printSchema()
        """),
        code("""
# CLONE: crear tabla de prueba
CLONE_TABLE = nombre_tabla("taxi_sesion9_clone")

try:
    spark.sql(f"DROP TABLE IF EXISTS {CLONE_TABLE}")
    spark.sql(f"CREATE TABLE {CLONE_TABLE} SHALLOW CLONE {DELTA_MAIN}")
    spark.sql(f"DESCRIBE HISTORY {CLONE_TABLE}").select("version", "timestamp", "operation").show(5, truncate=False)
except Exception as exc:
    print("CLONE puede no estar disponible en Community Edition.")
    print(f"Detalle: {type(exc).__name__}: {exc}")
        """),
        code("""
# VACUUM: eliminar archivos obsoletos
print("VACUUM debe usarse con cuidado porque limita time travel a versiones antiguas.")
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
spark.sql(f"VACUUM {DELTA_MAIN} RETAIN 0 HOURS")
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "true")
spark.sql(f"DESCRIBE DETAIL {DELTA_MAIN}").select("numFiles", "sizeInBytes").show()
        """),
    ]


def _seccion_14():
    return [
        section_header("14", "Lakeflow / Delta Live Tables"),
        md("""
## Definicion formal

**Lakeflow Spark Declarative Pipelines** es la evolucion del producto conocido
como **Delta Live Tables (DLT)**. La API Python todavia usa el modulo `dlt`.

No se ejecuta como celda interactiva comun: se configura como pipeline. Esta
seccion imprime el patron para que el estudiante entienda la arquitectura.
        """),
        code("""
# Codigo pedagogico de pipeline Lakeflow/DLT
PIPELINE_CODE = '''
import dlt
from pyspark.sql import functions as F

@dlt.view(name="taxi_raw_view")
def taxi_raw_view():
    return spark.read.table("default.taxi_source_delta")

@dlt.table(name="taxi_bronze", comment="Ingesta raw")
def taxi_bronze():
    return dlt.read("taxi_raw_view")

@dlt.table(name="taxi_silver", comment="Datos limpios")
@dlt.expect_all({
    "fare_positivo": "fare_amount > 0",
    "distancia_positiva": "trip_distance > 0"
})
@dlt.expect_or_drop("duracion_valida", "tpep_dropoff_datetime >= tpep_pickup_datetime")
def taxi_silver():
    return (
        dlt.read("taxi_bronze")
        .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
        .withColumn("tip_pct", F.col("tip_amount") / F.col("fare_amount") * 100)
    )

@dlt.table(name="taxi_gold_hourly", comment="Metricas por hora")
def taxi_gold_hourly():
    return (
        dlt.read("taxi_silver")
        .groupBy("pickup_hour")
        .agg(
            F.count("*").alias("viajes"),
            F.round(F.avg("fare_amount"), 2).alias("tarifa_prom")
        )
    )
'''

print(PIPELINE_CODE)
print("Para ejecutar: Workflows -> Lakeflow Declarative Pipelines -> Create pipeline")
        """),
        md("""
## Batch vs streaming

- Usa **batch** cuando reprocesas lotes completos o tablas estables.
- Usa **streaming** cuando llegan archivos o eventos nuevos continuamente.
- En Community Edition esta seccion es conceptual; en workspaces pagos verifica los triggers soportados.

## Parametros

Un pipeline puede leer parametros con `spark.conf.get("pipeline.parametro")`.
Esto permite cambiar fuentes, fechas o modos sin editar codigo.
        """),
        code("""
# Patron streaming pedagogico: imprimir, no ejecutar aqui
STREAMING_PATTERN = '''
import dlt

@dlt.table(name="eventos_bronze_stream")
def eventos_bronze_stream():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("dbfs:/FileStore/raw_events/")
    )
'''

print(STREAMING_PATTERN)
        """),
    ]


def _seccion_15():
    return [
        section_header("15", "Databricks Workflows y Jobs"),
        md("""
## Definicion formal

Un **Job** ejecuta una tarea de forma reproducible. Un **Workflow** puede contener
varias tareas conectadas como DAG: notebooks, Python scripts, SQL, pipelines
Lakeflow, dbt u otros tipos.

## Intuicion

El notebook interactivo sirve para aprender y explorar. El Job sirve para operar:
programar, parametrizar, monitorear, reintentar y notificar.
        """),
        md("""
## Conceptos clave

| Concepto | Explicacion |
|---|---|
| Task | Unidad ejecutable dentro de un Job |
| Job cluster | Compute creado para el Job |
| Existing compute | Compute reutilizado |
| Schedule | Programacion cron o trigger |
| Parameters | Valores que cambian sin editar codigo |
| Notifications | Alertas por exito, falla o duracion |
        """),
        md("""
## Jobs vs Lakeflow

Usa **Jobs** para orquestacion general: notebooks, SQL, scripts, modelos, reportes.
Usa **Lakeflow** cuando el problema central es declarar tablas de datos con
dependencias, calidad y procesamiento incremental.
        """),
        code("""
# Patron para que un notebook sea invocable como task
dbutils.widgets.text("fecha_proceso", "2026-01-01", "Fecha de proceso")
dbutils.widgets.dropdown("modo", "demo", ["demo", "produccion"], "Modo")

fecha_proceso = dbutils.widgets.get("fecha_proceso")
modo = dbutils.widgets.get("modo")

print(f"Ejecutando notebook con fecha_proceso={fecha_proceso}, modo={modo}")

# En un Job real, al final se puede devolver un resultado textual:
# dbutils.notebook.exit("ok")
        """),
    ]


def _seccion_16():
    return [
        section_header("16", "Taller end-to-end"),
        md("""
## Objetivo del taller

Aplicar los conceptos de la sesion en ejercicios guiados. Cada ejercicio tiene
instrucciones y deja un `NotImplementedError` para que el estudiante complete.
        """),
        code("""
# Ejercicio 1 -- Window functions
# Construye el top 3 de categorias de viaje por hora con mayor tip_pct promedio.
# Requisitos:
# - Leer la fuente de taxis preparada en `leer_taxi()`.
# - Crear pickup_hour, tip_pct y categoria_viaje.
# - Agrupar por pickup_hour y categoria_viaje.
# - Filtrar grupos con menos de 100 viajes.
# - Usar Window.partitionBy("pickup_hour").orderBy(F.desc("tip_pct_prom")).

raise NotImplementedError("Completa el ejercicio 1 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 2 -- MERGE en Delta
# Crea una tabla Delta con viajes del pickup_zip mas frecuente.
# Luego usa MERGE para marcar es_valido=0 donde fare_amount > 100 e insertar 3 filas nuevas.

raise NotImplementedError("Completa el ejercicio 2 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 3 -- Reporte de calidad
# Construye un DataFrame [metrica, valor] con:
# - pct_nulos por columna
# - pct_negativos para columnas numericas
# - top 5 pickup_zip
# - total_filas

raise NotImplementedError("Completa el ejercicio 3 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 4 -- Schema + I/O
# Define un StructType de 5 columnas, crea DataFrame sintetico, escribe con saveAsTable,
# lee de vuelta, verifica schema y agrega una columna con ALTER TABLE.

raise NotImplementedError("Completa el ejercicio 4 siguiendo las instrucciones.")
        """),
        code("""
# Ejercicio 5 -- Pipeline completo Databricks
# Lee la fuente de taxis preparada, filtra, enriquece con 5 columnas derivadas,
# crea tabla Silver con Liquid Clustering, ejecuta MERGE con 5 actualizaciones
# y muestra DESCRIBE HISTORY.

raise NotImplementedError("Completa el ejercicio 5 siguiendo las instrucciones.")
        """),
        md("""
## Checklist final

```
[ ] Uso `default.tabla` en Community Edition o `catalog.schema.table` en Unity Catalog
[ ] Entiendo por que C:\\Users no funciona dentro de Databricks
[ ] Uso DBFS/FileStore en Community Edition y conozco Volumes como patron moderno
[ ] Prefiero DataFrames/Spark SQL sobre RDDs para el trabajo principal
[ ] Uso %pip, no %sh pip
[ ] Puedo leer CSV, JSON, Parquet y Delta
[ ] Puedo explicar Parquet vs Delta
[ ] Puedo leer un plan con explain()
[ ] Reconozco Exchange como posible shuffle
[ ] Priorizo funciones nativas sobre UDFs
[ ] Entiendo el patron bronze/silver/gold
[ ] Se cuando usar Jobs y cuando Lakeflow
```

## Cierre

La idea mas importante: Databricks no es solo un notebook. Es una plataforma
para convertir datos en tablas confiables, transformaciones reproducibles y
ejecuciones gobernadas.
        """),
        md("""
## Referencias

- Databricks Community Edition: https://docs.databricks.com/en/getting-started/community-edition.html
- Databricks notebooks: https://docs.databricks.com/en/notebooks/
- DBFS: https://docs.databricks.com/en/dbfs/
- Databricks widgets: https://docs.databricks.com/en/notebooks/widgets.html
- Unity Catalog Volumes: https://docs.databricks.com/aws/en/volumes/
- Apache Spark documentation: https://spark.apache.org/docs/latest/
- PySpark functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html
- Apache Parquet: https://parquet.apache.org/docs/
- Delta Lake: https://docs.delta.io/latest/index.html
- Lakeflow Declarative Pipelines: https://docs.databricks.com/en/delta-live-tables/index.html
        """),
    ]


def build_cells():
    cells = [
        *uce_header(
            title="Databricks Community Edition: tutorial completo de introduccion",
            session=9,
            github_path="main/Cuadernos/9_Databricks_Serverless_Completo.ipynb",
            nota_plataforma=(
                "Databricks Community Edition con cluster clasico. "
                "Se incluyen notas de panorama sobre capacidades empresariales modernas."
            ),
        ),
        _proposito(),
        _correspondencia(),
        _toc(),
        *_seccion_0(),
        pregunta(1, "Community Edition", "En esta clase se trabaja con un cluster clasico de Databricks Community Edition.", "Que idea describe mejor este entorno?", ["Spark desaparece", "Permite practicar notebooks, Spark SQL y PySpark con recursos limitados", "Solo se puede usar Pandas", "No existen tablas"], "B", "Community Edition es suficiente para aprender el flujo base de Databricks y Spark."),
        *_seccion_1(),
        pregunta(2, "dbutils", "Los notebooks se parametrizan para jobs.", "Que modulo permite crear parametros visibles en el notebook?", ["dbutils.widgets", "dbutils.fs", "dbutils.secrets", "spark.catalog"], "A", "`dbutils.widgets` crea parametros de entrada."),
        *_seccion_2(),
        pregunta(3, "Spark", "Community Edition suele exponer SparkSession y SparkContext.", "Que API conviene priorizar?", ["RDDs", "sparkContext.parallelize", "DataFrames y Spark SQL", "Loops locales con collect"], "C", "DataFrames y SQL son el patron principal y optimizable."),
        *_seccion_3(),
        pregunta(4, "Tablas", "En Community Edition suele usarse el schema `default`; en Unity Catalog se usan tres niveles.", "Cual ruta NO debe usarse dentro de Databricks para leer datos del computador local?", ["default.trips", "hive_metastore.default.trips", "catalog.schema.table", "C:/datos/trips.csv"], "D", "Databricks no ve directamente el disco local del estudiante; se debe subir el archivo a DBFS o a un Volume."),
        *_seccion_4(),
        pregunta(5, "Spark SQL", "Una TempView vive durante la sesion.", "Que conviene usar para persistir resultados en Community Edition?", ["TempView", "Tabla en `default`", "Variable Python", "print"], "B", "Una tabla en el metastore permanece disponible despues de la celda."),
        *_seccion_5(),
        pregunta(6, "Schemas", "El schema es el contrato del dato.", "Por que declarar schema ayuda?", ["Evita toda ejecucion", "Reduce errores de inferencia y cambios silenciosos", "Convierte todo a texto", "Elimina permisos"], "B", "Un contrato explicito mejora confiabilidad."),
        *_seccion_6(),
        pregunta(7, "Parquet", "Parquet es columnar y Delta agrega log transaccional.", "Que afirmacion es correcta?", ["Parquet y Delta son identicos", "Delta usa Parquet mas transaction log", "CSV siempre es mas eficiente", "Delta solo sirve para imagenes"], "B", "Delta agrega ACID, historial y MERGE sobre datos Parquet."),
        *_seccion_7(),
        pregunta(8, "Lazy evaluation", "Spark no ejecuta transformaciones hasta una accion.", "Cual es una accion?", ["filter", "select", "withColumn", "count"], "D", "`count` dispara ejecucion."),
        *_seccion_8(),
        pregunta(9, "Photon", "Photon acelera consultas compatibles sin cambiar codigo.", "Donde se verifica el rendimiento?", ["Query Profile", "Nombre del archivo", "Ruta C:/Users", "Markdown"], "A", "Query Profile muestra detalles de ejecucion."),
        *_seccion_9(),
        pregunta(10, "Funciones", "Las funciones nativas son optimizables.", "Que conviene preferir?", ["UDF Python siempre", "Funciones nativas de PySpark", "collect y for", "Pandas para todo"], "B", "Las funciones nativas permanecen dentro del motor Spark."),
        *_seccion_10(),
        *_seccion_11(),
        pregunta(11, "Spark vs Pandas", "Pandas es excelente si todo cabe en RAM.", "Cuando suele ganar Spark?", ["Datos grandes y pipelines reproducibles", "Cinco filas locales", "Editar a mano", "Sin SQL ni crecimiento"], "A", "Spark gana por escala, SQL distribuido y operacion."),
        *_seccion_12(),
        pregunta(12, "Spark vs Dask", "Dask escala Python; Spark optimiza planes SQL/DataFrame.", "Que ventaja es clara de Spark?", ["Catalyst y SQL distribuido", "Editar Excel", "No usar tablas", "Solo numpy local"], "A", "Catalyst optimiza consultas antes de ejecutarlas."),
        *_seccion_13(),
        pregunta(13, "Delta Lake", "Delta tiene transaction log.", "Que habilita?", ["MERGE, time travel y ACID", "Leer disco local C:", "Eliminar schemas", "Evitar todos los jobs"], "A", "El log permite control transaccional e historial."),
        *_seccion_14(),
        *_seccion_15(),
        pregunta(14, "Workflows", "Un Job operacionaliza un notebook.", "Que pregunta resume la sesion?", ["Como traigo todo al driver?", "Donde vive el dato, que plan ejecuta Spark y como lo opero?", "Como evito tablas?", "Como reemplazo Spark con for loops?"], "B", "La mentalidad correcta conecta datos, motor, tablas y operacion."),
        *_seccion_16(),
    ]
    return cells


if __name__ == "__main__":
    cells = build_cells()
    validate(cells)
    save(cells, "Cuadernos/9_Databricks_Serverless_Completo.ipynb")
