# -*- coding: utf-8 -*-
"""
Genera Cuadernos/12_MongoDB_Atlas_NoSQL_Moderno.ipynb

Sesion 12: MongoDB Atlas, NoSQL documental y analitica moderna.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, sh, save, validate, uce_header, toc, section_header


OUTPUT = "Cuadernos/12_MongoDB_Atlas_NoSQL_Moderno.ipynb"


def interp(titulo, puntos):
    return md(
        "### Interpretacion docente -- " + titulo + "\n\n"
        + "\n".join(f"- {p}" for p in puntos)
    )


def ficha(nombre, sirve, parametros, devuelve, interpreta):
    return md(f"""
### Mini ficha: `{nombre}`

| Elemento | Explicacion |
|---|---|
| Funcion o concepto | `{nombre}` |
| Para que sirve | {sirve} |
| Parametros usados | {parametros} |
| Que devuelve | {devuelve} |
| Como interpretar la salida | {interpreta} |
    """)


def install_cell():
    return code('''
# Instalacion liviana para Colab o entornos sin PyMongo.
# En un entorno local/Anaconda ya configurado, esta celda puede no hacer nada.
import importlib.util
import sys
import subprocess

paquetes = []
if importlib.util.find_spec("pymongo") is None:
    paquetes.append("pymongo")
if importlib.util.find_spec("pandas") is None:
    paquetes.append("pandas")

if paquetes:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *paquetes])

print("Entorno Python listo para MongoDB.")
    ''')


def connection_cell():
    return code('''
import os
from getpass import getpass
from pprint import pprint
from datetime import datetime, timezone

import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING, GEOSPHERE
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure


ATLAS_URI = os.environ.get("MONGODB_URI")

if not ATLAS_URI:
    try:
        valor = getpass(
            "Pega MONGODB_URI de Atlas Free o deja vacio para intentar Docker local: "
        ).strip()
        ATLAS_URI = valor or None
    except Exception:
        ATLAS_URI = None

DOCKER_URIS = [
    "mongodb://admin:admin123@localhost:27017/?authSource=admin",
    "mongodb://admin:admin123@mongo:27017/?authSource=admin",
]


def conectar(uri, etiqueta):
    cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
    cliente.admin.command("ping")
    print(f"Conexion activa: {etiqueta}")
    return cliente, etiqueta


client = None
conexion_origen = None
errores = []

if ATLAS_URI:
    try:
        client, conexion_origen = conectar(ATLAS_URI, "Atlas Free")
    except Exception as exc:
        errores.append(("Atlas Free", str(exc)[:500]))

if client is None:
    for uri in DOCKER_URIS:
        try:
            client, conexion_origen = conectar(uri, "Docker local")
            break
        except Exception as exc:
            errores.append((uri, str(exc)[:300]))

if client is None:
    print("No se logro conectar ni a Atlas ni a Docker local.")
    print("Errores observados:")
    for fuente, detalle in errores:
        print("-", fuente, "=>", detalle)
    raise RuntimeError(
        "Configura MONGODB_URI para Atlas o levanta Docker con: "
        "docker compose --profile nosql up -d"
    )

print("Origen usado:", conexion_origen)
print("Bases disponibles visibles:", client.list_database_names()[:10])
    ''')


def seed_cell():
    return code('''
# Seed de respaldo para Docker local o para una base de practica en Atlas.
# No borra bases de ejemplo de Atlas. Solo reemplaza colecciones demo del curso.

db_demo = client["bigdata_course"]

restaurants_demo = [
    {
        "name": "Brunos On The Boulevard",
        "borough": "Queens",
        "cuisine": "American",
        "address": {
            "street": "Astoria Boulevard",
            "zipcode": "11369",
            "coord": [-73.8803827, 40.7643124],
        },
        "location": {"type": "Point", "coordinates": [-73.8803827, 40.7643124]},
        "grades": [
            {"date": datetime(2024, 11, 15, tzinfo=timezone.utc), "grade": "A", "score": 10},
            {"date": datetime(2025, 5, 20, tzinfo=timezone.utc), "grade": "B", "score": 22},
        ],
    },
    {
        "name": "La Esquina",
        "borough": "Manhattan",
        "cuisine": "Mexican",
        "address": {
            "street": "Kenmare Street",
            "zipcode": "10012",
            "coord": [-73.9974, 40.7216],
        },
        "location": {"type": "Point", "coordinates": [-73.9974, 40.7216]},
        "grades": [
            {"date": datetime(2025, 1, 9, tzinfo=timezone.utc), "grade": "A", "score": 8},
            {"date": datetime(2025, 8, 9, tzinfo=timezone.utc), "grade": "A", "score": 7},
        ],
    },
    {
        "name": "Bogota Coffee Lab",
        "borough": "Brooklyn",
        "cuisine": "Colombian",
        "address": {
            "street": "Bogart Street",
            "zipcode": "11206",
            "coord": [-73.9341, 40.7051],
        },
        "location": {"type": "Point", "coordinates": [-73.9341, 40.7051]},
        "grades": [
            {"date": datetime(2024, 9, 1, tzinfo=timezone.utc), "grade": "A", "score": 5},
            {"date": datetime(2025, 2, 1, tzinfo=timezone.utc), "grade": "A", "score": 6},
        ],
    },
    {
        "name": "Queens Dumpling House",
        "borough": "Queens",
        "cuisine": "Chinese",
        "address": {
            "street": "Main Street",
            "zipcode": "11354",
            "coord": [-73.8303, 40.7590],
        },
        "location": {"type": "Point", "coordinates": [-73.8303, 40.7590]},
        "grades": [
            {"date": datetime(2023, 6, 1, tzinfo=timezone.utc), "grade": "B", "score": 21},
            {"date": datetime(2025, 3, 1, tzinfo=timezone.utc), "grade": "A", "score": 11},
        ],
    },
]

movies_demo = [
    {
        "title": "The Matrix",
        "year": 1999,
        "genres": ["Action", "Sci-Fi"],
        "runtime": 136,
        "imdb": {"rating": 8.7, "votes": 2100000},
        "languages": ["English"],
        "plot": "A hacker discovers a simulated reality and joins a rebellion.",
    },
    {
        "title": "Roma",
        "year": 2018,
        "genres": ["Drama"],
        "runtime": 135,
        "imdb": {"rating": 7.7, "votes": 180000},
        "languages": ["Spanish", "Mixtec"],
        "plot": "A domestic worker observes family and social change in Mexico City.",
    },
    {
        "title": "Arrival",
        "year": 2016,
        "genres": ["Drama", "Sci-Fi"],
        "runtime": 116,
        "imdb": {"rating": 7.9, "votes": 760000},
        "languages": ["English"],
        "plot": "A linguist works with the military to communicate with alien visitors.",
    },
    {
        "title": "Monsters, Inc.",
        "year": 2001,
        "genres": ["Animation", "Comedy"],
        "runtime": 92,
        "imdb": {"rating": 8.1, "votes": 1000000},
        "languages": ["English"],
        "plot": "Two monsters learn that laughter is more powerful than fear.",
    },
]

weather_demo = [
    {
        "timestamp": datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
        "metaField": {"sensorId": "BOG-001", "city": "Bogota"},
        "temperature": 13.2,
        "humidity": 82,
    },
    {
        "timestamp": datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
        "metaField": {"sensorId": "BOG-001", "city": "Bogota"},
        "temperature": 14.1,
        "humidity": 78,
    },
    {
        "timestamp": datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
        "metaField": {"sensorId": "MED-001", "city": "Medellin"},
        "temperature": 22.4,
        "humidity": 65,
    },
    {
        "timestamp": datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
        "metaField": {"sensorId": "MED-001", "city": "Medellin"},
        "temperature": 23.3,
        "humidity": 62,
    },
]

transactions_demo = [
    {
        "customer_id": 1001,
        "account_id": "A-1001",
        "date": datetime(2026, 1, 3, tzinfo=timezone.utc),
        "amount": 125.50,
        "transaction_code": "buy",
        "symbol": "MDB",
    },
    {
        "customer_id": 1001,
        "account_id": "A-1001",
        "date": datetime(2026, 1, 8, tzinfo=timezone.utc),
        "amount": 80.20,
        "transaction_code": "sell",
        "symbol": "MDB",
    },
    {
        "customer_id": 1002,
        "account_id": "A-1002",
        "date": datetime(2026, 1, 9, tzinfo=timezone.utc),
        "amount": 220.00,
        "transaction_code": "buy",
        "symbol": "AAPL",
    },
]

colecciones_demo = {
    "restaurants": restaurants_demo,
    "movies": movies_demo,
    "weather_measurements": weather_demo,
    "transactions_demo": transactions_demo,
}

for nombre, documentos in colecciones_demo.items():
    db_demo[nombre].delete_many({"_seed": "curso_bigdata2026"})
    docs = []
    for doc in documentos:
        copia = dict(doc)
        copia["_seed"] = "curso_bigdata2026"
        docs.append(copia)
    db_demo[nombre].insert_many(docs)

db_demo.restaurants.create_index([("borough", ASCENDING), ("cuisine", ASCENDING)])
db_demo.restaurants.create_index([("location", GEOSPHERE)])
db_demo.movies.create_index([("genres", ASCENDING), ("year", DESCENDING)])
db_demo.weather_measurements.create_index([("metaField.sensorId", ASCENDING), ("timestamp", ASCENDING)])
db_demo.transactions_demo.create_index([("customer_id", ASCENDING), ("date", ASCENDING)])

print("Seed local/listo en bigdata_course:")
for nombre in colecciones_demo:
    print(nombre, db_demo[nombre].count_documents({"_seed": "curso_bigdata2026"}))
    ''')


def diagnostics_cell():
    return code('''
info = client.server_info()
print("Version de MongoDB:", info.get("version"))
print("Origen de conexion:", conexion_origen)

for db_name in ["sample_restaurants", "sample_mflix", "sample_airbnb", "sample_analytics", "sample_weatherdata", "bigdata_course"]:
    if db_name in client.list_database_names():
        db_tmp = client[db_name]
        print("\\nBase:", db_name)
        for col_name in db_tmp.list_collection_names()[:8]:
            try:
                print(" -", col_name, "=>", db_tmp[col_name].count_documents({}), "documentos")
            except Exception as exc:
                print(" -", col_name, "=> no se pudo contar:", str(exc)[:120])
    ''')


def select_collections_cell():
    return code('''
def coleccion_preferida(db_atlas, col_atlas, db_fallback="bigdata_course", col_fallback=None):
    col_fallback = col_fallback or col_atlas
    if db_atlas in client.list_database_names() and col_atlas in client[db_atlas].list_collection_names():
        return client[db_atlas], client[db_atlas][col_atlas], f"{db_atlas}.{col_atlas}"
    return client[db_fallback], client[db_fallback][col_fallback], f"{db_fallback}.{col_fallback}"


db_rest, restaurants, restaurants_label = coleccion_preferida(
    "sample_restaurants", "restaurants", "bigdata_course", "restaurants"
)
db_movies, movies, movies_label = coleccion_preferida(
    "sample_mflix", "movies", "bigdata_course", "movies"
)
db_weather, weather, weather_label = coleccion_preferida(
    "sample_weatherdata", "data", "bigdata_course", "weather_measurements"
)
db_trans, transactions, transactions_label = coleccion_preferida(
    "sample_analytics", "transactions", "bigdata_course", "transactions_demo"
)

print("Colecciones usadas en la sesion:")
print("restaurants:", restaurants_label)
print("movies:", movies_label)
print("weather:", weather_label)
print("transactions:", transactions_label)
    ''')


# ---------------------------------------------------------------------------
# SECCIÓN 1 — Por qué NoSQL después de Spark y Delta
# ---------------------------------------------------------------------------

def seccion1_cells():
    return [
        section_header("1", "Por que NoSQL despues de Spark y Delta"),
        md("""
## Transicion desde Spark

En las sesiones anteriores procesamos archivos con Spark: leimos Parquet, construimos DataFrames distribuidos y aplicamos transformaciones lazy sobre particiones. Ese modelo es poderoso para analitica en lotes.

MongoDB aborda un problema distinto: **modelar informacion operacional** que vive dentro de aplicaciones, eventos en tiempo real y servicios que necesitan leer objetos completos con baja latencia. No reemplaza a Spark; trabaja en otro nivel del ecosistema.

> **Pregunta de orientacion:** si en Spark la unidad de trabajo es una fila en un DataFrame distribuido, en MongoDB la unidad de trabajo es un **documento** en una coleccion.
        """),
        md("""
## Que es NoSQL

NoSQL (Not Only SQL) es una familia de sistemas de almacenamiento que surgieron para resolver limitaciones del modelo relacional cuando el volumen, la velocidad o la variedad de los datos supera lo que un esquema fijo maneja bien.

El movimiento NoSQL no propone eliminar SQL. Propone que no todo problema de datos encaja en una tabla.

### Los cuatro tipos principales

| Tipo | Modelo de datos | Ejemplos | Caso tipico |
|---|---|---|---|
| **Documental** | Documentos JSON/BSON | MongoDB, Couchbase | Catalogos, perfiles, contenido web |
| **Clave-valor** | Pares clave → valor | Redis, DynamoDB | Sesiones, cache, configuracion |
| **Columnar** | Familias de columnas | Cassandra, HBase | Series de tiempo, logs de alta escritura |
| **Grafo** | Nodos y aristas | Neo4j, Amazon Neptune | Redes sociales, recomendaciones, fraude |

MongoDB es una base **documental**: el documento es la unidad de almacenamiento, lectura y modelado.
        """),
        md("""
## Contexto historico breve

| Año | Evento |
|---|---|
| 2006 | Google publica Bigtable (base columnar para escala web) |
| 2007 | Amazon publica Dynamo (base clave-valor para alta disponibilidad) |
| 2009 | MongoDB 1.0 y el termino "NoSQL" se popularizan |
| 2011-2013 | Explosion de bases NoSQL especializadas |
| 2016+ | Las bases relacionales adoptan columnas JSON; MongoDB agrega transacciones multi-documento |
| 2023-2026 | Vector Search se integra en bases documentales para aplicaciones de IA |

La aparicion de NoSQL no fue capricho tecnico. Fue una respuesta a la escala de las aplicaciones web y a la necesidad de evolucionar esquemas sin parar el sistema.
        """),
        md("""
## Teorema CAP (mencion conceptual)

En un sistema distribuido no se pueden garantizar simultaneamente las tres propiedades siguientes:

- **C**onsistency (Consistencia): todos los nodos ven el mismo dato al mismo tiempo.
- **A**vailability (Disponibilidad): toda solicitud recibe una respuesta, aunque no sea la mas reciente.
- **P**artition tolerance (Tolerancia a particiones): el sistema sigue funcionando aunque fallen conexiones entre nodos.

MongoDB elige **CP** por defecto: prioriza consistencia y tolerancia a particiones. En modo Atlas con replicas, ofrece consistencia de lectura configurable.

Esto no significa que MongoDB sea lento; significa que ante un fallo de red, prefiere rechazar una escritura antes que confirmar datos inconsistentes.
        """),
        md("""
## Ventajas y desventajas de NoSQL documental

### Ventajas

- **Esquema flexible**: un documento puede tener campos que otro no tiene. Util cuando la estructura evoluciona.
- **Escalado horizontal**: se distribuyen datos en shards sin necesidad de un servidor unico muy costoso.
- **Lecturas de objetos completos**: si un restaurante y sus inspecciones viven en el mismo documento, una sola lectura trae todo.
- **Datos anidados naturales**: arreglos y subdocumentos reflejan la estructura real del negocio sin joins.
- **Alta velocidad de escritura**: sin joins ni integridad referencial forzada, las inserciones son rapidas.

### Desventajas

- **Joins costosos o inexistentes**: `$lookup` existe pero no es tan maduro como SQL JOIN en bases relacionales grandes.
- **Transacciones multi-documento**: soportadas desde MongoDB 4.0, pero agregan overhead y no son el patron central.
- **Sin SQL estandar**: cada base NoSQL tiene su propio lenguaje de consulta.
- **Curva de diseño diferente**: hay que pensar en patrones de consulta antes de modelar, no despues.
- **Duplicacion de datos**: el embedding repite informacion; actualizar un valor compartido requiere cuidado.

### Error comun

NoSQL no significa "sin modelo". Significa que el modelo no es necesariamente tabular, pero debe diseñarse con igual o mayor cuidado.
        """),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 2 — MongoDB en 2026
# ---------------------------------------------------------------------------

def seccion2_cells():
    return [
        section_header("2", "MongoDB en 2026"),
        md("""
## MongoDB Server, Atlas, Compass y PyMongo

| Herramienta | Que es | Para que se usa |
|---|---|---|
| MongoDB Server | Motor de base de datos | Guarda y consulta documentos |
| MongoDB Atlas | Plataforma cloud administrada | Clusters, backups, Search, Vector Search, monitoreo |
| MongoDB Compass | Interfaz grafica de escritorio | Explorar documentos, probar consultas e indices |
| PyMongo | Driver de Python | Conectar notebooks y aplicaciones Python |

## Actualizaciones relevantes 2026

- MongoDB 8.0 reporta mejoras importantes de rendimiento frente a versiones previas.
- Atlas integra Search y Vector Search para aplicaciones de busqueda y AI.
- Las colecciones time series siguen siendo importantes para IoT, monitoreo y datos por evento.
- Atlas Vector Search admite busqueda semantica, busqueda hibrida y patrones RAG.
        """),
        md("""
## Anatomia de un documento MongoDB

Un documento es un objeto JSON/BSON. Puede contener:

```json
{
  "_id": ObjectId("64a1f2e3..."),
  "name": "Bogota Coffee Lab",
  "borough": "Brooklyn",
  "cuisine": "Colombian",
  "address": {
    "street": "Bogart Street",
    "zipcode": "11206"
  },
  "grades": [
    { "date": ISODate("2025-02-01"), "grade": "A", "score": 6 },
    { "date": ISODate("2024-09-01"), "grade": "A", "score": 5 }
  ],
  "activo": true
}
```

| Elemento | Tipo | Descripcion |
|---|---|---|
| `_id` | ObjectId | Identificador unico generado automaticamente |
| `"name"` | String | Campo simple |
| `"address"` | Subdocumento | Objeto anidado con campos propios |
| `"grades"` | Array | Lista de subdocumentos con historial de inspecciones |
| `"activo"` | Boolean | Campo booleano |

BSON agrega tipos que JSON puro no tiene: `ObjectId`, `ISODate`, `Decimal128`, `Binary`.
        """),
        md("""
## Equivalencia SQL y MongoDB

| SQL | MongoDB | Notas |
|---|---|---|
| Database | Database | mismo concepto |
| Table | Collection | sin esquema fijo |
| Row | Document | puede tener campos distintos entre documentos |
| Column | Field | tipos flexibles por documento |
| Primary Key | `_id` | generado automaticamente si no se provee |
| `SELECT *` | `find({})` | trae todos los documentos |
| `WHERE` | filtro MQL `{campo: valor}` | primer argumento de `find()` |
| `SELECT campo1, campo2` | proyeccion `{campo1: 1, campo2: 1}` | segundo argumento de `find()` |
| `GROUP BY` | `$group` en pipeline | parte del aggregation pipeline |
| `JOIN` | `$lookup` en pipeline | menos eficiente que SQL JOIN en general |
| `ORDER BY` | `$sort` en pipeline | |
| `CREATE INDEX` | `create_index()` | misma idea, sintaxis distinta |

Esta tabla es el puente mas util entre lo que ya conocen y MongoDB. Ante cualquier duda de sintaxis, preguntate: ¿como lo haria en SQL? Luego busca el equivalente MQL.
        """),
        md("""
## El mismo dato: tabla SQL vs documento MongoDB

Supongamos un sistema de pedidos. En SQL tendriamos tres tablas:

```
pedidos(id, cliente_id, estado, fecha)
clientes(id, nombre, ciudad)
items_pedido(pedido_id, sku, cantidad, precio)
```

Para ver un pedido completo necesitamos dos JOIN. En MongoDB el mismo pedido puede vivir como un documento:

```json
{
  "_id": ObjectId("..."),
  "estado": "validada",
  "fecha": ISODate("2026-01-15"),
  "cliente": { "nombre": "Ana Torres", "ciudad": "Bogota" },
  "items": [
    { "sku": "TECLADO-01", "cantidad": 1, "precio": 95000 },
    { "sku": "MOUSE-03",   "cantidad": 2, "precio": 35000 }
  ]
}
```

Una sola lectura trae el pedido completo. Esta es la intuicion central del embedding: guardar junto lo que se consulta junto.

La decision no es siempre embedding. Si los clientes necesitan actualizarse independientemente y hay miles de pedidos por cliente, referenciar puede ser mejor.
        """),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 2b — Usando Atlas y Compass directamente (sin codigo)
# ---------------------------------------------------------------------------

def seccion2b_cells():
    return [
        section_header("2b", "Usando Atlas y Compass sin escribir codigo"),
        md("""
Antes de conectar desde Python, es importante conocer las interfaces graficas de MongoDB. Son el camino mas rapido para explorar datos, prototipar consultas y entender la estructura de los documentos.
        """),
        md("""
## Atlas Data Explorer (interfaz web)

1. Ingresar a [cloud.mongodb.com](https://cloud.mongodb.com) y abrir el cluster.
2. Hacer clic en **Browse Collections**.
3. Seleccionar la base de datos y la coleccion (por ejemplo, `sample_restaurants > restaurants`).
4. En el campo **Filter**, escribir un filtro MQL:
   ```json
   { "borough": "Queens" }
   ```
5. Ver los documentos que coinciden, con posibilidad de expandir subdocumentos y arreglos.
6. Desde la UI tambien se puede **insertar**, **editar** y **eliminar** documentos, y ver **indices** y estadisticas desde la pestana **Indexes**.

Esto es util para explorar datos nuevos antes de escribir codigo y para verificar resultados de inserciones o actualizaciones.
        """),
        md("""
## Atlas Aggregation Pipeline Builder

Dentro del Data Explorer, la pestana **Aggregation** permite:

1. Agregar etapas una por una con un selector visual: `$match`, `$group`, `$sort`, `$project`, etc.
2. Ver una vista previa de los documentos resultantes despues de cada etapa, en tiempo real.
3. Una vez listo el pipeline, hacer clic en **Export Pipeline Code** y elegir el lenguaje: Python, Node.js, Java, C#, etc.

El builder genera el codigo PyMongo equivalente al pipeline construido visualmente. Es una herramienta muy practica para prototipar antes de pasar al notebook.
        """),
        md("""
## MongoDB Compass (aplicacion de escritorio)

Compass se instala localmente y se conecta con el mismo URI de Atlas:

1. Abrir Compass e ingresar el URI de conexion (el mismo que se usa en PyMongo).
2. Navegar la base de datos y las colecciones.
3. En la pestana **Documents**, usar la barra de filtros para probar consultas.
4. En la pestana **Explain Plan**, ver como MongoDB planea ejecutar una consulta y si usa o no un indice.
5. En la pestana **Indexes**, crear y eliminar indices con interfaz grafica.
6. En la pestana **Aggregations**, construir pipelines de forma similar al builder de Atlas.

Compass es especialmente util para analizar planes de ejecucion y optimizar consultas lentas.
        """),
        md("""
## Cuando usar cada herramienta

| Situacion | Herramienta recomendada |
|---|---|
| Explorar datos por primera vez | Atlas Data Explorer o Compass |
| Prototipar un pipeline de agregacion | Atlas Aggregation Builder o Compass |
| Automatizar, integrar o analizar desde Python | PyMongo (este notebook) |
| Revisar si una consulta usa un indice | Compass → Explain Plan |
| Configurar indices Search o Vector Search | Atlas UI → Search Indexes |
| Compartir un resultado con un equipo no tecnico | Atlas Charts |

PyMongo no es la unica puerta de entrada a MongoDB. Es la que usamos en este notebook porque permite integrar consultas con pandas, pipelines de datos y aplicaciones analiticas.
        """),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 3 — Conexion segura
# ---------------------------------------------------------------------------

def seccion3_cells():
    return [
        section_header("3", "Conexion segura a Atlas Free y fallback Docker"),
        md("""
## Ruta principal: Atlas Free

1. Crear cuenta en MongoDB Atlas.
2. Crear cluster gratuito.
3. Cargar sample datasets desde Atlas (boton **Load Sample Dataset** en el cluster).
4. Crear usuario de base de datos con usuario y contrasena.
5. Permitir la IP temporal del entorno (Network Access → Add IP Address).
6. Copiar el URI desde **Connect → Drivers** y guardarlo como variable de entorno `MONGODB_URI`.

## Respaldo: Docker local

Si Atlas no esta disponible, se puede levantar Mongo local:

```bash
cd infraestructura
docker compose --profile nosql up -d
```

En el notebook se intenta primero Atlas y luego Docker local.

## Regla de seguridad

Nunca se escribe una URI real de Atlas dentro del cuaderno ni del repositorio. Las credenciales van en variables de entorno o se ingresan con `getpass()`.
        """),
        install_cell(),
        connection_cell(),
        ficha(
            "MongoClient(uri, ...)",
            "crea una conexion al servidor MongoDB.",
            "`uri` con credenciales y host; `serverSelectionTimeoutMS` para tiempo maximo de espera; `authSource` para la base de autenticacion.",
            "un objeto cliente que representa la conexion activa.",
            "el cliente no lanza error en la construccion; el error aparece en la primera operacion real. Usa `admin.command('ping')` para verificar inmediatamente."
        ),
        seed_cell(),
        diagnostics_cell(),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 4 — Datasets
# ---------------------------------------------------------------------------

def seccion4_cells():
    return [
        section_header("4", "Datasets reales de Atlas y seed local"),
        md("""
## Datasets usados

| Dataset Atlas | Coleccion | Uso en clase |
|---|---|---|
| `sample_restaurants` | `restaurants` | documentos anidados, geodatos, arreglos de inspecciones |
| `sample_mflix` | `movies` | arrays, generos, ratings, busqueda textual conceptual |
| `sample_airbnb` | `listingsAndReviews` | documentos ricos, ubicacion, precios, amenities |
| `sample_analytics` | `transactions` | movimientos financieros y agregaciones por cliente |
| `sample_weatherdata` | `data` | series de tiempo |

Si esos datasets no existen (Docker local), el seed de la seccion anterior crea versiones pequeñas en `bigdata_course`.
        """),
        select_collections_cell(),
        code('''
print("Primer restaurante/documento disponible:")
pprint(restaurants.find_one({}, {"_id": 0}))
        '''),
        interp("lectura de un documento", [
            "Un documento puede contener campos simples, subdocumentos y arreglos.",
            "La estructura se parece mas a un objeto de aplicacion que a una fila plana.",
            "La clave docente es identificar que partes se consultan juntas y que partes conviene indexar.",
            "El campo `grades` es un arreglo de subdocumentos: cada inspeccion es un objeto con fecha, nota y puntaje.",
        ]),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 5 — CRUD
# ---------------------------------------------------------------------------

def crud_cells():
    return [
        section_header("5", "CRUD como flujo profesional"),
        md("""
## Definicion formal

CRUD resume cuatro operaciones basicas: crear, leer, actualizar y eliminar. En MongoDB estas operaciones trabajan sobre documentos BSON dentro de colecciones.

## Intuicion

CRUD no es solo sintaxis. Es la forma en que una aplicacion mantiene estado: registra eventos, consulta datos, corrige valores y retira documentos cuando corresponde.

Trabajaremos con una coleccion de demostracion (`crud_demo`) para no modificar datasets reales de Atlas.
        """),

        # --- Crear: insert_one ---
        md("### Crear: `insert_one()`"),
        code('''
demo = client["bigdata_course"]["crud_demo"]

doc_demo = {
    "_seed": "curso_bigdata2026",
    "tipo": "orden_prueba",
    "cliente": {"id": 501, "ciudad": "Bogota"},
    "items": [
        {"sku": "MONGO-INTRO", "cantidad": 1, "precio": 120000},
        {"sku": "NOSQL-LAB",   "cantidad": 2, "precio": 85000},
    ],
    "estado": "creada",
    "creado_en": datetime.now(timezone.utc),
}

insert_result = demo.insert_one(doc_demo)
print("_id generado automaticamente:", insert_result.inserted_id)
        '''),
        interp("insert_one y el _id", [
            "MongoDB genera un ObjectId unico si no se provee `_id`.",
            "El ObjectId codifica el timestamp de insercion: los primeros 4 bytes son segundos desde epoch.",
            "Si insertas el mismo documento dos veces sin `_id`, MongoDB crea dos documentos distintos con IDs distintos.",
        ]),
        ficha("insert_one(documento)", "inserta un documento en la coleccion.", "el documento como dict de Python.", "un objeto con `inserted_id`.", "verifica `inserted_id` para confirmar que la insercion se registro y obtener el ID para lecturas posteriores."),

        # --- Leer: find_one y operadores MQL ---
        md("""
### Leer: `find_one()`, `find()` y operadores MQL

La lectura en MongoDB se hace con filtros escritos en **MQL** (MongoDB Query Language). Los filtros son diccionarios Python donde las claves son campos y los valores son condiciones.

**Notacion de punto para campos anidados**: para filtrar por `cliente.ciudad` se escribe `"cliente.ciudad"` como clave del filtro.
        """),
        code('''
# Leer por _id exacto
doc_por_id = demo.find_one({"_id": insert_result.inserted_id})
print("Por _id:")
pprint(doc_por_id)

# Leer por campo anidado (dot notation)
doc_por_ciudad = demo.find_one(
    {"cliente.ciudad": "Bogota"},
    {"tipo": 1, "estado": 1, "cliente": 1, "_id": 0}
)
print("\\nPor cliente.ciudad con proyeccion:")
pprint(doc_por_ciudad)
        '''),
        md("""
### Tabla de operadores MQL

Estos operadores son el vocabulario basico de cualquier consulta MongoDB. Son equivalentes a los operadores `WHERE` de SQL.

| Operador | Significado | Ejemplo de uso |
|---|---|---|
| *(implicito)* | igual a | `{"estado": "creada"}` |
| `$gt` | mayor que | `{"score": {"$gt": 15}}` |
| `$gte` | mayor o igual | `{"score": {"$gte": 20}}` |
| `$lt` | menor que | `{"precio": {"$lt": 100000}}` |
| `$lte` | menor o igual | `{"precio": {"$lte": 85000}}` |
| `$ne` | distinto de | `{"estado": {"$ne": "cancelada"}}` |
| `$in` | en lista | `{"cuisine": {"$in": ["Mexican", "Chinese"]}}` |
| `$nin` | no en lista | `{"borough": {"$nin": ["Bronx"]}}` |
| `$or` | disyuncion logica | `{"$or": [{"estado": "creada"}, {"estado": "validada"}]}` |
| `$and` | conjuncion logica | `{"$and": [{"borough": "Queens"}, {"cuisine": "Chinese"}]}` |
| `$exists` | campo existe | `{"zipcode": {"$exists": True}}` |
| `$type` | tipo de campo BSON | `{"score": {"$type": "number"}}` |
| `$regex` | expresion regular | `{"name": {"$regex": "^La", "$options": "i"}}` |

**Regla clave**: el filtro equivalente de `WHERE cuisine = 'Mexican' AND score >= 8` es:
```python
{"cuisine": "Mexican", "grades.score": {"$gte": 8}}
```
Varias claves en el mismo dict se interpretan como AND implicito.
        """),
        code('''
# Ejemplo con $gte: restaurantes con al menos una inspeccion score >= 20
docs_alto_score = list(restaurants.find(
    {"grades.score": {"$gte": 20}},
    {"name": 1, "borough": 1, "cuisine": 1, "_id": 0}
).limit(4))
print("Restaurantes con score >= 20 en alguna inspeccion:")
for d in docs_alto_score:
    pprint(d)

# Ejemplo con $in: cocinas en lista
docs_cocinas = list(restaurants.find(
    {"cuisine": {"$in": ["Mexican", "Colombian", "Chinese"]}},
    {"name": 1, "cuisine": 1, "borough": 1, "_id": 0}
).limit(4))
print("\\nRestaurantes con cuisines en lista:")
for d in docs_cocinas:
    pprint(d)
        '''),
        interp("filtros MQL en accion", [
            "El filtro `{grades.score: {$gte: 20}}` no requiere hacer unwind del arreglo: MongoDB busca dentro del array automaticamente.",
            "Un restaurante con 5 inspecciones donde solo una tiene score 22 aparecera en el resultado.",
            "Si necesitas el promedio de todas las inspecciones, ahi si necesitas el aggregation pipeline con $unwind.",
        ]),
        ficha("find(filtro, proyeccion)", "lee documentos que cumplen una condicion.", "filtro MQL como primer argumento; proyeccion de campos como segundo (1 para incluir, 0 para excluir).", "un cursor iterable; usa `.limit()`, `.sort()` para controlarlo.", "si no usas proyeccion ni limite puedes traer mas datos de los necesarios; el cursor no ejecuta la consulta hasta que lo iteras."),

        # --- Crear: insert_many ---
        md("### Crear varios documentos: `insert_many()`"),
        code('''
docs_batch = [
    {"_seed": "curso_bigdata2026", "tipo": "orden_prueba", "cliente": {"id": 502, "ciudad": "Medellin"}, "estado": "enviada",   "total": 75000},
    {"_seed": "curso_bigdata2026", "tipo": "orden_prueba", "cliente": {"id": 503, "ciudad": "Cali"},     "estado": "creada",    "total": 210000},
    {"_seed": "curso_bigdata2026", "tipo": "orden_prueba", "cliente": {"id": 504, "ciudad": "Bogota"},   "estado": "cancelada", "total": 30000},
]

batch_result = demo.insert_many(docs_batch)
print("IDs insertados:", batch_result.inserted_ids)
print("Total en demo ahora:", demo.count_documents({"_seed": "curso_bigdata2026"}))
        '''),
        ficha("insert_many(lista)", "inserta multiples documentos en una sola operacion.", "lista de dicts de Python.", "un objeto con `inserted_ids` (lista de ObjectIds).", "mas eficiente que llamar insert_one en un loop; si un documento falla, el resto puede seguir con `ordered=False`."),

        # --- Actualizar ---
        md("### Actualizar: `update_one()` y `update_many()`"),
        code('''
# Actualizar un documento: cambiar estado a "validada"
upd_one = demo.update_one(
    {"_id": insert_result.inserted_id},
    {"$set": {"estado": "validada"}}
)
print("matched:", upd_one.matched_count, "| modified:", upd_one.modified_count)

# Actualizar todos los de Bogota: agregar campo "region"
upd_many = demo.update_many(
    {"cliente.ciudad": "Bogota", "_seed": "curso_bigdata2026"},
    {"$set": {"region": "centro"}}
)
print("Actualizados en Bogota:", upd_many.modified_count)
        '''),
        interp("uso de $set", [
            "Usar `$set` modifica solo los campos indicados; sin `$set` el documento completo seria reemplazado.",
            "Revisar `matched_count` y `modified_count`: si matched > 0 y modified = 0, el valor ya era el mismo.",
            "`update_many` es el equivalente de `UPDATE ... WHERE` en SQL, pero sin transaccion automatica multi-documento.",
        ]),
        ficha("update_one(filtro, cambio)", "modifica el primer documento que cumple el filtro.", "filtro MQL y operador de cambio como `$set`, `$inc`, `$push`.", "un resultado con `matched_count` y `modified_count`.", "revisa ambos conteos antes de asumir que el dato cambio; si matched=0, el filtro no encontro nada."),

        # --- Eliminar ---
        md("### Eliminar: `delete_one()`"),
        code('''
# Limpiar documentos de demo creados en esta sesion
delete_result = demo.delete_many({"_seed": "curso_bigdata2026"})
print("Documentos eliminados:", delete_result.deleted_count)
        '''),
        interp("borrado seguro", [
            "La eliminacion usa la marca `_seed` para no borrar documentos reales.",
            "En produccion, un patron comun es el borrado logico: en vez de eliminar, actualizar un campo `activo: false`.",
        ]),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 6 — Diseño documental
# ---------------------------------------------------------------------------

def seccion6_cells():
    return [
        section_header("6", "Diseño documental"),
        md("""
## Embedding vs referencing

| Decision | Que significa | Ejemplo | Conviene cuando |
|---|---|---|---|
| Embedding | Guardar datos relacionados dentro del mismo documento | `grades` dentro de restaurante | Se leen juntos y tienen tamaño controlado |
| Referencing | Guardar ids hacia otros documentos | `customer_id` en transacciones | Hay alta cardinalidad o crecimiento grande |

## Preguntas de diseño

1. Que consulta sera mas frecuente.
2. Que informacion se actualiza junta.
3. Que arreglo puede crecer sin limite.
4. Que campos filtran y ordenan.
5. Que informacion debe mantenerse consistente entre documentos.
        """),
        md("""
### El mismo pedido: dos modelos

El codigo siguiente muestra el mismo pedido modelado de dos formas. Observa que la diferencia no es tecnica sino de decision de diseño.
        """),
        code('''
# Modelo 1: EMBEDDING — items dentro del documento del pedido
pedido_embebido = {
    "_id": "ORD-001",
    "cliente_id": 501,
    "estado": "validada",
    "fecha": datetime(2026, 1, 15, tzinfo=timezone.utc),
    "items": [
        {"sku": "TECLADO-01", "nombre": "Teclado mecanico", "cantidad": 1, "precio": 95000},
        {"sku": "MOUSE-03",   "nombre": "Mouse ergonomico", "cantidad": 2, "precio": 35000},
    ],
    "total": 165000,
}

# Modelo 2: REFERENCING — items en coleccion separada
pedido_referenciado = {
    "_id": "ORD-001",
    "cliente_id": 501,
    "estado": "validada",
    "fecha": datetime(2026, 1, 15, tzinfo=timezone.utc),
    "total": 165000,
}

items_separados = [
    {"pedido_id": "ORD-001", "sku": "TECLADO-01", "nombre": "Teclado mecanico", "cantidad": 1, "precio": 95000},
    {"pedido_id": "ORD-001", "sku": "MOUSE-03",   "nombre": "Mouse ergonomico", "cantidad": 2, "precio": 35000},
]

print("--- Modelo embebido ---")
pprint(pedido_embebido)
print("\\n--- Modelo referenciado (pedido) ---")
pprint(pedido_referenciado)
print("\\n--- Modelo referenciado (items) ---")
pprint(items_separados)
        '''),
        interp("embedding vs referencing en accion", [
            "El modelo embebido lee un pedido completo con una sola operacion. Ideal si los items no se consultan sin su pedido.",
            "El modelo referenciado permite consultar todos los items de un SKU especifico sin cargar pedidos completos.",
            "El embedding tiene un limite: MongoDB impone un tamaño maximo de 16 MB por documento. Un pedido con 10,000 items embebidos puede acercarse a ese limite.",
            "La regla practica: si el arreglo puede crecer sin control, referencia. Si es de tamaño fijo y pequeno, embebe.",
        ]),
        md("""
## Advertencia sobre arreglos que crecen

Si una aplicacion agrega continuamente elementos a un arreglo embebido (por ejemplo, mensajes de un chat, logs de un proceso, eventos de un usuario), el documento crece con cada escritura. Esto provoca:

- Documentos enormes que tardan mas en leerse.
- Fragmentacion en disco.
- El limite de 16 MB se puede alcanzar.

En esos casos, el patron correcto es una coleccion separada con `documento_id` como referencia.
        """),
        ficha("BSON", "representa documentos de forma binaria para MongoDB.", "campos, tipos nativos como ObjectId, ISODate, Decimal128 y arreglos.", "documentos almacenables y consultables.", "permite fechas reales y tipos que JSON puro no maneja; los drivers de Python convierten automaticamente `datetime` a ISODate."),
        ficha("Embedding", "guarda informacion relacionada dentro del documento principal.", "subdocumentos o arrays como valor de un campo.", "lecturas mas directas sin joins.", "sirve cuando los datos se consultan juntos y el arreglo no crece sin control."),
        ficha("Referencing", "relaciona documentos mediante identificadores.", "campo con el `_id` de otro documento.", "documentos separados que se unen desde la aplicacion o con `$lookup`.", "sirve cuando hay alta cardinalidad, actualizaciones independientes o crecimiento ilimitado del arreglo."),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 7 — Aggregation Pipeline
# ---------------------------------------------------------------------------

def aggregation_cells():
    return [
        section_header("7", "Aggregation Pipeline"),
        md("""
## Definicion formal

Un **aggregation pipeline** es una secuencia de etapas. Cada etapa recibe documentos, los filtra, transforma, agrupa u ordena, y entrega documentos a la siguiente etapa.

## Equivalencia con SQL y Spark

| MongoDB | SQL | Spark |
|---|---|---|
| `$match` | `WHERE` | `filter()` |
| `$project` | `SELECT columnas` | `select()` |
| `$group` | `GROUP BY` | `groupBy().agg()` |
| `$sort` | `ORDER BY` | `orderBy()` |
| `$limit` | `LIMIT` | `limit()` |
| `$unwind` | explode array | `explode()` |
| `$lookup` | `JOIN` | `join()` |
| `$count` | `COUNT(*)` | `count()` |

La regla de rendimiento es identica a Spark: **filtra temprano** con `$match`, **proyecta campos necesarios** con `$project`, y **agrupa solo lo que aporta** a la pregunta.
        """),

        # Pipeline de 1 etapa
        md("### Pipeline de una etapa: `$match`"),
        code('''
# Un pipeline de una etapa es solo un filtro.
# La potencia aparece cuando encadenamos etapas.
resultado_simple = list(restaurants.aggregate([
    {"$match": {"borough": "Queens"}}
]))
print(f"Restaurantes en Queens: {len(resultado_simple)}")
pprint(resultado_simple[0] if resultado_simple else "sin resultados")
        '''),
        interp("pipeline minimo", [
            "Un pipeline de una etapa equivale exactamente a `find({filtro})`.",
            "La ventaja del pipeline aparece cuando se agregan mas etapas: no es posible agrupar o transformar con `find()` solo.",
        ]),

        # Pipeline de 2 etapas
        md("### Pipeline de dos etapas: `$match` + `$project`"),
        code('''
# Seleccionar solo campos relevantes de restaurantes en Manhattan
pipeline_2 = [
    {"$match": {"borough": "Manhattan"}},
    {"$project": {"_id": 0, "name": 1, "cuisine": 1, "borough": 1}},
]

resultado_2 = list(restaurants.aggregate(pipeline_2))
print(f"Total: {len(resultado_2)}")
pd.DataFrame(resultado_2).head(6)
        '''),

        # Pipeline completo: grupo por borough + cocina
        md("### Pipeline completo: `$match` + `$group` + `$sort` + `$limit`"),
        code('''
pipeline_cocinas = [
    {"$match": {"borough": {"$exists": True}, "cuisine": {"$exists": True}}},
    {"$group": {
        "_id": {"borough": "$borough", "cuisine": "$cuisine"},
        "n_restaurantes": {"$sum": 1}
    }},
    {"$sort": {"n_restaurantes": -1}},
    {"$limit": 12},
]

resultado_cocinas = list(restaurants.aggregate(pipeline_cocinas))
pd.DataFrame(resultado_cocinas)
        '''),
        interp("top de cocinas por zona", [
            "El resultado resume documentos en lugar de mostrarlos uno por uno.",
            "La clave `_id` contiene el grupo compuesto: zona y tipo de cocina.",
            "En un dataset Atlas real veras mas diversidad; en el seed local veras pocos grupos, pero la logica es la misma.",
        ]),

        # $unwind
        md("### `$unwind`: explotar arreglos"),
        code('''
pipeline_scores = [
    {"$unwind": "$grades"},
    {"$match": {"grades.score": {"$type": "number"}}},
    {"$group": {
        "_id": "$cuisine",
        "promedio_score": {"$avg": "$grades.score"},
        "n_inspecciones": {"$sum": 1}
    }},
    {"$sort": {"promedio_score": 1}},
    {"$limit": 10},
]

pd.DataFrame(list(restaurants.aggregate(pipeline_scores)))
        '''),
        interp("arrays y $unwind", [
            "`grades` es un arreglo; `$unwind` crea una fila logica por cada elemento del arreglo.",
            "Esto permite calcular promedios por cocina sin desnormalizar previamente la coleccion.",
            "Despues de `$unwind`, cada 'fila' del pipeline tiene los campos del restaurante mas los campos de una inspeccion.",
        ]),

        # Peliculas por decada
        code('''
pipeline_peliculas = [
    {"$match": {"year": {"$type": "number"}, "genres": {"$exists": True}}},
    {"$unwind": "$genres"},
    {"$project": {
        "genre": "$genres",
        "decada": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]},
        "rating": "$imdb.rating"
    }},
    {"$group": {
        "_id": {"decada": "$decada", "genre": "$genre"},
        "n_peliculas": {"$sum": 1},
        "rating_promedio": {"$avg": "$rating"}
    }},
    {"$sort": {"_id.decada": -1, "n_peliculas": -1}},
    {"$limit": 15},
]

pd.DataFrame(list(movies.aggregate(pipeline_peliculas)))
        '''),

        # Transacciones
        code('''
pipeline_transacciones = [
    {"$match": {"amount": {"$type": "number"}}},
    {"$group": {
        "_id": {"customer_id": "$customer_id", "codigo": "$transaction_code"},
        "valor_total": {"$sum": "$amount"},
        "n_movimientos": {"$sum": 1}
    }},
    {"$sort": {"valor_total": -1}},
    {"$limit": 10},
]

pd.DataFrame(list(transactions.aggregate(pipeline_transacciones)))
        '''),

        # $lookup
        md("""
### `$lookup`: join entre colecciones

`$lookup` es el equivalente de un LEFT JOIN en SQL. Une documentos de la coleccion actual con documentos de otra coleccion basandose en un campo comun.

**Cuando usarlo**: cuando los datos estan referenciados (no embebidos) y necesitas combinarlos para un reporte.

**Limitacion**: es menos eficiente que un JOIN relacional en tablas muy grandes. Preferir el embedding cuando el patron de lectura es predecible.
        """),
        code('''
# Ejemplo conceptual: unir transactions_demo con una tabla de simbolos.
# Se inserta una coleccion auxiliar minima para ilustrar el $lookup.

simbolos_col = client["bigdata_course"]["simbolos"]
simbolos_col.delete_many({"_seed": "curso_bigdata2026"})
simbolos_col.insert_many([
    {"_seed": "curso_bigdata2026", "symbol": "MDB",  "empresa": "MongoDB Inc.",  "sector": "Tecnologia"},
    {"_seed": "curso_bigdata2026", "symbol": "AAPL", "empresa": "Apple Inc.",    "sector": "Tecnologia"},
])

pipeline_lookup = [
    {"$match": {"amount": {"$type": "number"}}},
    {"$lookup": {
        "from": "simbolos",
        "localField": "symbol",
        "foreignField": "symbol",
        "as": "info_empresa"
    }},
    {"$unwind": {"path": "$info_empresa", "preserveNullAndEmpty": True}},
    {"$project": {
        "_id": 0,
        "customer_id": 1,
        "symbol": 1,
        "amount": 1,
        "transaction_code": 1,
        "empresa": "$info_empresa.empresa",
        "sector": "$info_empresa.sector",
    }},
]

pd.DataFrame(list(transactions.aggregate(pipeline_lookup)))
        '''),
        interp("$lookup en practica", [
            "`from` indica la coleccion con la que se hace el join.",
            "`localField` es el campo de la coleccion actual; `foreignField` es el campo de la coleccion remota.",
            "El resultado se guarda en un arreglo (`as`); `$unwind` lo aplana a un campo plano.",
            "Si no hay coincidencia y `preserveNullAndEmpty` es True, el documento se conserva con el campo vacio.",
        ]),
        ficha("aggregate(pipeline)", "ejecuta una secuencia de etapas de transformacion sobre una coleccion.", "lista de dicts, cada uno con una etapa: `$match`, `$group`, `$sort`, `$project`, `$unwind`, `$lookup`, `$limit`, etc.", "un cursor con los documentos resultantes de la ultima etapa.", "el pipeline se ejecuta de izquierda a derecha; filtra primero para reducir el volumen de datos en etapas costosas como `$group`."),
        ficha("$lookup", "une documentos de dos colecciones por un campo comun (equivalente a LEFT JOIN).", "`from` (coleccion remota), `localField`, `foreignField`, `as` (nombre del resultado).", "agrega un campo tipo arreglo con los documentos coincidentes de la coleccion remota.", "usar $unwind para aplanar el arreglo resultante; rendimiento optimo cuando ambos campos tienen indice."),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 8 — Índices y rendimiento
# ---------------------------------------------------------------------------

def index_cells():
    return [
        section_header("8", "Indices y rendimiento"),
        md("""
## Definicion formal

Un indice es una estructura auxiliar que permite encontrar documentos sin revisar toda la coleccion. Sin indice, MongoDB hace un **collection scan**: revisa cada documento. Con indice, salta directamente a los documentos relevantes.

## Tipos que veremos

- **Simple**: un campo, por ejemplo `cuisine`.
- **Compuesto**: varios campos, por ejemplo `borough + cuisine`.
- **Multikey**: sobre arrays, por ejemplo `genres` (MongoDB crea automaticamente entradas por cada elemento del array).
- **Geoespacial (2dsphere)**: sobre campos GeoJSON.
- **TTL**: expira documentos automaticamente despues de un tiempo.

## Error comun

Crear indices para todo no es optimizar. Cada indice acelera algunas lecturas, pero **agrega costo a escrituras y almacenamiento**. El principio es: crea indices para consultas frecuentes y costosas, no para todas las consultas posibles.
        """),
        code('''
restaurants.create_index([("borough", ASCENDING), ("cuisine", ASCENDING)])

consulta = {"borough": "Queens", "cuisine": {"$in": ["American", "Chinese", "Colombian"]}}
proyeccion = {"name": 1, "borough": 1, "cuisine": 1, "_id": 0}

print("Consulta con filtro y proyeccion:")
for doc in restaurants.find(consulta, proyeccion).limit(5):
    pprint(doc)

print("\\nPlan de ejecucion resumido:")
plan = restaurants.find(consulta, proyeccion).limit(5).explain()
pprint(plan.get("queryPlanner", {}).get("winningPlan", plan))
        '''),
        interp("lectura de explain", [
            "`explain()` muestra como MongoDB planea resolver la consulta.",
            "Busca `IXSCAN` (Index Scan) en el plan: significa que el indice fue usado.",
            "Si ves `COLLSCAN` (Collection Scan) en una consulta frecuente, probablemente falte un indice.",
            "La interpretacion exacta depende de la version de MongoDB, pero la pregunta docente siempre es: ¿que campos filtro y existe un indice para ellos?",
        ]),
        md("""
## TTL Index: indice con expiracion automatica

Un TTL (Time To Live) index elimina automaticamente documentos despues de un tiempo definido. Es muy util para:

- Sesiones de usuario (expirar despues de 30 minutos de inactividad).
- Logs temporales (conservar solo los ultimos 7 dias).
- Tokens de autenticacion con tiempo de vida limitado.
- Datos de sensores IoT que no deben acumularse indefinidamente.

```python
# Ejemplo conceptual: expira documentos 3600 segundos (1 hora) despues de creado_en
coleccion.create_index(
    [("creado_en", ASCENDING)],
    expireAfterSeconds=3600
)
```

MongoDB revisa los indices TTL cada 60 segundos, por lo que la eliminacion puede tardar hasta un minuto en ejecutarse.

**Importante**: el campo indexado debe ser de tipo `datetime` con zona horaria UTC. Si el campo no existe en un documento, ese documento no expira.
        """),
        ficha("create_index(keys, ...)", "crea un indice sobre uno o mas campos de la coleccion.", "`keys` como lista de tuplas `(campo, ASCENDING/DESCENDING/GEOSPHERE)`; opciones como `unique=True`, `expireAfterSeconds=N`.", "el nombre del indice creado.", "si el indice ya existe con la misma definicion, MongoDB no lo duplica; si cambia la definicion, primero eliminalo con `drop_index()`."),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 9 — Geodatos
# ---------------------------------------------------------------------------

def geo_cells():
    return [
        section_header("9", "Geodatos con MongoDB"),
        md("""
## Definicion formal

MongoDB soporta datos geoespaciales usando GeoJSON. Un punto se representa como:

```json
{ "type": "Point", "coordinates": [longitud, latitud] }
```

La coordenada va en orden **longitud, latitud** (no al reves como en Google Maps). Es un error comun invertirlos.

Para usar consultas geoespaciales, el campo debe tener un indice `2dsphere`.
        """),
        code('''
restaurants.create_index([("location", GEOSPHERE)])

centro_queens = {
    "type": "Point",
    "coordinates": [-73.8803827, 40.7643124],
}

geo_query = {
    "location": {
        "$near": {
            "$geometry": centro_queens,
            "$maxDistance": 8000,
        }
    }
}

campos = {"name": 1, "borough": 1, "cuisine": 1, "location": 1, "_id": 0}
docs_geo = list(restaurants.find(geo_query, campos).limit(10))
pd.DataFrame(docs_geo)
        '''),
        interp("consulta geoespacial", [
            "La consulta busca restaurantes dentro de 8 km del punto de referencia.",
            "El indice `2dsphere` es obligatorio para que `$near` funcione; sin el, MongoDB lanza un error.",
            "Los resultados llegan ordenados por distancia al punto de referencia, de mas cercano a mas lejano.",
            "Con el dataset seed local el resultado es pequeno; con `sample_restaurants` se vuelve un caso real de exploracion urbana.",
        ]),
        code('''
# Visualizacion opcional con folium. Si no esta instalado, la clase continua sin mapa.
try:
    import folium
    mapa = folium.Map(location=[40.7643, -73.8803], zoom_start=11)
    for doc in docs_geo:
        coords = doc.get("location", {}).get("coordinates")
        if coords:
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=f"{doc.get('name')} - {doc.get('cuisine')}"
            ).add_to(mapa)
    display(mapa)
except Exception as exc:
    print("Mapa opcional no disponible:", str(exc)[:200])
        '''),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 10 — Time Series
# ---------------------------------------------------------------------------

def time_series_cells():
    return [
        section_header("10", "Time Series en MongoDB"),
        md("""
## Definicion formal

Una coleccion de series de tiempo guarda mediciones asociadas a un instante. MongoDB usa tres componentes:

- `timeField`: campo con la fecha/hora de la medicion (obligatorio, tipo `datetime`).
- `metaField`: campo con metadatos de la fuente, como sensor, ciudad o dispositivo (recomendado).
- **metricas**: los demas campos con los valores medidos: temperatura, humedad, precio, latencia, etc.

MongoDB optimiza internamente el almacenamiento de series de tiempo para compresion y consultas por rango de tiempo.

En MongoDB 8.0, las shard keys que contienen el `timeField` estan deprecadas para estas colecciones; la recomendacion es distribuir por metadatos, no por el tiempo crudo.

## Casos de uso tipicos

- Sensores IoT (temperatura, humedad, vibracion).
- Metricas de infraestructura (CPU, latencia, errores por minuto).
- Precios de activos financieros.
- Logs de eventos de aplicacion.
        """),
        code('''
pipeline_weather = [
    {"$match": {"timestamp": {"$exists": True}}},
    {"$project": {
        "ciudad": "$metaField.city",
        "sensor": "$metaField.sensorId",
        "hora": {"$dateToString": {"format": "%Y-%m-%d %H:00", "date": "$timestamp"}},
        "temperature": 1,
        "humidity": 1,
    }},
    {"$group": {
        "_id": {"ciudad": "$ciudad", "hora": "$hora"},
        "temp_promedio": {"$avg": "$temperature"},
        "humedad_promedio": {"$avg": "$humidity"},
        "n_mediciones": {"$sum": 1}
    }},
    {"$sort": {"_id.hora": 1, "_id.ciudad": 1}},
    {"$limit": 20},
]

pd.DataFrame(list(weather.aggregate(pipeline_weather)))
        '''),
        interp("series de tiempo", [
            "La unidad de analisis ya no es una entidad estatica, sino una medicion en el tiempo.",
            "El `metaField` permite agrupar mediciones de la misma fuente sin necesidad de filtros complejos.",
            "La etapa `$dateToString` convierte la fecha a texto para agrupar por hora: todos los registros de la misma hora forman un grupo.",
            "Este patron es identico a un resample horario en pandas o a una ventana temporal en Spark Structured Streaming.",
        ]),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 11 — Atlas Search y Vector Search
# ---------------------------------------------------------------------------

def search_vector_cells():
    return [
        section_header("11", "Atlas Search y Vector Search"),
        md("""
## Atlas Search

Atlas Search agrega busqueda textual con relevancia. A diferencia de un filtro exacto como `{"title": "Matrix"}`, una busqueda textual puede:

- Ordenar resultados por relevancia (no por insercion o alphabeticamente).
- Analizar lenguaje: plurales, sinonimos, stopwords.
- Soportar experiencias tipo buscador web dentro de la propia base de datos.

Se configura creando un **Search Index** desde la UI de Atlas o via API, y luego se usa la etapa `$search` en un aggregation pipeline.

## Vector Search

MongoDB Vector Search permite almacenar **embeddings** (vectores numericos que representan significado) junto con los documentos operacionales. En 2026 se usa para:

- Busqueda semantica: encontrar documentos similares en significado, no solo en palabras exactas.
- Busqueda hibrida: combinar texto exacto + similitud semantica.
- Patrones RAG (Retrieval-Augmented Generation): recuperar contexto relevante para modelos de lenguaje.
- Recomendadores por similitud de contenido.

Los indices de Vector Search admiten embeddings de hasta 8192 dimensiones y permiten prefiltros por campos indexados.

## La diferencia clave

| Tipo de busqueda | Pregunta que responde | Ejemplo |
|---|---|---|
| Filtro exacto MQL | ¿Cuales peliculas tienen genero `Sci-Fi`? | `{"genres": "Sci-Fi"}` |
| Atlas Search textual | ¿Cuales peliculas mencionan "aliens" o "extraterrestres"? | `$search` con query textual |
| Vector Search semantico | ¿Cuales peliculas tratan sobre comunicacion con seres no humanos, aunque no usen esa frase? | `$vectorSearch` con embedding de la pregunta |

La tercera pregunta requiere representar **significado**. Ese es el espacio natural de embeddings y Vector Search.

## Nota de ejecucion

Los ejemplos siguientes son conceptuales. Para ejecutarlos se necesita Atlas con un indice Search o Vector Search configurado desde la UI.
        """),
        code('''
# Ejemplo conceptual de pipeline Atlas Search.
# Requiere un indice Search en Atlas llamado "movies_text_search".
pipeline_search_conceptual = [
    {
        "$search": {
            "index": "movies_text_search",
            "text": {
                "query": "alien communication language",
                "path": ["plot", "title"]
            }
        }
    },
    {"$project": {"title": 1, "plot": 1, "score": {"$meta": "searchScore"}}},
    {"$limit": 5}
]

pprint(pipeline_search_conceptual)
        '''),
        code('''
# Ejemplo conceptual de $vectorSearch.
# Requiere Atlas Vector Search y embeddings reales almacenados en el campo "plot_embedding".
pipeline_vector_conceptual = [
    {
        "$vectorSearch": {
            "index": "plot_embedding_index",
            "path": "plot_embedding",
            "queryVector": [0.12, -0.03, 0.44],  # en practica: embedding del texto de busqueda
            "numCandidates": 100,
            "limit": 5,
            "filter": {"year": {"$gte": 2000}}
        }
    },
    {"$project": {"title": 1, "plot": 1, "score": {"$meta": "vectorSearchScore"}}}
]

pprint(pipeline_vector_conceptual)
        '''),
    ]


# ---------------------------------------------------------------------------
# SECCIÓN 12 — Taller guiado
# ---------------------------------------------------------------------------

def workshop_cells():
    return [
        section_header("12", "Taller guiado"),
        md("""
El taller se resuelve sobre Atlas si los sample datasets estan cargados. Si no, usa el seed local `bigdata_course`. Lo importante es practicar la forma de pensar:

1. Que pregunta tengo.
2. Que documentos necesito.
3. Que campos filtro y con que operadores.
4. Que campos proyecto.
5. Que agregacion resume mejor.
6. Que interpretacion es valida y que no puedo concluir todavia.
        """),

        md("#### Ejercicio 1 — Consulta simple con proyeccion"),
        code('''
# Mostrar nombre, borough y cocina de los primeros 5 restaurantes.
for doc in restaurants.find(
    {"borough": {"$exists": True}},
    {"name": 1, "borough": 1, "cuisine": 1, "_id": 0}
).limit(5):
    pprint(doc)
        '''),

        md("#### Ejercicio 2 — Filtro con `$gte` sobre un campo de arreglo"),
        code('''
# Restaurantes que tienen al menos una inspeccion con score >= 20.
docs_altos = list(restaurants.find(
    {"grades.score": {"$gte": 20}},
    {"name": 1, "borough": 1, "cuisine": 1, "grades.score": 1, "_id": 0}
).limit(5))
for d in docs_altos:
    pprint(d)
        '''),

        md("#### Ejercicio 3 — Filtro con `$or`"),
        code('''
# Restaurantes que estan en Queens O tienen cocina Colombian.
docs_or = list(restaurants.find(
    {"$or": [{"borough": "Queens"}, {"cuisine": "Colombian"}]},
    {"name": 1, "borough": 1, "cuisine": 1, "_id": 0}
).limit(6))
print(f"Encontrados: {len(docs_or)}")
for d in docs_or:
    pprint(d)
        '''),

        md("#### Ejercicio 4 — Dot notation: filtro por campo anidado"),
        code('''
# Restaurantes cuya direccion tiene zipcode "11369".
# La clave del filtro usa notacion de punto para acceder al subdocumento.
docs_zip = list(restaurants.find(
    {"address.zipcode": "11369"},
    {"name": 1, "address.zipcode": 1, "borough": 1, "_id": 0}
))
print(f"Encontrados con zipcode 11369: {len(docs_zip)}")
for d in docs_zip:
    pprint(d)
        '''),

        md("#### Ejercicio 5 — Agregacion ejecutiva por cocina"),
        code('''
pipeline = [
    {"$group": {"_id": "$cuisine", "n": {"$sum": 1}}},
    {"$sort": {"n": -1}},
    {"$limit": 10},
]
pd.DataFrame(list(restaurants.aggregate(pipeline)))
        '''),

        md("#### Ejercicio 6 — Indice y explain sobre consulta frecuente"),
        code('''
restaurants.create_index([("cuisine", ASCENDING)])
plan = restaurants.find({"cuisine": "American"}).limit(3).explain()
winning = plan.get("queryPlanner", {}).get("winningPlan", plan)
pprint(winning)
# Busca IXSCAN en la salida: indica que el indice fue usado.
        '''),

        md("#### Ejercicio 7 — Comparacion SQL vs Mongo (la misma consulta)"),
        code('''
sql_equivalente = (
    "SELECT cuisine, COUNT(*) AS n\\n"
    "FROM restaurants\\n"
    "GROUP BY cuisine\\n"
    "ORDER BY n DESC\\n"
    "LIMIT 10;"
)

mongo_equivalente = [
    {"$group": {"_id": "$cuisine", "n": {"$sum": 1}}},
    {"$sort": {"n": -1}},
    {"$limit": 10},
]

print("--- SQL ---")
print(sql_equivalente)
print("\\n--- MongoDB pipeline equivalente ---")
pprint(mongo_equivalente)
        '''),

        md("""
#### Ejercicio 8 — Pregunta de diseño documental (reflexion)

Dado el siguiente esquema relacional de un sistema de biblioteca:

```
autores(id, nombre, nacionalidad)
libros(id, titulo, anio, autor_id)
prestamos(id, libro_id, usuario, fecha_inicio, fecha_fin)
```

Responde en texto (no en codigo):

1. Si el caso de uso principal es *mostrar un libro con su autor*, ¿embederias el autor dentro del documento libro o usarias referencia?
2. Si los prestamos de un libro pueden llegar a miles a lo largo de los anos, ¿los embederias dentro del libro o usarias una coleccion separada?
3. ¿Que campo o campos indexarias para responder rapidamente a la pregunta *prestamos activos de un usuario*?

No hay una sola respuesta correcta. El objetivo es justificar cada decision con las cinco preguntas de diseño de la Seccion 6.
        """),

        interp("taller guiado", [
            "Una solucion correcta no trae toda la coleccion para filtrar en Python.",
            "La proyeccion y el limite hacen visible que se piensa en datos grandes.",
            "El operador `$or` y la dot notation son herramientas que aparecen constantemente en consultas reales.",
            "La interpretacion debe distinguir resultado descriptivo de causalidad o juicio de negocio.",
            "El ejercicio de diseño no tiene solucion unica; lo importante es que la decision se justifique con el patron de consulta.",
        ]),
    ]


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------

def build_cells():
    cells = [
        *uce_header(
            title="MongoDB Atlas, NoSQL documental y analitica moderna",
            session=12,
            github_path="main/Cuadernos/12_MongoDB_Atlas_NoSQL_Moderno.ipynb",
            nota_plataforma="MongoDB Atlas Free como ruta principal; Docker local como respaldo.",
        ),
        md("""
## Vista rapida de la sesion

| Elemento | Detalle |
|---|---|
| Sesion | 12 |
| Tema | MongoDB Atlas, NoSQL documental y analitica moderna |
| Herramientas | MongoDB Atlas Free, PyMongo, Compass, Docker local |
| Producto | Notebook de consulta, agregacion e interpretacion sobre datos documentales |
| Competencia | Diseñar y consultar documentos JSON/BSON con criterio analitico |

## Proposito pedagogico

Despues de Spark, Parquet y Delta Lake, esta sesion cambia la pregunta: ya no solo pensamos en procesar archivos o tablas analiticas, sino en modelar informacion flexible para aplicaciones y analitica operativa.

MongoDB no debe presentarse como una base "sin estructura". Es una base documental: permite estructuras flexibles, pero exige diseñar documentos segun las consultas, los patrones de lectura y la forma real de la informacion.
        """),
        toc([
            "1. Por que NoSQL despues de Spark y Delta",
            "2. MongoDB en 2026 -- fundamentos y equivalencias",
            "2b. Usando Atlas y Compass sin escribir codigo",
            "3. Conexion segura a Atlas Free y fallback Docker",
            "4. Datasets reales de Atlas y seed local",
            "5. CRUD como flujo profesional",
            "6. Diseño documental",
            "7. Aggregation Pipeline",
            "8. Indices y rendimiento",
            "9. Geodatos",
            "10. Time Series",
            "11. Atlas Search y Vector Search",
            "12. Taller guiado",
            "13. Cierre y referencias",
        ]),
        *seccion1_cells(),
        *seccion2_cells(),
        *seccion2b_cells(),
        *seccion3_cells(),
        *seccion4_cells(),
        *crud_cells(),
        *seccion6_cells(),
        *aggregation_cells(),
        *index_cells(),
        *geo_cells(),
        *time_series_cells(),
        *search_vector_cells(),
        *workshop_cells(),
        section_header("13", "Cierre y referencias"),
        md("""
## Recapitulacion

MongoDB permite modelar datos como documentos: una forma potente cuando los datos tienen estructura flexible, campos anidados, arreglos y patrones de lectura orientados a objetos.

Aprendimos a:
- Contextualizar MongoDB dentro del ecosistema NoSQL y despues de Spark.
- Leer y escribir documentos con PyMongo y desde la interfaz de Atlas.
- Usar operadores MQL para filtrar con precision.
- Diseñar documentos eligiendo entre embedding y referencing.
- Construir aggregation pipelines de una a cuatro etapas.
- Usar `$lookup` para unir colecciones referenciadas.
- Crear indices y leer planes de ejecucion.
- Trabajar con geodatos y series de tiempo.

## Idea mas importante

La flexibilidad no reemplaza el diseño. Una buena coleccion documental se diseña desde las consultas: que filtro, que proyecto, que agrego, que indexo y que interpreto.

## Errores comunes

- Pegar credenciales reales en el notebook o en el repositorio.
- Traer toda la coleccion con `list(find())` sin filtro ni limite.
- Filtrar en Python lo que MongoDB puede filtrar con MQL.
- Crear indices sin relacion con consultas reales.
- Usar documentos con arreglos que crecen sin limite (embedding sin control).
- Confundir busqueda exacta con busqueda semantica.
- Invertir longitud y latitud en datos GeoJSON.

## Proxima sesion

Integrar MongoDB con pipelines de datos, aplicaciones analiticas o busqueda avanzada con Atlas Search.

## Referencias

- MongoDB 8.0 release notes: https://www.mongodb.com/docs/manual/release-notes/8.0/
- Atlas sample datasets: https://www.mongodb.com/docs/atlas/sample-data/
- Aggregation pipeline: https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
- MQL operators: https://www.mongodb.com/docs/manual/reference/operator/query/
- Time series collections: https://www.mongodb.com/docs/v8.0/core/timeseries-collections/
- MongoDB Vector Search: https://www.mongodb.com/docs/vector-search/
- Atlas Aggregation Pipeline Builder: https://www.mongodb.com/docs/atlas/atlas-ui/agg-pipeline/
- MongoDB Compass: https://www.mongodb.com/products/tools/compass
- Atlas changelog: https://www.mongodb.com/docs/atlas/release-notes/changelog/
- MongoDB Community Docker: https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-community-with-docker/
        """),
    ]
    return cells


def main():
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)


if __name__ == "__main__":
    main()
