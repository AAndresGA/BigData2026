# -*- coding: utf-8 -*-
"""
Genera Cuadernos/11_Spark_SECOP_Solucion_Taller.ipynb

Sesion 11: solucion guiada del taller SECOP usando Spark en Databricks.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header, toc, section_header


def interp(titulo, puntos):
    return md(
        "### Como interpretar el resultado -- " + titulo + "\n\n" +
        "\n".join(f"- {p}" for p in puntos)
    )


def ficha(nombre, sirve, parametros, devuelve, interpreta):
    return md(f"""
### Mini ficha de funcion: `{nombre}`

| Elemento | Explicacion |
|---|---|
| Funcion usada | `{nombre}` |
| Para que sirve | {sirve} |
| Parametros usados | {parametros} |
| Que devuelve | {devuelve} |
| Como interpretar la salida | {interpreta} |
    """)


PREGUNTAS_TALLER = {
    1: """### Enunciado literal del taller original

**Pregunta 1 -- Concentracion territorial del gasto publico**

**Variables requeridas:** `departamento`, `valor_total_adquisicion`, año extraido de `fecha_de_publicacion_del_proceso`

Calcula el **valor total contratado por departamento** y su **porcentaje sobre el total nacional**. Presenta:
- Tabla: top 10 departamentos, valor total, % del total, % acumulado
- Grafica de barras horizontales
- Responde: ¿Los 5 primeros departamentos concentran mas del 60% del gasto? ¿Que indica esto sobre la centralizacion?

**Limpieza necesaria:** Convertir columna de valor a numerico (`dd.to_numeric`). Extraer año con `.dt.year`.""",
    2: """### Enunciado literal del taller original

**Pregunta 2 -- Variabilidad por tipo de contrato**

**Variables requeridas:** `tipo_de_contrato`, `valor_total_adquisicion`, `modalidad_de_contratacion`, `departamento`

Para cada tipo de contrato calcula: **valor promedio**, **desviacion estandar** y **coeficiente de variacion (CV = std/mean)**. Presenta:
- Tabla ordenada por CV descendente
- Grafica de barras comparando el CV por tipo
- Responde: ¿Que tipo de contrato tiene mayor dispersion de valores? ¿Por que crees que ocurre esto?

**Limpieza necesaria:** Valor a numerico. Filtrar filas donde valor > 0 y no nulo.""",
    3: """### Enunciado literal del taller original

**Pregunta 3 -- Evolucion mensual de la contratacion**

**Variables requeridas:** `fecha_de_publicacion_del_proceso`, `tipo_de_contrato`, `estado_del_proceso`, `valor_total_adquisicion`

Grafica el **numero de contratos publicados por mes y año**. Presenta:
- Serie de tiempo con linea (eje x = mes-año, eje y = cantidad de contratos)
- Colorea o separa por `tipo_de_contrato` (top 3 tipos)
- Responde: ¿Hay algun mes o periodo con pico inusual? ¿A que podria atribuirse?

**Limpieza necesaria:** Parsear fecha con `dd.to_datetime(..., errors='coerce')`. Extraer año y mes. Manejar fechas nulas.""",
    4: """### Enunciado literal del taller original

**Pregunta 4 -- Proveedores dominantes**

**Variables requeridas:** `proveedor_adjudicado`, `valor_total_adquisicion`, `tipo_de_contrato`, `departamento`

Identifica los **20 proveedores con mayor valor total adjudicado**. Presenta:
- Tabla: proveedor, valor total, cantidad de contratos, % del total nacional, departamento mas frecuente
- Grafica de barras horizontales (top 20)
- Responde: ¿Hay concentracion en pocos proveedores? ¿Cuantos proveedores acumulan el 30% del gasto total?

**Limpieza necesaria:** Normalizar texto del proveedor (`.str.strip().str.upper()`). Filtrar nulos en proveedor.""",
    5: """### Enunciado literal del taller original

**Pregunta 5 -- Duracion vs valor del contrato**

**Variables requeridas:** `duracion`, `unidad_de_duracion`, `valor_total_adquisicion`, `departamento`, `tipo_de_contrato`

Convierte todas las duraciones a **dias** (1 mes = 30 dias, 1 año = 365 dias). Clasifica:
- **Corto**: < 30 dias
- **Mediano**: 30-365 dias
- **Largo**: > 365 dias

Calcula el valor promedio por categoria y departamento. Presenta:
- Heatmap o tabla pivote: filas = categoria de duracion, columnas = top 10 departamentos, valores = valor promedio
- Responde: ¿El valor promedio crece con la duracion? ¿Es consistente entre departamentos?

**Limpieza necesaria:** Convertir duracion a numerico. Crear funcion de conversion a dias segun `unidad_de_duracion`.""",
    6: """### Enunciado literal del taller original

**Pregunta 6 -- Efectividad por sector del estado**

**Variables requeridas:** `estado_del_proceso`, `sector`, `orden`, `modalidad_de_contratacion`, `valor_total_adquisicion`

Calcula para cada sector (o `orden`) la tasa de:
- Procesos **Celebrados** (exitosos)
- Procesos **Desiertos** (sin adjudicacion)
- Procesos **Cancelados**

Presenta:
- Grafico de barras apiladas al 100% (stacked bar) por sector
- Tabla con tasa de exito (% celebrado) ordenada descendente
- Responde: ¿Que sectores tienen la mayor tasa de procesos fallidos? ¿Que implicaciones tiene para el gasto publico?

**Limpieza necesaria:** Normalizar texto de `estado_del_proceso` y `sector` (strip + upper). Agrupar estados similares si hay variantes.""",
    7: """### Enunciado literal del taller original

**Pregunta 7 -- Contratacion directa vs licitacion**

**Variables requeridas:** `modalidad_de_contratacion`, `valor_total_adquisicion`, `tipo_de_contrato`, `departamento`, año

Compara el **valor promedio de contratos** entre las modalidades principales. Presenta:
- Boxplot o grafica de violin (si tienes muchos datos, usa cuantiles con Dask)
- Tabla: modalidad, conteo, valor promedio, mediana aproximada, total
- Evolucion anual: ¿como cambia la proporcion de contratacion directa vs licitacion en el tiempo?
- Responde: ¿La contratacion directa se asocia a montos mas bajos o mas altos? ¿Que implicaciones tiene?

**Nota Dask:** Dask no soporta `median()` exacto en distribuido. Usa `.quantile(0.5)` como aproximacion o `describe()` para percentiles.""",
    8: """### Enunciado literal del taller original

**Pregunta 8 -- Ranking de entidades contratantes**

**Variables requeridas:** `nombre_entidad`, `valor_total_adquisicion`, `tipo_de_contrato`, `estado_del_proceso`, `departamento`

Construye el **ranking de las 15 entidades mas activas** (por numero de procesos). Para cada una muestra:
- Total de procesos publicados
- Valor total contratado
- Valor promedio por contrato
- Tipo de contrato mas frecuente
- Tasa de celebracion (% procesos celebrados)

Presenta:
- Tabla completa con las 5 metricas anteriores
- Grafica de dispersion: eje x = numero de contratos, eje y = valor promedio, tamaño del punto = valor total
- Responde: ¿Las entidades con mas contratos son tambien las que mas gastan por contrato?

**Limpieza necesaria:** Normalizar nombre de entidad.""",
    9: """### Enunciado literal del taller original

**Pregunta 9 -- Deteccion de outliers economicos**

**Variables requeridas:** `valor_total_adquisicion`, `tipo_de_contrato`, `nombre_entidad`, `departamento`, `estado_del_proceso`

Para cada tipo de contrato calcula la **media (mu)** y **desviacion estandar (sigma)** del valor. Marca como **outlier** todo contrato con valor > mu + 3 sigma.

Presenta:
- Tabla de outliers: entidad, departamento, tipo, valor, cuantas desviaciones sobre la media
- Mapa o grafico de barras: ¿en que departamentos se concentran los outliers?
- Responde: ¿Los outliers son errores de datos o contratos legitimamente grandes? ¿Como distinguirlos?

**Nota Dask:** Calcula mu y sigma por tipo con Dask (`.compute()`), luego aplica el filtro con `map_partitions`.""",
    10: """### Enunciado literal del taller original

**Pregunta 10 (Reto) -- Indicador de heterogeneidad contractual**

**Variables requeridas:** `nombre_entidad`, `valor_total_adquisicion`, `tipo_de_contrato`, `departamento`, `sector`

Para cada entidad con **mas de 50 contratos registrados**, calcula el **Coeficiente de Variacion (CV = std / mean)** del valor. Un CV > 2.0 puede indicar heterogeneidad inusual en los montos de una misma entidad.

Presenta:
- Top 20 entidades con mayor CV (con su departamento, sector y numero de contratos)
- Grafica de dispersion: eje x = numero de contratos, eje y = CV, colorear por sector
- Responde: ¿Que sectores dominan el top 20 de alta heterogeneidad? ¿Que hipotesis plantearias sobre las causas?

**Nota:** Este es un indicador estadistico, **no una acusacion**. Alta varianza puede deberse a tipos de contrato mixtos, proyectos de escala muy diferente, o errores de datos.""",
}


def enunciado_original(num):
    return md(PREGUNTAS_TALLER[num])


def codigo_base_librerias():
    return code("""
# Librerias base de Spark para todo el cuaderno
from pyspark.sql import functions as F
from pyspark.sql import Window
import time

print("Spark:", spark.version)
print("Este cuaderno esta disenado para Databricks con Spark DataFrames, SQL, Volumes y Parquet.")
    """)


def parametros_databricks():
    return code("""
# ============================================================
# PARAMETROS DEL CUADERNO
# ============================================================
# Este notebook se ejecuta en Databricks, no en el repo local. Por eso primero
# detectamos el catalogo y el esquema activos del workspace. En algunos espacios
# existe `main`; en otros NO existe. Si tu workspace no tiene `main`, usa el
# catalogo que aparezca en SHOW CATALOGS.

def valor_sql_escalar(query, default=None):
    try:
        return spark.sql(query).first()[0]
    except Exception:
        return default

CATALOG_DETECTADO = valor_sql_escalar("SELECT current_catalog()", None)
SCHEMA_DETECTADO = valor_sql_escalar("SELECT current_schema()", None)

try:
    catalogos_disponibles = [row[0] for row in spark.sql("SHOW CATALOGS").take(50)]
except Exception:
    catalogos_disponibles = []

print("Catalogo detectado:", CATALOG_DETECTADO)
print("Schema detectado:", SCHEMA_DETECTADO)
print("Catalogos disponibles:", catalogos_disponibles)

# Defaults validados en este curso:
# - Catalogo: workspace
# - Schema: default
# - Volume del taller: tallerspark
# Si tu workspace usa otros nombres, cambia estas tres variables.
CATALOG_PREFERIDO = "workspace"
SCHEMA_PREFERIDO = "default"
VOLUME_PREFERIDO = "tallerspark"

CATALOG = CATALOG_PREFERIDO if CATALOG_PREFERIDO in catalogos_disponibles else (CATALOG_DETECTADO or (catalogos_disponibles[0] if catalogos_disponibles else "<catalog>"))
SCHEMA = SCHEMA_PREFERIDO
VOLUME = VOLUME_PREFERIDO

RAW_CSV_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/secop/raw_csv/"
PARQUET_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/secop/parquet/"
LATENCIA_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/secop/resultados_latencia/"

TABLA_RAW = f"{CATALOG}.{SCHEMA}.secop_raw"
TABLA_ANALITICA = f"{CATALOG}.{SCHEMA}.secop_base_analitica"
TABLA_LATENCIA = f"{CATALOG}.{SCHEMA}.resultados_latencia"

# modo_demo: pocos archivos o muestra pequena
# modo_clase: muestra de clase, por ejemplo 300k filas
# modo_completo: base completa, solo si hay cuota y almacenamiento suficiente
MODO_EJECUCION = "modo_clase"

print("Rutas que usara el cuaderno:")
print("RAW_CSV_PATH :", RAW_CSV_PATH)
print("PARQUET_PATH :", PARQUET_PATH)
print("TABLA_ANALITICA :", TABLA_ANALITICA)
print("MODO_EJECUCION :", MODO_EJECUCION)

if CATALOG in (None, "", "<catalog>"):
    raise ValueError(
        "No se detecto un catalogo valido. Ejecuta SHOW CATALOGS en Databricks "
        "y asigna CATALOG manualmente en esta celda."
    )
    """)


def verificar_volume():
    return code("""
# Crear esquema y Volume si el usuario tiene permisos.
# Si no tienes permisos, usa un Volume ya creado por el docente y cambia
# CATALOG, SCHEMA y VOLUME en la celda de parametros.
try:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME}")
    print("Schema y Volume verificados o creados correctamente.")
except Exception as e:
    print("No se pudo crear el schema o el Volume desde el notebook.")
    print("Usa un Volume existente o solicita permisos al administrador/docente.")
    print("Detalle tecnico:", str(e)[:500])

# Verificacion orientativa del Volume.
# Si esta celda falla, no significa que Spark este mal: normalmente indica que
# el Volume aun no existe, que el usuario no tiene permiso o que los archivos
# todavia no se han subido a la ruta esperada.
try:
    archivos = dbutils.fs.ls(RAW_CSV_PATH)
    print(f"Archivos encontrados en RAW_CSV_PATH: {len(archivos)}")
    for item in archivos[:10]:
        print(item.path, item.size)
except Exception as e:
    print("No se pudo listar RAW_CSV_PATH.")
    print("Revisa que exista el Volume y que hayas subido los CSV a:")
    print(RAW_CSV_PATH)
    print("Detalle tecnico:", str(e)[:500])
    """)


def descargar_secop_a_volume():
    return code("""
# ============================================================
# DESCARGA DE SECOP HACIA VOLUMES
# ============================================================
# Si el Volume esta vacio, esta celda descarga chunks CSV desde datos.gov.co.
# No descarga al computador local ni al repositorio: escribe directamente en
# /Volumes/<catalog>/<schema>/<volume>/secop/raw_csv/
#
# Nota: en algunos entornos Free/serverless, el acceso externo a internet puede
# estar restringido. Si falla por red/permisos, usa la interfaz de Databricks
# para subir los CSV al mismo RAW_CSV_PATH.

from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import time

SECOP_CSV_URL = "https://www.datos.gov.co/resource/p6dx-8zbt.csv"
CHUNK_SIZE = 100_000

if MODO_EJECUCION == "modo_demo":
    OFFSETS_DESCARGA = [0]
elif MODO_EJECUCION == "modo_clase":
    OFFSETS_DESCARGA = [0, 100_000, 200_000]
elif MODO_EJECUCION == "modo_completo":
    # Ajusta TOTAL_FILAS si datos.gov.co reporta un volumen diferente.
    # El dataset cambia con el tiempo.
    TOTAL_FILAS = 8_600_000
    OFFSETS_DESCARGA = list(range(0, TOTAL_FILAS, CHUNK_SIZE))
else:
    raise ValueError("MODO_EJECUCION debe ser modo_demo, modo_clase o modo_completo")

def asegurar_directorio_volume(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def descargar_chunk_secop(offset, limit=CHUNK_SIZE):
    asegurar_directorio_volume(RAW_CSV_PATH)
    destino = Path(RAW_CSV_PATH) / f"secop_chunk_{offset:07d}.csv"
    if destino.exists() and destino.stat().st_size > 0:
        print(f"Ya existe: {destino.name} ({destino.stat().st_size / 1024 / 1024:.1f} MB)")
        return str(destino)

    params = urlencode({"$limit": limit, "$offset": offset})
    url = f"{SECOP_CSV_URL}?{params}"
    print(f"Descargando offset={offset:,} limit={limit:,} -> {destino.name}")

    inicio = time.perf_counter()
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=600) as response:
        contenido = response.read()
    destino.write_bytes(contenido)
    segundos = time.perf_counter() - inicio

    print(f"OK {destino.name}: {len(contenido) / 1024 / 1024:.1f} MB en {segundos:.1f}s")
    return str(destino)

print("Modo de descarga:", MODO_EJECUCION)
print("Chunks a preparar:", len(OFFSETS_DESCARGA))
print("Destino:", RAW_CSV_PATH)

archivos_descargados = []
for offset in OFFSETS_DESCARGA:
    try:
        archivos_descargados.append(descargar_chunk_secop(offset))
    except Exception as e:
        print("No se pudo descargar el chunk offset=", offset)
        print("Detalle:", str(e)[:800])
        print("Si el error es de internet o permisos, sube manualmente los CSV al Volume:")
        print(RAW_CSV_PATH)
        break

print("Archivos listos:", len(archivos_descargados))
    """)


def leer_csv_y_reducir():
    return code("""
# Leer CSV crudo desde Volumes.
# No inferimos schema en CSV. En SECOP una misma columna puede venir como numero
# en un chunk y como texto en otro; con `inferSchema=True`, Spark puede fallar al
# mezclar archivos con errores como DELTA_FAILED_TO_MERGE_FIELDS.
# Leemos el CSV como texto estable y convertimos despues con `try_cast`.

try:
    archivos_csv = [
        item.path for item in dbutils.fs.ls(RAW_CSV_PATH)
        if item.path.lower().endswith(".csv")
    ]
except Exception as e:
    archivos_csv = []
    print("No se pudo listar RAW_CSV_PATH.")
    print("Ruta esperada:", RAW_CSV_PATH)
    print("Causa frecuente: el catalogo/schema/Volume no existe o no tienes permisos.")
    print("Catalogos disponibles detectados arriba:", catalogos_disponibles)
    print("Solucion: cambia CATALOG, SCHEMA y VOLUME en la celda de parametros, o ejecuta la celda de creacion/descarga con permisos.")
    print("Detalle tecnico:", str(e)[:800])

if not archivos_csv:
    raise ValueError(
        "No hay CSV disponibles para leer. Primero descarga los chunks SECOP hacia el Volume "
        "o sube archivos CSV manualmente a: " + RAW_CSV_PATH
    )

print(f"Archivos CSV encontrados: {len(archivos_csv)}")
for ruta in archivos_csv[:5]:
    print(" -", ruta)

df_csv_raw = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .option("multiLine", True)
    .option("escape", '"')
    .csv(archivos_csv)
)

print("Columnas disponibles:", len(df_csv_raw.columns))
display(df_csv_raw.limit(3))
    """)


def crear_base_analitica():
    return code("""
# El taller original usa nombres pedagogicos como `departamento` o
# `valor_total_adquisicion`, pero el CSV real de Socrata puede traer nombres
# como `departamento_entidad`, `valor_total_adjudicacion` o `entidad`.
# Por eso primero mapeamos nombres reales a nombres canonicos.

CANDIDATOS_COLUMNAS = {
    "departamento": ["departamento", "departamento_entidad", "departamento_proveedor"],
    "valor_total_adquisicion": ["valor_total_adquisicion", "valor_total_adjudicacion", "precio_base"],
    "fecha_de_publicacion_del_proceso": [
        "fecha_de_publicacion_del_proceso",
        "fecha_de_publicacion_del",
        "fecha_de_publicacion",
        "fecha_de_ultima_publicaci",
    ],
    "tipo_de_contrato": ["tipo_de_contrato"],
    "modalidad_de_contratacion": ["modalidad_de_contratacion"],
    "proveedor_adjudicado": ["proveedor_adjudicado", "nombre_del_proveedor", "nit_del_proveedor_adjudicado"],
    "duracion": ["duracion"],
    "unidad_de_duracion": ["unidad_de_duracion"],
    "estado_del_proceso": ["estado_del_proceso", "estado_resumen", "estado_del_procedimiento", "estado_de_apertura_del_proceso"],
    "sector": ["sector"],
    "orden": ["orden", "ordenentidad"],
    "nombre_entidad": ["nombre_entidad", "entidad"],
}

def elegir_columna(df_entrada, nombre_canonico, obligatoria=True):
    disponibles = set(df_entrada.columns)
    for candidata in CANDIDATOS_COLUMNAS[nombre_canonico]:
        if candidata in disponibles:
            return candidata
    if obligatoria:
        raise ValueError(
            "No se encontro columna para "
            + nombre_canonico
            + ". Candidatas esperadas: "
            + ", ".join(CANDIDATOS_COLUMNAS[nombre_canonico])
            + ". Columnas reales disponibles: "
            + ", ".join(df_entrada.columns)
        )
    return None

def construir_base_secop(df_entrada):
    mapa_columnas = {}
    for nombre in CANDIDATOS_COLUMNAS:
        mapa_columnas[nombre] = elegir_columna(
            df_entrada,
            nombre,
            obligatoria=(nombre != "sector")
        )

    print("Mapa de columnas usado:")
    for canonica, real in mapa_columnas.items():
        print(f"  {canonica:35s} <- {real}")

    expresiones = []
    for canonica, real in mapa_columnas.items():
        if real is None:
            expresiones.append(F.lit(None).cast("string").alias(canonica))
        else:
            expresiones.append(F.col(real).alias(canonica))

    df_reducido = df_entrada.select(*expresiones)

    return (
        df_reducido
        .withColumn("departamento_norm", F.upper(F.trim(F.col("departamento"))))
        .withColumn("tipo_contrato_norm", F.upper(F.trim(F.col("tipo_de_contrato"))))
        .withColumn("modalidad_norm", F.upper(F.trim(F.col("modalidad_de_contratacion"))))
        .withColumn("proveedor_norm", F.upper(F.trim(F.col("proveedor_adjudicado"))))
        .withColumn("estado_norm", F.upper(F.trim(F.col("estado_del_proceso"))))
        .withColumn("sector_norm", F.upper(F.trim(F.col("sector"))))
        .withColumn("orden_norm", F.upper(F.trim(F.col("orden"))))
        .withColumn("entidad_norm", F.upper(F.trim(F.col("nombre_entidad"))))
        .withColumn(
            "valor_contrato",
            F.expr("try_cast(regexp_replace(cast(valor_total_adquisicion as string), '[^0-9.-]', '') as double)")
        )
        .withColumn(
            "duracion_num",
            F.expr("try_cast(regexp_replace(cast(duracion as string), '[^0-9.-]', '') as double)")
        )
        .withColumn(
            "fecha_publicacion",
            F.expr("try_cast(fecha_de_publicacion_del_proceso as timestamp)")
        )
        .withColumn("anio", F.year("fecha_publicacion"))
        .withColumn("mes", F.month("fecha_publicacion"))
        .withColumn("mes_anio", F.date_format("fecha_publicacion", "yyyy-MM"))
        .withColumn(
            "duracion_dias",
            F.when(F.upper(F.col("unidad_de_duracion")).contains("DIA"), F.col("duracion_num"))
             .when(F.upper(F.col("unidad_de_duracion")).contains("MES"), F.col("duracion_num") * F.lit(30.0))
             .when(F.upper(F.col("unidad_de_duracion")).contains("ANO"), F.col("duracion_num") * F.lit(365.0))
             .when(F.upper(F.col("unidad_de_duracion")).contains("AÑO"), F.col("duracion_num") * F.lit(365.0))
             .otherwise(F.col("duracion_num"))
        )
        .withColumn(
            "categoria_duracion",
            F.when(F.col("duracion_dias") < 30, F.lit("Corto"))
             .when(F.col("duracion_dias") <= 365, F.lit("Mediano"))
             .when(F.col("duracion_dias") > 365, F.lit("Largo"))
             .otherwise(F.lit("Sin dato"))
        )
    )

columnas_necesarias = list(CANDIDATOS_COLUMNAS.keys())

df_secop_limpio = construir_base_secop(df_csv_raw)

display(df_secop_limpio.limit(5))
    """)


def escribir_parquet():
    return code("""
# Escribir la base limpia y reducida a Parquet en el Volume.
# Esta escritura no usa DBFS root ni rutas locales: queda gobernada por Unity Catalog Volumes.
# Si ya existia una version vieja con otro esquema, la retiramos para evitar
# mezclar archivos Parquet incompatibles.
try:
    dbutils.fs.rm(PARQUET_PATH, True)
    print("Parquet anterior retirado:", PARQUET_PATH)
except Exception as e:
    print("No se retiro Parquet anterior o no existia. Continuamos.")
    print("Detalle:", str(e)[:300])

(
    df_secop_limpio
    .write
    .mode("overwrite")
    .parquet(PARQUET_PATH)
)

print("Base reducida escrita en Parquet:")
print(PARQUET_PATH)

df_secop_parquet = spark.read.parquet(PARQUET_PATH)
display(df_secop_parquet.limit(5))
    """)


def comparar_latencia():
    return code("""
# Comparacion didactica de latencia CSV vs Parquet.
# El CSV se lee como texto estable, sin inferSchema, y despues se tipa con
# try_cast. Asi evitamos conflictos entre chunks con formatos diferentes.
# Se mide con acciones pequenas y comparables. No es un benchmark universal.

def medir(nombre, formato, operacion):
    inicio = time.perf_counter()
    valor = operacion()
    segundos = time.perf_counter() - inicio
    return (nombre, formato, float(segundos), str(valor))

df_csv_para_medicion = (
    construir_base_secop(
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .option("multiLine", True)
        .option("escape", '"')
        .csv(archivos_csv)
    )
)

df_parquet_para_medicion = spark.read.parquet(PARQUET_PATH)

mediciones = []
mediciones.append(medir("conteo_filas", "CSV", lambda: df_csv_para_medicion.count()))
mediciones.append(medir("conteo_filas", "Parquet", lambda: df_parquet_para_medicion.count()))

mediciones.append(medir(
    "top_departamentos",
    "CSV",
    lambda: (
        df_csv_para_medicion
        .groupBy("departamento_norm")
        .count()
        .orderBy(F.desc("count"))
        .limit(10)
        .count()
    )
))

mediciones.append(medir(
    "top_departamentos",
    "Parquet",
    lambda: (
        df_parquet_para_medicion
        .groupBy("departamento_norm")
        .count()
        .orderBy(F.desc("count"))
        .limit(10)
        .count()
    )
))

mediciones.append(medir(
    "filtro_anio",
    "CSV",
    lambda: (
        df_csv_para_medicion
        .filter(F.col("anio") >= 2024)
        .count()
    )
))

mediciones.append(medir(
    "filtro_anio",
    "Parquet",
    lambda: df_parquet_para_medicion.filter(F.col("anio") >= 2024).count()
))

df_latencia = spark.createDataFrame(
    mediciones,
    ["operacion", "formato", "segundos", "resultado"]
)

spark.sql(f"DROP TABLE IF EXISTS {TABLA_LATENCIA}")

(
    df_latencia
    .write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable(TABLA_LATENCIA)
)

display(df_latencia.orderBy("operacion", "formato"))
    """)


def cargar_tabla_analitica():
    return code("""
# Crear tabla analitica para resolver el taller.
# Si el entorno no permite saveAsTable, el DataFrame df queda disponible desde Parquet.
df = spark.read.parquet(PARQUET_PATH)

spark.sql(f"DROP TABLE IF EXISTS {TABLA_ANALITICA}")

(
    df
    .write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable(TABLA_ANALITICA)
)

df = spark.table(TABLA_ANALITICA)
print("Tabla analitica lista:", TABLA_ANALITICA)
print("Filas disponibles:", df.count())
display(df.limit(5))
    """)


def plot_helpers():
    return code("""
# Helpers de visualizacion.
# Solo convierten a Pandas resultados pequenos ya agregados: top 10, top 20
# o series mensuales resumidas. No se usan sobre la base completa.
import matplotlib.pyplot as plt

def barh_spark(df_resultado, x_col, y_col, titulo, xlabel):
    pdf = df_resultado.toPandas()
    plt.figure(figsize=(10, 5))
    plt.barh(pdf[y_col].astype(str), pdf[x_col])
    plt.gca().invert_yaxis()
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.show()

def line_spark(df_resultado, x_col, y_col, titulo, xlabel, ylabel):
    pdf = df_resultado.toPandas()
    plt.figure(figsize=(11, 5))
    plt.plot(pdf[x_col].astype(str), pdf[y_col], marker="o")
    plt.xticks(rotation=60)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()

def scatter_spark(df_resultado, x_col, y_col, titulo, xlabel, ylabel):
    pdf = df_resultado.toPandas()
    plt.figure(figsize=(9, 5))
    plt.scatter(pdf[x_col], pdf[y_col], alpha=0.75)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()
    """)


def solucion_1():
    return [
        section_header("8.1", "Pregunta 1 -- Concentracion territorial del gasto publico"),
        enunciado_original(1),
        md("""
## Que se busca

La pregunta mide si el valor contratado se concentra en pocos departamentos. Esta lectura es descriptiva: muestra concentracion territorial del registro, no prueba centralizacion causal del gasto.
        """),
        code("""
total_nacional = (
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .agg(F.sum("valor_contrato").alias("total"))
    .first()["total"]
)

p1_base = (
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .groupBy("departamento_norm")
    .agg(F.sum("valor_contrato").alias("valor_total"))
    .withColumn("porcentaje_total", F.col("valor_total") / F.lit(total_nacional) * F.lit(100.0))
)

ventana = Window.orderBy(F.desc("valor_total")).rowsBetween(Window.unboundedPreceding, Window.currentRow)

p1_top10 = (
    p1_base
    .withColumn("porcentaje_acumulado", F.sum("porcentaje_total").over(ventana))
    .orderBy(F.desc("valor_total"))
    .limit(10)
)

display(p1_top10)
barh_spark(p1_top10.orderBy(F.asc("valor_total")), "valor_total", "departamento_norm", "Top 10 departamentos por valor contratado", "Valor contratado")
        """),
        interp("concentracion territorial", [
            "La tabla se lee de mayor a menor valor contratado y permite ver cuanto aporta cada departamento al total.",
            "El porcentaje acumulado muestra si los primeros territorios concentran una parte dominante del registro.",
            "No podemos concluir todavia que haya inequidad territorial: se necesita comparar con poblacion, numero de entidades, presupuesto y cobertura institucional."
        ]),
    ]


def solucion_2():
    return [
        section_header("8.2", "Pregunta 2 -- Variabilidad por tipo de contrato"),
        enunciado_original(2),
        code("""
p2 = (
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .groupBy("tipo_contrato_norm")
    .agg(
        F.count("*").alias("n_contratos"),
        F.avg("valor_contrato").alias("valor_promedio"),
        F.stddev("valor_contrato").alias("desviacion"),
        F.sum("valor_contrato").alias("valor_total")
    )
    .filter(F.col("n_contratos") >= 20)
    .withColumn("cv", F.col("desviacion") / F.col("valor_promedio"))
    .orderBy(F.desc("cv"))
)

p2_top = p2.limit(15)
display(p2_top)
barh_spark(p2_top.orderBy(F.asc("cv")), "cv", "tipo_contrato_norm", "Coeficiente de variacion por tipo de contrato", "CV")
        """),
        interp("variabilidad por tipo", [
            "Un CV alto significa que dentro del mismo tipo de contrato hay montos muy heterogeneos.",
            "La variabilidad puede deberse a proyectos de escalas distintas, registros atipicos o problemas de calidad.",
            "No conviene comparar solo promedios: dos tipos pueden tener media similar pero dispersion muy diferente."
        ]),
    ]


def solucion_3():
    return [
        section_header("8.3", "Pregunta 3 -- Evolucion mensual de la contratacion"),
        enunciado_original(3),
        code("""
top_tipos = (
    df
    .filter(F.col("tipo_contrato_norm").isNotNull())
    .groupBy("tipo_contrato_norm")
    .count()
    .orderBy(F.desc("count"))
    .limit(3)
)

p3 = (
    df
    .filter(F.col("mes_anio").isNotNull())
    .join(top_tipos.select("tipo_contrato_norm"), on="tipo_contrato_norm", how="inner")
    .groupBy("mes_anio", "tipo_contrato_norm")
    .agg(F.count("*").alias("n_procesos"))
    .orderBy("mes_anio", "tipo_contrato_norm")
)

display(p3)

p3_total = (
    df
    .filter(F.col("mes_anio").isNotNull())
    .groupBy("mes_anio")
    .agg(F.count("*").alias("n_procesos"))
    .orderBy("mes_anio")
)
line_spark(p3_total, "mes_anio", "n_procesos", "Procesos publicados por mes", "Mes", "Numero de procesos")
        """),
        interp("evolucion mensual", [
            "La serie permite detectar meses con picos o caidas inusuales en publicacion de procesos.",
            "Un pico puede reflejar ciclos presupuestales, cambios normativos, cargues masivos o comportamiento real de contratacion.",
            "Antes de interpretar politicamente, verifica si la fecha corresponde a publicacion, adjudicacion u otra etapa del proceso."
        ]),
    ]


def solucion_4():
    return [
        section_header("8.4", "Pregunta 4 -- Proveedores dominantes"),
        enunciado_original(4),
        code("""
p4_base = (
    df
    .filter(
        F.col("proveedor_norm").isNotNull()
        & (F.col("proveedor_norm") != "")
        & F.col("valor_contrato").isNotNull()
        & (F.col("valor_contrato") > 0)
    )
)

proveedor_departamento = (
    p4_base
    .groupBy("proveedor_norm", "departamento_norm")
    .count()
)

w_prov = Window.partitionBy("proveedor_norm").orderBy(F.desc("count"))
dep_frecuente = (
    proveedor_departamento
    .withColumn("rn", F.row_number().over(w_prov))
    .filter(F.col("rn") == 1)
    .select("proveedor_norm", F.col("departamento_norm").alias("departamento_mas_frecuente"))
)

total_valor = p4_base.agg(F.sum("valor_contrato").alias("total")).first()["total"]

p4 = (
    p4_base
    .groupBy("proveedor_norm")
    .agg(
        F.sum("valor_contrato").alias("valor_total"),
        F.count("*").alias("n_contratos")
    )
    .join(dep_frecuente, on="proveedor_norm", how="left")
    .withColumn("porcentaje_total", F.col("valor_total") / F.lit(total_valor) * F.lit(100.0))
    .orderBy(F.desc("valor_total"))
)

p4_top20 = p4.limit(20)
display(p4_top20)
barh_spark(p4_top20.orderBy(F.asc("valor_total")), "valor_total", "proveedor_norm", "Top 20 proveedores por valor adjudicado", "Valor")
        """),
        interp("proveedores dominantes", [
            "La tabla muestra concentracion por proveedor, pero el nombre normalizado puede mezclar homonimos o variantes de identificacion.",
            "Un proveedor dominante no implica irregularidad por si mismo; puede estar asociado a contratos nacionales, salud, infraestructura o tecnologia.",
            "Para auditoria real se debe cruzar con NIT, objeto contractual, modalidad, entidad y vigencia."
        ]),
    ]


def solucion_5():
    return [
        section_header("8.5", "Pregunta 5 -- Duracion vs valor del contrato"),
        enunciado_original(5),
        code("""
top_departamentos_p5 = (
    df
    .filter(F.col("departamento_norm").isNotNull())
    .groupBy("departamento_norm")
    .count()
    .orderBy(F.desc("count"))
    .limit(10)
)

p5 = (
    df
    .filter(
        F.col("valor_contrato").isNotNull()
        & (F.col("valor_contrato") > 0)
        & F.col("categoria_duracion").isNotNull()
    )
    .join(top_departamentos_p5.select("departamento_norm"), on="departamento_norm", how="inner")
    .groupBy("categoria_duracion", "departamento_norm")
    .agg(
        F.avg("valor_contrato").alias("valor_promedio"),
        F.count("*").alias("n_contratos")
    )
    .orderBy("categoria_duracion", F.desc("valor_promedio"))
)

display(p5)
        """),
        interp("duracion vs valor", [
            "La tabla compara categorias de duracion dentro de los departamentos con mayor presencia en la muestra.",
            "Si los contratos largos tienen mayor promedio, eso es coherente con proyectos mas extensos, pero no siempre ocurre.",
            "Las unidades de duracion pueden estar mal registradas; por eso la conversion a dias debe leerse como aproximacion operativa."
        ]),
    ]


def solucion_6():
    return [
        section_header("8.6", "Pregunta 6 -- Efectividad por orden institucional"),
        enunciado_original(6),
        md("""
## Criterio de solucion del profesor

La efectividad se mide comparando el total de procesos publicados contra los procesos que aparecen como celebrados o adjudicados. La lectura se hace por orden institucional porque permite comparar niveles de gestion publica con categorias interpretables.
        """),
        code("""
p6_base = (
    df
    .filter(F.col("orden_norm").isNotNull() & (F.col("orden_norm") != ""))
    .withColumn(
        "estado_grupo",
        F.when(F.col("estado_norm").contains("CELEBR"), F.lit("Celebrado"))
         .when(F.col("estado_norm").contains("ADJUDIC"), F.lit("Celebrado"))
         .when(F.col("estado_norm").contains("CONTRATO"), F.lit("Celebrado"))
         .when(F.col("estado_norm").contains("DESIERT"), F.lit("Desierto"))
         .when(F.col("estado_norm").contains("CANCEL"), F.lit("Cancelado"))
         .otherwise(F.lit("Otro"))
    )
)

p6 = (
    p6_base
    .groupBy("orden_norm")
    .agg(
        F.count("*").alias("total_procesos"),
        F.sum(F.when(F.col("estado_grupo") == "Celebrado", 1).otherwise(0)).alias("celebrados"),
        F.sum(F.when(F.col("estado_grupo") == "Desierto", 1).otherwise(0)).alias("desiertos"),
        F.sum(F.when(F.col("estado_grupo") == "Cancelado", 1).otherwise(0)).alias("cancelados")
    )
    .withColumn("tasa_celebracion", F.col("celebrados") / F.col("total_procesos") * F.lit(100.0))
    .withColumn("tasa_fallidos", (F.col("desiertos") + F.col("cancelados")) / F.col("total_procesos") * F.lit(100.0))
    .filter(F.col("total_procesos") >= 20)
    .orderBy(F.desc("tasa_celebracion"))
)

p6_top = p6.limit(15)
display(p6_top)
barh_spark(
    p6_top.orderBy(F.asc("tasa_celebracion")),
    "tasa_celebracion",
    "orden_norm",
    "Tasa de celebracion o adjudicacion por orden institucional",
    "% celebrados o adjudicados"
)
        """),
        interp("efectividad por orden institucional", [
            "La tasa de celebracion compara procesos celebrados o adjudicados contra el total de procesos del orden institucional.",
            "La grafica se lee de menor a mayor en el eje vertical: barras mas largas indican mayor proporcion de procesos que llegaron a resultado contractual.",
            "La tasa de fallidos queda en la tabla como apoyo; si es baja o cero en la muestra, no conviene convertirla en el grafico principal."
        ]),
    ]


def solucion_7():
    return [
        section_header("8.7", "Pregunta 7 -- Contratacion directa vs licitacion"),
        enunciado_original(7),
        code("""
p7 = (
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .groupBy("modalidad_norm")
    .agg(
        F.count("*").alias("n_contratos"),
        F.avg("valor_contrato").alias("valor_promedio"),
        F.expr("percentile_approx(valor_contrato, 0.5)").alias("mediana_aprox"),
        F.sum("valor_contrato").alias("valor_total")
    )
    .filter(F.col("n_contratos") >= 20)
    .orderBy(F.desc("valor_total"))
)

p7_top = p7.limit(15)
display(p7_top)
barh_spark(p7_top.orderBy(F.asc("valor_promedio")), "valor_promedio", "modalidad_norm", "Valor promedio por modalidad", "Valor promedio")

p7_anual = (
    df
    .filter(F.col("anio").isNotNull() & F.col("modalidad_norm").isNotNull())
    .withColumn(
        "modalidad_grupo",
        F.when(F.col("modalidad_norm").contains("DIRECT"), F.lit("Contratacion directa"))
         .when(F.col("modalidad_norm").contains("LICIT"), F.lit("Licitacion"))
         .otherwise(F.lit("Otra"))
    )
    .groupBy("anio", "modalidad_grupo")
    .agg(F.count("*").alias("n_procesos"))
    .orderBy("anio", "modalidad_grupo")
)
display(p7_anual)
        """),
        interp("modalidades de contratacion", [
            "La mediana aproximada es util porque los valores de contratos suelen estar muy sesgados por contratos enormes.",
            "Comparar contratacion directa y licitacion requiere controlar por sector, objeto y tipo de contrato.",
            "La evolucion anual permite ver cambios de composicion, pero no identifica por si sola la causa institucional."
        ]),
    ]


def solucion_8():
    return [
        section_header("8.8", "Pregunta 8 -- Ranking de entidades contratantes"),
        enunciado_original(8),
        code("""
entidad_tipo = (
    df
    .filter(F.col("entidad_norm").isNotNull() & F.col("tipo_contrato_norm").isNotNull())
    .groupBy("entidad_norm", "tipo_contrato_norm")
    .count()
)

w_ent = Window.partitionBy("entidad_norm").orderBy(F.desc("count"))
tipo_mas_frecuente = (
    entidad_tipo
    .withColumn("rn", F.row_number().over(w_ent))
    .filter(F.col("rn") == 1)
    .select("entidad_norm", F.col("tipo_contrato_norm").alias("tipo_mas_frecuente"))
)

p8 = (
    df
    .filter(F.col("entidad_norm").isNotNull())
    .groupBy("entidad_norm", "departamento_norm")
    .agg(
        F.count("*").alias("total_procesos"),
        F.sum("valor_contrato").alias("valor_total"),
        F.avg("valor_contrato").alias("valor_promedio"),
        F.sum(F.when(F.col("estado_norm").contains("CELEBR") | F.col("estado_norm").contains("ADJUDIC"), 1).otherwise(0)).alias("procesos_celebrados")
    )
    .withColumn("tasa_celebracion", F.col("procesos_celebrados") / F.col("total_procesos") * F.lit(100.0))
    .join(tipo_mas_frecuente, on="entidad_norm", how="left")
    .orderBy(F.desc("total_procesos"))
)

p8_top15 = p8.limit(15)
display(p8_top15)
scatter_spark(p8_top15, "total_procesos", "valor_promedio", "Entidades: numero de procesos vs valor promedio", "Procesos", "Valor promedio")
        """),
        interp("ranking de entidades", [
            "Una entidad con muchos procesos no necesariamente es la que mas gasta por contrato.",
            "El valor promedio puede distorsionarse por pocos contratos extremos; revisa tambien total y mediana si el analisis lo exige.",
            "La tasa de celebracion depende de como SECOP registre estados y de si el proceso ya cerro."
        ]),
    ]


def solucion_9():
    return [
        section_header("8.9", "Pregunta 9 -- Deteccion de outliers economicos"),
        enunciado_original(9),
        code("""
stats_tipo = (
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .groupBy("tipo_contrato_norm")
    .agg(
        F.avg("valor_contrato").alias("media_tipo"),
        F.stddev("valor_contrato").alias("sigma_tipo"),
        F.count("*").alias("n_tipo")
    )
    .filter((F.col("n_tipo") >= 20) & F.col("sigma_tipo").isNotNull() & (F.col("sigma_tipo") > 0))
)

p9 = (
    df
    .filter(F.col("valor_contrato").isNotNull() & (F.col("valor_contrato") > 0))
    .join(stats_tipo, on="tipo_contrato_norm", how="inner")
    .withColumn("z_aprox", (F.col("valor_contrato") - F.col("media_tipo")) / F.col("sigma_tipo"))
    .filter(F.col("z_aprox") > 3)
    .select(
        "nombre_entidad",
        "departamento_norm",
        "tipo_contrato_norm",
        "valor_contrato",
        "media_tipo",
        "sigma_tipo",
        "z_aprox",
        "estado_norm"
    )
    .orderBy(F.desc("z_aprox"))
)

p9_top = p9.limit(25)
display(p9_top)

p9_dep = (
    p9
    .groupBy("departamento_norm")
    .agg(F.count("*").alias("n_outliers"))
    .orderBy(F.desc("n_outliers"))
    .limit(15)
)
barh_spark(p9_dep.orderBy(F.asc("n_outliers")), "n_outliers", "departamento_norm", "Outliers economicos por departamento", "Numero de outliers")
        """),
        interp("outliers economicos", [
            "Un outlier estadistico es un contrato muy alejado de la media de su tipo, no una acusacion.",
            "Puede ser un contrato legitimo de gran escala, un error de digitacion o una clasificacion demasiado amplia.",
            "La revision responsable exige mirar objeto contractual, entidad, proveedor, modalidad y documentos del proceso."
        ]),
    ]


def solucion_10():
    return [
        section_header("8.10", "Pregunta 10 bonus -- Heterogeneidad contractual"),
        enunciado_original(10),
        code("""
p10 = (
    df
    .filter(
        F.col("entidad_norm").isNotNull()
        & F.col("valor_contrato").isNotNull()
        & (F.col("valor_contrato") > 0)
    )
    .groupBy("entidad_norm", "departamento_norm", "orden_norm")
    .agg(
        F.count("*").alias("n_contratos"),
        F.avg("valor_contrato").alias("valor_promedio"),
        F.stddev("valor_contrato").alias("desviacion")
    )
    .filter((F.col("n_contratos") > 50) & F.col("desviacion").isNotNull())
    .withColumn("cv", F.col("desviacion") / F.col("valor_promedio"))
    .orderBy(F.desc("cv"))
)

p10_top20 = p10.limit(20)
display(p10_top20)
scatter_spark(p10_top20, "n_contratos", "cv", "Heterogeneidad contractual por entidad", "Numero de contratos", "CV")
        """),
        interp("heterogeneidad contractual", [
            "Un CV alto indica que una entidad registra contratos de montos muy diferentes entre si.",
            "Esto puede deberse a una mezcla normal de proyectos pequenos y grandes, o a problemas de calidad en valores.",
            "El indicador sirve para priorizar revision descriptiva; no debe presentarse como hallazgo sancionatorio."
        ]),
    ]


def seccion_operacionalizacion():
    return [
        section_header("10", "Delta Lake y Jobs -- llevar el flujo a operacion"),
        md("""
## Por que esta extension importa

Hasta aqui resolvimos el taller como una clase guiada. El siguiente paso profesional es convertir este flujo en un proceso repetible: que no dependa de ejecutar celdas manualmente, que registre cuando se descargaron los datos y que deje una tabla lista para consultas recurrentes.

La siguiente extension natural es operacionalizar este flujo: convertirlo en **Job**, parametrizar rutas, registrar fecha de descarga y dejar una tabla **Delta** lista para consultas recurrentes.

## Que es Delta Lake

**Delta Lake** es una capa transaccional sobre archivos Parquet. En Databricks, las tablas son Delta por defecto salvo que se indique otro formato. La idea importante para esta clase es:

| Formato | Para que sirve | Ventaja | Limite |
|---|---|---|---|
| CSV | Intercambio simple de datos | Facil de descargar y revisar | Texto pesado, no conserva tipos, lento de parsear |
| Parquet | Analitica columnar | Conserva tipos, comprime y lee columnas necesarias | No tiene por si solo historial transaccional de tabla |
| Delta | Tabla lakehouse sobre Parquet + log transaccional | ACID, metadatos, historial, `MERGE`, `UPDATE`, consultas recurrentes | Requiere trabajar como tabla o ruta Delta, no editar archivos internos manualmente |

En este taller, CSV sirve como aterrizaje inicial, Parquet ayuda a comparar latencia, y Delta es la forma recomendada para dejar una tabla final reutilizable.

## Por que Delta aparece como Parquet en algunos planes

Una confusion normal en Databricks es esta: el estudiante crea una tabla Delta, ejecuta `explain()` y ve una linea como `PhotonScan parquet`.

Eso no es una contradiccion. Delta Lake tiene dos capas:

1. **Archivos Parquet**: contienen los datos columnares.
2. **Log Delta**: contiene el historial de transacciones, versiones, metadatos y lista de archivos activos.

Cuando consultas una tabla Delta, Databricks consulta el log para saber que version leer y luego Photon escanea los archivos Parquet correspondientes. Por eso el plan fisico puede decir `parquet`, mientras que conceptualmente estas trabajando con una tabla Delta.

La diferencia pedagogica es:

- Si lees una carpeta Parquet suelta, Spark solo ve archivos.
- Si lees una tabla Delta, Spark ve una tabla con reglas de consistencia, historial y metadatos.
- Si un Job actualiza la tabla, Delta ayuda a que las lecturas no queden mezcladas con escrituras incompletas.

## Crear una tabla Delta final

Despues de limpiar SECOP, la tabla analitica puede guardarse asi:

```python
(
    df
    .write
    .mode("overwrite")
    .format("delta")
    .saveAsTable(f"{CATALOG}.{SCHEMA}.secop_base_analitica")
)
```

Luego se consulta desde otro notebook o Databricks SQL sin repetir descarga, parseo CSV ni limpieza:

```sql
SELECT orden_norm, COUNT(*) AS procesos, SUM(valor_contrato) AS valor_total
FROM workspace.default.secop_base_analitica
GROUP BY orden_norm
ORDER BY valor_total DESC;
```

## Como crear un Job en Databricks para este flujo

1. Abre el notebook final en Databricks.
2. Verifica que los parametros `CATALOG`, `SCHEMA`, `VOLUME` y `MODO_EJECUCION` esten correctos.
3. Haz clic en **Schedule** o ve a **Jobs & Pipelines**.
4. Crea un **Job** con una tarea de tipo **Notebook**.
5. Selecciona este notebook como tarea.
6. En compute, usa serverless si esta disponible para tu workspace.
7. Define parametros del task si el workspace los permite: catalogo, schema, volume, modo y fecha de descarga.
8. Ejecuta **Run now** una vez y revisa Query Profile.
9. Si la corrida es correcta, programa la frecuencia o dejalo como ejecucion manual controlada.
10. Registra en una tabla de metadatos la fecha de descarga, modo y rutas usadas.

## Que debe quedar al final de un Job correcto

- CSV descargado o disponible en Volume.
- Parquet de trabajo actualizado.
- Tabla Delta `secop_base_analitica` lista.
- Metadatos de ejecucion guardados.
- Resultados consultables sin repetir todo el flujo manualmente.

## Que cambia al operacionalizar

| En clase | En operacion |
|---|---|
| Ejecutamos celdas manualmente | Un Job ejecuta el notebook con parametros |
| Cambiamos rutas editando codigo | Las rutas vienen de widgets o parametros |
| Sabemos informalmente cuando descargamos | Guardamos fecha de descarga y modo de ejecucion |
| Usamos DataFrames temporales | Dejamos tablas Delta consultables |
| Revisamos resultados en pantalla | Creamos salidas reproducibles para dashboards o informes |

## Parametros minimos recomendados

- `catalog`: catalogo de Unity Catalog.
- `schema`: esquema de trabajo.
- `volume`: Volume donde viven los archivos.
- `modo_ejecucion`: `modo_demo`, `modo_clase` o `modo_completo`.
- `fecha_descarga`: fecha en la que se descargaron los datos SECOP.
- `tabla_salida`: tabla Delta final para consultas.

## Resultado esperado

Al final de una version operacional, el estudiante deberia poder abrir Databricks SQL o un notebook nuevo y consultar:

```sql
SELECT departamento_norm, SUM(valor_contrato) AS valor_total
FROM workspace.default.secop_base_analitica
GROUP BY departamento_norm
ORDER BY valor_total DESC
LIMIT 10;
```

## Advertencia docente

Operacionalizar no significa volver mas complejo el notebook por gusto. Significa quitar decisiones manuales repetidas, registrar contexto y reducir el riesgo de que dos grupos obtengan resultados distintos por rutas, fechas o modos de ejecucion no documentados.
        """),
        code("""
# Ejemplo de metadatos para una version operacional.
# En un Job real, estos valores pueden venir de widgets o parametros del task.
from datetime import datetime

metadata_ejecucion = spark.createDataFrame(
    [(
        CATALOG,
        SCHEMA,
        VOLUME,
        MODO_EJECUCION,
        RAW_CSV_PATH,
        PARQUET_PATH,
        datetime.now().isoformat(timespec="seconds")
    )],
    [
        "catalog",
        "schema",
        "volume",
        "modo_ejecucion",
        "raw_csv_path",
        "parquet_path",
        "fecha_registro"
    ]
)

display(metadata_ejecucion)

# Si tu workspace permite tablas Delta, puedes guardar este registro asi:
# metadata_ejecucion.write.mode("append").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.secop_metadata_ejecucion")
        """),
        interp("operacionalizacion", [
            "Registrar metadatos ayuda a explicar por que dos ejecuciones pueden tener resultados distintos.",
            "Un Job reduce errores manuales cuando el flujo se repite cada semana o cada cohorte.",
            "Una tabla Delta final permite que otros notebooks, dashboards o consultas SQL reutilicen el resultado sin repetir toda la limpieza."
        ]),
    ]


def seccion_rubrica_operacional():
    return [
        section_header("9", "Como leer la ejecucion interna de Spark"),
        md("""
## Como leer esta seccion

Esta seccion no es una rubrica. Es una guia para que el estudiante aprenda a leer que hace Spark cuando ejecuta una solucion: que parte lee datos, que parte agrupa, que parte ordena y donde puede aparecer costo innecesario.

## Como lee Spark una solucion

- Una **transformation** como `select`, `filter` o `withColumn` construye un plan; todavia no ejecuta el trabajo completo.
- Una **action** como `count`, `display`, `write`, `first` o `toPandas` dispara un **Job**.
- Un **Job** puede dividirse en **Stages** cuando aparece un limite de intercambio de datos, por ejemplo un `groupBy`, `orderBy`, `join` o una ventana.
- Cada **Stage** se divide en **Tasks**, que procesan particiones de los datos.
- Un **shuffle** ocurre cuando Spark debe redistribuir datos entre workers, por ejemplo para agrupar por departamento o ordenar por valor.
- En Databricks serverless, el lugar recomendado para observar esto es **Query Profile**, complementado por `explain()`.

Por eso una respuesta excelente no solo calcula: reduce lectura, usa Parquet, evita acciones repetidas, agrega antes de graficar y explica las limitaciones del resultado.

## Como se lee un Physical Plan real

Ejemplo observado en esta clase:

```text
== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- == Initial Plan ==
   PhotonResultStage
   +- PhotonColumnarToRow
      +- PhotonTopK(sortOrder=[valor_total DESC NULLS LAST])
         +- PhotonGroupingAgg(keys=[departamento_norm], functions=[sum(valor_contrato)])
            +- PhotonScan parquet workspace.default.secop_base_analitica[
               departamento_norm, valor_contrato
            ] DataFilters: [isnotnull(valor_contrato), (valor_contrato > 0.0)]

== Photon Explanation ==
The query is fully supported by Photon.
```

Lectura docente:

| Linea del plan | Como se interpreta |
|---|---|
| `AdaptiveSparkPlan isFinalPlan=false` | Spark usa Adaptive Query Execution. El plan puede ajustarse durante la ejecucion segun estadisticas reales. |
| `PhotonResultStage` | Databricks ejecuta esta parte con Photon, su motor vectorizado. Buena senal: la consulta entra al camino optimizado. |
| `PhotonColumnarToRow` | Internamente trabaja columnar, pero convierte filas para entregar resultado al notebook. |
| `PhotonTopK(sortOrder=[valor_total DESC])` | El `orderBy(...).limit(...)` se optimiza como Top K: Spark no necesita ordenar absolutamente todo si solo pide el top. |
| `PhotonGroupingAgg(keys=[departamento_norm], functions=[sum(...)])` | Hay una agregacion por departamento. Esta operacion suele implicar redistribucion o combinacion de particiones. |
| `PhotonScan parquet ... [departamento_norm, valor_contrato]` | Spark lee los archivos Parquet fisicos. Si la fuente es una tabla Delta, Delta primero usa su log transaccional para decidir que archivos Parquet son la version valida. |
| `DataFilters` y `DictionaryFilters` | El filtro `valor_contrato > 0` se empuja hacia la lectura. Spark evita procesar parte de los datos inutiles. |
| `ReadSchema` | Muestra las columnas leidas realmente. Si aparecen 50 columnas para una pregunta que usa 2, hay una oportunidad de optimizacion. |
| `The query is fully supported by Photon` | La consulta evita rutas lentas como UDF Python y puede ejecutarse con el motor optimizado de Databricks. |

Lectura clave: **Delta Lake es log + Parquet**. En el plan fisico puedes ver `parquet` porque ese es el formato de archivo que Photon escanea. La diferencia frente a leer una carpeta Parquet suelta es que Delta mantiene metadatos de tabla, control transaccional, historial y consistencia entre escrituras y lecturas.

## Que significa "usar UDF Python para limpieza simple"

Una UDF Python es una funcion escrita por el usuario que Spark no entiende internamente con el mismo nivel de detalle que una expresion nativa. Por ejemplo, esto es una mala idea para limpiar valores simples:

```python
def limpiar_valor(x):
    return float(str(x).replace("$", "").replace(",", ""))

# Mala practica para este caso: Spark debe llamar Python fila por fila.
```

Para este cuaderno es mejor:

```python
F.expr("try_cast(regexp_replace(cast(valor_total_adquisicion as string), '[^0-9.-]', '') as double)")
```

La version nativa permite que Catalyst y Photon optimicen el plan. La UDF puede sacar parte del trabajo del camino optimizado, dificultar el `pushdown`, complicar el plan y volver mas costosa la ejecucion.

## Window: ejemplo visual y por que cuesta en Pandas

En la pregunta de concentracion territorial usamos una ventana para calcular porcentaje acumulado:

```python
ventana = Window.orderBy(F.desc("valor_total")).rowsBetween(Window.unboundedPreceding, Window.currentRow)

p1_base.withColumn(
    "porcentaje_acumulado",
    F.sum("porcentaje_total").over(ventana)
)
```

Visualmente:

| Departamento | % del total | % acumulado |
|---|---:|---:|
| A | 30 | 30 |
| B | 20 | 50 |
| C | 10 | 60 |

Spark lo interpreta como una operacion de ventana: debe respetar un orden y calcular un acumulado. Eso puede introducir `Sort` y operaciones por particion.

En Pandas se haria con algo como:

```python
pdf = pdf.sort_values("valor_total", ascending=False)
pdf["porcentaje_acumulado"] = pdf["porcentaje_total"].cumsum()
```

Eso es simple si el resultado ya es pequeno. La dificultad aparece si intentas hacer ese acumulado sobre millones de filas antes de agregar: Pandas necesita tener los datos en memoria del driver. En Spark, la regla pedagogica es: **agrega primero, reduce el resultado y despues calcula ventanas o graficas sobre una tabla pequeña**.

## Lectura docente del rendimiento

En este taller conviene revisar tres preguntas en Query Profile:

- Pregunta 1: muestra `groupBy` por departamento, `sum` de valor y una ventana acumulada.
- Pregunta 4: muestra agregacion por proveedor y una ventana para seleccionar el departamento mas frecuente.
- Pregunta 7: muestra percentiles aproximados, conteos y evolucion anual por modalidad.

El objetivo no es que el estudiante memorice todos los operadores, sino que pueda reconocer tres señales: lectura de columnas, shuffles por agregacion y ordenamientos por rankings.
        """),
        code("""
# Diagnostico operacional opcional con explain()
# Estas llamadas no ejecutan una accion de conteo ni escritura; muestran el plan
# que Spark prepararia. En Databricks serverless, complementa esto con Query Profile
# cuando ejecutes una accion como display(), count() o write().

print("PLAN 1: groupBy con posible shuffle")
(
    df
    .filter(F.col("valor_contrato") > 0)
    .groupBy("departamento_norm")
    .agg(F.sum("valor_contrato").alias("valor_total"))
    .explain()
)

print("\\nPLAN 2: orderBy + limit")
(
    df
    .filter(F.col("valor_contrato") > 0)
    .groupBy("proveedor_norm")
    .agg(F.sum("valor_contrato").alias("valor_total"))
    .orderBy(F.desc("valor_total"))
    .limit(20)
    .explain()
)

print("\\nPLAN 3: lectura Parquet con seleccion de columnas")
(
    spark.read.parquet(PARQUET_PATH)
    .select("departamento_norm", "valor_contrato", "anio")
    .filter(F.col("anio") >= 2024)
    .explain()
)
        """),
        interp("lectura operacional de Spark", [
            "Un buen resultado numerico puede ser una mala solucion si obliga a Spark a leer, mover o materializar datos innecesariamente.",
            "Jobs, Stages y Tasks no son conceptos decorativos: ayudan a ubicar cuando el costo viene de lectura, shuffle, ordenamiento o escritura.",
            "La optimizacion aqui no busca trucos avanzados; busca decisiones claras: leer menos, limpiar una vez, agregar en Spark y graficar solo resumenes."
        ]),
    ]


def build_cells():
    cells = [
        *uce_header(
            title="Solucion del taller SECOP con Spark en Databricks",
            session=11,
            github_path="main/Cuadernos/11_Spark_SECOP_Solucion_Taller.ipynb",
            nota_plataforma=(
                "Databricks Free/Community 2026 con compute serverless. "
                "El cuaderno usa Volumes, Parquet, Spark SQL y DataFrames; no depende de rutas locales del repo."
            ),
        ),
        md("""
## Proposito pedagogico

Esta sesion retoma el taller SECOP trabajado con Dask y lo resuelve con Spark en Databricks. La idea no es decir que Spark siempre es mejor, sino aprender a ordenar un flujo de procesamiento cuando la base puede acercarse a 20 GB y no conviene trabajar como si todo cupiera comodamente en memoria.

El cuaderno esta pensado para ejecutarse dentro de Databricks, en un entorno aislado del repositorio. Por eso no usa rutas como `C:\\Users\\...` ni `Cuadernos/datos/...` como fuente obligatoria. Los CSV deben estar dentro de un Volume o en una tabla del workspace.

## Alcance de la sesion

- Preparar datos SECOP en Databricks Volumes.
- Descargar chunks SECOP desde datos.gov.co si el Volume esta vacio.
- Comparar latencia entre leer CSV y leer Parquet usando la misma muestra.
- Crear una tabla analitica reducida para no reprocesar 20 GB innecesariamente.
- Resolver las 10 preguntas del taller original con Spark.
- Reconocer malas practicas frecuentes y formas mas optimas de ordenar el trabajo.

## Agenda sugerida

1. Contexto: del taller Dask a una solucion Spark.
2. Restricciones reales de Databricks y de una base cercana a 20 GB.
3. Preparacion o descarga de datos en Volumes.
4. CSV vs Parquet: lectura, conversion y latencia.
5. Tabla analitica SECOP.
6. Orden correcto de procesamiento en Spark.
7. Solucion completa de las 10 preguntas.
8. Ejecucion operacional, Delta Lake, Jobs y cierre.

## Por que importa

En datos publicos grandes, el problema no es solo escribir una consulta que funcione. Tambien importa donde viven los archivos, cuantas columnas se leen, cuantas veces se parsea CSV, cuando se dispara una accion y que parte del resultado se lleva al driver para graficar.
        """),
        toc([
            "0. Correspondencia con el taller Dask original",
            "1. Preparar Databricks y Volumes",
            "2. Parametros del cuaderno",
            "3. Descargar o leer CSV crudo y crear base reducida",
            "4. CSV vs Parquet: diferencia de latencia",
            "5. Tabla analitica y orden de procesamiento",
            "6. Malas practicas y alternativas en Spark",
            "7. Mini fichas de funciones",
            "8. Solucion completa del taller",
            "9. Como leer la ejecucion interna de Spark",
            "10. Delta Lake y Jobs: operacionalizacion",
            "11. Cierre y referencias",
        ]),
        section_header("0", "Correspondencia con el taller Dask original"),
        md("""
| Taller Dask original | Solucion Spark en esta sesion |
|---|---|
| Descarga paralela por chunks | Carga de CSV en Databricks Volumes y lectura distribuida con Spark |
| Dask lee varios CSV como particiones | Spark lee archivos desde Volume y los convierte a Parquet |
| Diagnostico de calidad con Pandas/Dask | Limpieza tipada con funciones nativas de Spark |
| 10 preguntas analiticas | Las mismas 10 preguntas resueltas con DataFrames/Spark SQL |
| Evaluacion del taller Dask | Criterios adaptados a ejecucion, calidad y optimizacion en Spark |

No se elimina el taller Dask: este cuaderno es la solucion equivalente en Spark y Databricks.
        """),
        section_header("1", "Preparar Databricks y Volumes"),
        md("""
## Definicion formal

Un **Volume** de Unity Catalog es una ubicacion gobernada para guardar archivos no tabulares dentro de Databricks. Sirve para almacenar CSV, Parquet, JSON, imagenes u otros archivos que luego pueden ser leidos por Spark.

## Intuicion

Piensa en un Volume como una carpeta administrada por Databricks. No es el disco de tu computador y no es una carpeta del repositorio. Si el notebook corre en Databricks, Spark solo ve lo que esta accesible dentro del workspace, tablas, Volumes o ubicaciones externas autorizadas.

## Preparacion esperada

1. Crea o identifica un catalogo, un esquema y un Volume.
2. Para que todos los estudiantes lo repliquen igual, crea o usa el Volume `workspace.default.tallerspark`.
3. Sube los CSV del SECOP a una ruta como:

`/Volumes/<catalog>/<schema>/<volume>/secop/raw_csv/`

4. Para este workspace, la ruta esperada queda:

`/Volumes/workspace/default/tallerspark/secop/raw_csv/`

5. Si no tienes archivos, el cuaderno incluye una celda para descargar chunks desde datos.gov.co hacia esa ruta.
6. Este cuaderno convertira esos CSV a Parquet en:

`/Volumes/<catalog>/<schema>/<volume>/secop/parquet/`

## Advertencia docente

La base completa puede acercarse a 20 GB en CSV. En Databricks Free/serverless eso puede chocar con cuotas, tiempo de ejecucion y limites del workspace. Por eso el modo por defecto es `modo_clase`: se prueba con muestra o chunks controlados, y luego se escala con criterio.
        """),
        codigo_base_librerias(),
        section_header("2", "Parametros del cuaderno"),
        parametros_databricks(),
        verificar_volume(),
        section_header("3", "Descargar o leer CSV crudo y crear base reducida"),
        md("""
## Si el Volume esta vacio

En Spark/Databricks no hay archivos por defecto. Primero deben existir CSV en una ruta que el workspace pueda ver. Este cuaderno ofrece dos caminos:

1. **Descarga desde datos.gov.co hacia el Volume**: util si el workspace permite salida a internet.
2. **Carga manual por la interfaz de Databricks**: util si el entorno Free/serverless bloquea la descarga externa.

El modo por defecto `modo_clase` descarga tres chunks de 100.000 filas. El modo completo queda disponible, pero no se recomienda activarlo sin revisar cuota, tiempo y almacenamiento.
        """),
        descargar_secop_a_volume(),
        md("""
## Por que no leer todo sin pensar

CSV es un formato de texto. Para analizarlo, Spark debe leer texto, separar columnas, aplicar tipos y convertir valores. Si repetimos ese trabajo en cada pregunta, desperdiciamos tiempo y cuota.

La primera optimizacion no es sofisticada: leer solo lo necesario, limpiar una vez y escribir una version analitica en Parquet. Ese Parquet es el primer salto: pasamos de texto crudo a archivos columnares tipados.

Luego viene Delta Lake. Delta no reemplaza la idea de Parquet: la organiza como tabla. Una tabla Delta se guarda sobre archivos Parquet, pero agrega un registro transaccional (`_delta_log`) para saber que archivos pertenecen a la version valida de la tabla, que cambios se hicieron y como leerla de forma consistente.

Por eso en este cuaderno veras dos niveles:

| Nivel | Que representa | Para que lo usamos aqui |
|---|---|---|
| CSV crudo | Datos descargados como texto | Entrada inicial desde datos.gov.co |
| Parquet | Datos limpios en formato columnar | Comparar latencia y evitar parsear CSV repetidamente |
| Delta Lake | Tabla gobernada sobre Parquet + log transaccional | Dejar una tabla final consultable, reproducible y lista para Jobs |

Cuando Databricks muestra `PhotonScan parquet` sobre una tabla Delta, no significa que Delta desaparecio. Significa que el motor fisico esta leyendo los archivos Parquet que componen la tabla Delta, usando el log Delta para saber cuales son validos.
        """),
        leer_csv_y_reducir(),
        crear_base_analitica(),
        ficha("regexp_replace()", "limpia caracteres no numericos antes de convertir texto a numero.", "columna y patron regular.", "una columna transformada.", "si el resultado queda vacio, debe combinarse con `try_cast` para evitar errores ANSI."),
        ficha("try_cast()", "convierte valores malformados en NULL en lugar de romper la ejecucion.", "expresion de texto y tipo destino.", "un valor convertido o NULL.", "es clave en Spark 4 cuando hay cadenas vacias, textos o fechas invalidas."),
        section_header("4", "CSV vs Parquet: diferencia de latencia y por que importa"),
        md("""
## Definicion formal

**CSV** es un formato de texto separado por delimitadores. **Parquet** es un formato columnar binario que preserva tipos, usa compresion y permite leer solo columnas necesarias.

## Intuicion en palabras

CSV es facil de compartir, pero costoso de analizar repetidamente. Parquet es menos legible a simple vista, pero esta pensado para motores analiticos como Spark.

## Ejemplo pequeno manual

Si una consulta solo necesita `departamento` y `valor_contrato`, un CSV obliga a revisar lineas de texto completas. En Parquet, Spark puede leer de forma mas selectiva las columnas necesarias y evitar parte del parseo.

## Advertencia

La comparacion de latencia depende del tamano de muestra, del estado del compute serverless, de la cuota, de archivos pequenos y de optimizaciones internas. No la leas como benchmark universal; leela como evidencia pedagogica del costo de repetir CSV frente a trabajar con un formato analitico.
        """),
        escribir_parquet(),
        comparar_latencia(),
        interp("CSV vs Parquet", [
            "Si Parquet sale mas rapido, la razon principal suele ser que evita parsear texto repetidamente y preserva tipos.",
            "Si la diferencia es pequena, puede deberse a muestra pequena, calentamiento del compute o a que la operacion no lee muchas columnas.",
            "La conclusion practica es convertir temprano a Parquet o Delta cuando el flujo tendra varias preguntas analiticas."
        ]),
        section_header("5", "Tabla analitica y orden de procesamiento"),
        cargar_tabla_analitica(),
        md("""
## Orden recomendado en Spark

1. Leer archivos desde Volume o tabla.
2. Seleccionar columnas minimas.
3. Convertir tipos con funciones nativas.
4. Normalizar texto.
5. Filtrar registros invalidos solo cuando el analisis lo justifique.
6. Escribir Parquet una vez para evitar parseo repetido; escribir Delta una vez para dejar una tabla final con historial transaccional.
7. Resolver preguntas con agregaciones.
8. Convertir a Pandas solo resultados pequenos para graficar.

## Que no podemos concluir todavia

Que un resultado sea rapido en muestra no garantiza el mismo tiempo en la base completa. La escala cambia el costo de lectura, shuffle, escritura y visualizacion.
        """),
        section_header("6", "Malas practicas y alternativas en Spark"),
        md("""
| Mala practica | Por que duele | Alternativa recomendada |
|---|---|---|
| Leer todos los campos del CSV en cada pregunta | Repite parseo y aumenta bytes leidos | Crear `secop_base_analitica` |
| Inferir schema siempre sobre 20 GB | Recorre datos para deducir tipos y puede mezclar tipos incompatibles entre chunks | Leer CSV como texto estable y convertir una vez con `try_cast` |
| Llevar toda la base al driver | Puede romper memoria y cuota | Agregar en Spark y graficar top/resumen |
| Usar UDF Python para limpieza simple | Sale del camino mas optimizable | Usar funciones nativas de Spark |
| Repetir acciones innecesarias | Cada accion puede disparar ejecucion | Agrupar calculos y materializar resultados utiles |
| No mirar el plan | No ves scans, shuffles ni cuellos de botella | Usar `explain()` y Query Profile |
| Escribir muchos archivos pequenos | Lentitud por sobrecarga de metadatos | Controlar particiones de salida cuando aplique |

En serverless, recuerda que la Spark UI clasica no esta disponible. Usa **Query Profile** para inspeccionar consultas, scans, shuffles y tiempos.
        """),
        code("""
# Ejemplo pedagogico: leer el plan fisico sin ejecutar una accion costosa.
(
    df
    .filter(F.col("valor_contrato") > 0)
    .groupBy("departamento_norm")
    .agg(F.sum("valor_contrato").alias("valor_total"))
    .orderBy(F.desc("valor_total"))
    .limit(10)
    .explain()
)
        """),
        section_header("7", "Mini fichas de funciones clave"),
        ficha("spark.read.csv()", "lee archivos CSV desde una ruta accesible por Spark.", "`header=True`, `inferSchema=False`, `multiLine=True`, `escape` y ruta del Volume.", "un DataFrame distribuido con columnas inicialmente textuales.", "la lectura puede ser costosa porque CSV es texto; por eso se tipa una vez y se guarda en Parquet/Delta."),
        ficha("DataFrame.write.parquet()", "escribe un DataFrame como archivos Parquet.", "modo de escritura y ruta destino.", "archivos Parquet en el Volume.", "sirve para no repetir parseo CSV en cada analisis; es formato de archivo, no una tabla transaccional por si solo."),
        ficha("DataFrame.write.format('delta').saveAsTable()", "guarda un DataFrame como tabla Delta administrada por Databricks.", "formato `delta`, modo de escritura, `overwriteSchema` y nombre de tabla.", "una tabla consultable con Spark SQL y Databricks SQL.", "Delta usa archivos Parquet mas un log transaccional; por eso puedes ver `parquet` en el plan fisico aunque consultes una tabla Delta."),
        ficha("groupBy().agg()", "agrupa filas y calcula metricas agregadas.", "columnas de grupo y expresiones como sum, avg o count.", "un DataFrame resumido.", "cada fila resultante representa un grupo."),
        ficha("percentile_approx()", "calcula percentiles aproximados de forma escalable.", "columna numerica y percentil.", "un valor aproximado por grupo.", "es preferible a medianas exactas costosas en grandes datos."),
        ficha("Window", "define ventanas para acumulados, rankings o calculos por particion.", "orden o particion de filas.", "una especificacion usada por funciones analiticas.", "permite calcular acumulados sin sacar datos de Spark."),
        section_header("8", "Solucion completa del taller"),
        md("""
Cada pregunta conserva los criterios originales de evaluacion: limpieza, uso correcto de Spark, correctitud, visualizacion e interpretacion. Las graficas se hacen sobre resultados pequenos ya agregados.
        """),
        plot_helpers(),
    ]
    for builder in [
        solucion_1,
        solucion_2,
        solucion_3,
        solucion_4,
        solucion_5,
        solucion_6,
        solucion_7,
        solucion_8,
        solucion_9,
        solucion_10,
    ]:
        cells.extend(builder())

    cells.extend([
        *seccion_rubrica_operacional(),
        *seccion_operacionalizacion(),
        section_header("11", "Cierre de sesion"),
        md("""
## Recapitulacion

En esta sesion convertimos el taller SECOP a una solucion Spark pensada para Databricks moderno. La clave fue no depender del repositorio local, preparar datos en Volumes, convertir CSV a Parquet, crear una tabla analitica reducida y resolver las 10 preguntas con funciones nativas.

## Idea mas importante

Spark no arregla automaticamente un mal orden de trabajo. El rendimiento mejora cuando lees menos, limpias una vez, escribes en formato analitico y solo llevas al driver resultados pequenos.

## Errores comunes

- Tratar Databricks como si viera el disco local.
- Repetir lectura CSV en cada analisis.
- Convertir toda la base a Pandas para graficar.
- Usar funciones Python fila a fila para limpieza que Spark puede hacer nativamente.
- Interpretar outliers o concentracion como prueba de irregularidad.

## Proxima sesion

En la proxima sesion se puede tomar la extension anterior y convertirla en un Job completo con parametros, calendario de ejecucion, tabla Delta final y bitacora de descargas.

## Referencias

- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Databricks serverless limitations: https://docs.databricks.com/aws/en/compute/serverless/limitations
- Databricks Volumes: https://docs.databricks.com/en/volumes/
- Serverless notebooks y Query Profile: https://docs.databricks.com/en/compute/serverless/notebooks.html
- Spark SQL performance tuning: https://spark.apache.org/docs/latest/sql-performance-tuning.html
- PySpark functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html
- Datos SECOP II: https://www.datos.gov.co/resource/p6dx-8zbt.csv
        """),
    ])
    return cells


if __name__ == "__main__":
    cells = build_cells()
    validate(cells)
    save(cells, "Cuadernos/11_Spark_SECOP_Solucion_Taller.ipynb")

