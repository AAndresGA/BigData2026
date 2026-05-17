# -*- coding: utf-8 -*-
"""
Genera Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb

Taller final en formato reto: observatorio operativo de contratacion publica
con SECOP II desde 2021, datos no estructurados, MongoDB y dashboard.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header


cells = [
    *uce_header(
        title="Taller final: reto de observatorio operativo con SECOP II y MongoDB",
        session=13,
        github_path="main/Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb",
        nota_plataforma="Jupyter, Colab o Databricks. MongoDB Atlas recomendado para el dashboard.",
    ),
    md("""
# Reto del taller

Una oficina de control interno necesita una herramienta sencilla para revisar
contratacion publica reciente. El equipo no quiere leer miles de filas crudas.
Necesita una bandeja de contratos priorizados, fichas consultables y un tablero
que cambie cuando llega una nueva carga.

Ustedes son el equipo de datos. Deben construir un prototipo funcional con datos
publicos de SECOP II desde `2021-01-01`.

La solucion no debe afirmar fraude. Debe responder:

> Que contratos, proveedores, entidades, territorios y temas merecen revision
> prioritaria segun reglas descriptivas y verificables?
    """),
    md("""
## Reglas del reto

1. Solo se aceptan datos desde `2021-01-01`.
2. Deben integrar varias bases: contratos, adiciones, ejecucion y territorio.
3. Deben usar al menos un dato no estructurado: texto libre del objeto contractual
   o descripcion de adiciones.
4. Deben resolver un reto NoSQL real con MongoDB: modelo documental, `upsert`,
   consultas por campos anidados, agregaciones y busqueda textual.
5. Deben crear documentos en MongoDB. Si el entorno de clase lo impide, pueden
   generar JSON de respaldo, pero la entrega final debe mostrar MongoDB o una
   justificacion tecnica verificable.
6. Deben demostrar dos cargas: `lote_1` y `lote_2`.
7. Deben crear datos para un dashboard.
8. Airflow es opcional. El taller se debe poder resolver desde este cuaderno.

El reto no es copiar codigo. El reto es completar, ejecutar, verificar y explicar.
    """),
    md("""
## Lo que deben entregar

| Entregable | Que debe contener |
|---|---|
| Notebook ejecutado | Evidencia de cada reto resuelto |
| Arquitectura | Diagrama del flujo usado |
| Modelo NoSQL | Explicacion de por que se embeben entidad, proveedor, territorio, texto y prioridad |
| MongoDB | Documentos, indices, consultas, agregaciones y metadata de carga |
| Dashboard | KPIs, alertas, proveedores, entidades y temas |
| Informe ejecutivo | Hallazgos, limites y recomendaciones |

El profesor verificara evidencias, no solo texto descriptivo.
    """),
    md("""
## Criterios de entrega

La entrega debe tener esta estructura minima:

```text
entrega_equipo/
  notebook_taller.ipynb
  informe_ejecutivo.pdf
  arquitectura.png
  evidencia_dashboard/
    lote_1.png
    lote_2.png
  evidencia_mongodb/
    contratos_operativos.json
    alertas_revision.json
    dashboard_kpis.json
    dashboard_temas.json
    consultas_mongodb.md
```

Si usan MongoDB Atlas, pueden reemplazar los JSON por capturas o exportaciones
de las colecciones, pero deben demostrar:

- nombre de la base de datos;
- colecciones creadas;
- cantidad de documentos por coleccion;
- indices creados;
- consultas ejecutadas;
- diferencia entre lote 1 y lote 2.
    """),
    md("""
## Arquitectura minima que deben implementar

```text
SECOP II contratos desde 2021
SECOP II adiciones desde 2021
SECOP II ejecucion desde 2021
DIVIPOLA municipios
        |
        v
Lote 1 y lote 2
        |
        v
Limpieza + cruces + texto no estructurado
        |
        v
Indice descriptivo de prioridad
        |
        v
MongoDB
  contratos_operativos
  alertas_revision
  dashboard_kpis
  dashboard_entidades
  dashboard_proveedores
  dashboard_temas
  metadata_pipeline
  indices: texto_busqueda, prioridad.nivel, entidad.nit, proveedor.documento
        |
        v
Dashboard / evidencias de consulta
```
    """),
    md("""
---
# Reto 0. Preparar el entorno

Ejecuten la celda. Si faltan paquetes, se instalan. Si ya existen, el notebook
continua.

**Evidencia:** la celda termina sin error.
    """),
    code("""
import sys
import subprocess
import importlib.util

paquetes = {
    "requests": "requests",
    "pandas": "pandas",
    "pymongo": "pymongo",
    "dns": "dnspython",
}

faltantes = [
    paquete
    for modulo, paquete in paquetes.items()
    if importlib.util.find_spec(modulo) is None
]

if faltantes:
    print("Instalando paquetes faltantes:", faltantes)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *faltantes])
else:
    print("Dependencias listas.")
    """),
    code("""
import os
import re
import json
import unicodedata
from pathlib import Path
from datetime import datetime, timezone

import requests
import pandas as pd
import numpy as np
from IPython.display import display

BASE = "https://www.datos.gov.co/resource"
FUENTES = {
    "contratos": f"{BASE}/jbjy-vk9h.json",
    "adiciones": f"{BASE}/cb9c-h8sn.json",
    "ejecucion": f"{BASE}/mfmm-jqmq.json",
    "divipola": f"{BASE}/gdxc-w37w.json",
}

FECHA_INICIO = "2021-01-01T00:00:00"
SALIDA = Path("salidas_taller_final")
SALIDA.mkdir(exist_ok=True)

def consultar_socrata(url, params=None, timeout=45):
    r = requests.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()

print("Fecha minima del reto:", FECHA_INICIO)
    """),
    md("""
---
# Reto 1. Probar que las fuentes sirven

No empiecen descargando datos grandes. Primero prueben que cada fuente responde
y que el filtro desde 2021 funciona.

**Evidencia:** cuatro muestras visibles: contratos, adiciones, ejecucion y DIVIPOLA.
    """),
    code("""
def muestra(nombre, params):
    datos = consultar_socrata(FUENTES[nombre], params)
    df = pd.DataFrame(datos)
    print(f"{nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
    display(df.head(3))
    return df

_contratos = muestra("contratos", {
    "$select": "id_contrato,fecha_de_firma,departamento,ciudad,valor_del_contrato,objeto_del_contrato",
    "$where": f"fecha_de_firma >= '{FECHA_INICIO}'",
    "$limit": 3,
})

_adiciones = muestra("adiciones", {
    "$select": "id_contrato,tipo,descripcion,fecharegistro",
    "$where": f"fecharegistro >= '{FECHA_INICIO}'",
    "$limit": 3,
})

_ejecucion = muestra("ejecucion", {
    "$select": "identificadorcontrato,fechacreacion,porcentaje_de_avance_real,estado_del_contrato",
    "$where": f"fechacreacion >= '{FECHA_INICIO}'",
    "$limit": 3,
})

_divipola = muestra("divipola", {"$limit": 3})
    """),
    md("""
**Checkpoint del profesor**

- Las tres fuentes SECOP muestran fechas desde 2021.
- DIVIPOLA muestra municipios con codigo y coordenadas.
- El equipo puede explicar para que sirve cada fuente.
    """),
    md("""
---
# Reto 2. Descargar dos lotes de contratos

El prototipo debe simular actualizacion. Por eso se usan dos lotes. El segundo
lote representa una nueva carga.

**Evidencia:** conteo de filas de `lote_1` y `lote_2`.
    """),
    code("""
BATCH_SIZE = 100

CONTRATOS_SELECT = ",".join([
    "id_contrato",
    "nombre_entidad",
    "nit_entidad",
    "departamento",
    "ciudad",
    "sector",
    "orden",
    "estado_contrato",
    "tipo_de_contrato",
    "modalidad_de_contratacion",
    "fecha_de_firma",
    "fecha_de_inicio_del_contrato",
    "fecha_de_fin_del_contrato",
    "ultima_actualizacion",
    "documento_proveedor",
    "proveedor_adjudicado",
    "valor_del_contrato",
    "valor_pagado",
    "dias_adicionados",
    "objeto_del_contrato",
])

def descargar_lote(offset, limit=BATCH_SIZE):
    params = {
        "$select": CONTRATOS_SELECT,
        "$where": f"fecha_de_firma >= '{FECHA_INICIO}'",
        "$limit": limit,
        "$offset": offset,
        "$order": "fecha_de_firma DESC",
    }
    return pd.DataFrame(consultar_socrata(FUENTES["contratos"], params))

lote_1 = descargar_lote(0)
lote_2 = descargar_lote(BATCH_SIZE)

print("lote_1:", lote_1.shape)
print("lote_2:", lote_2.shape)
display(lote_1.head())
    """),
    md("""
---
# Reto 3. Limpiar contratos y cruzar territorio

Conviertan fechas y valores. Luego intenten cruzar departamento/municipio con
DIVIPOLA.

**Evidencia:** tabla con `id_contrato`, municipio, valor y codigo DIVIPOLA.
    """),
    code("""
def normalizar_texto(x):
    if pd.isna(x):
        return ""
    x = str(x).strip().upper()
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))
    return " ".join(x.split())

def preparar_contratos(df):
    out = df.copy()
    for col in ["fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "ultima_actualizacion"]:
        out[col] = pd.to_datetime(out[col], errors="coerce")
    for col in ["valor_del_contrato", "valor_pagado", "dias_adicionados"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    out["departamento_norm"] = out["departamento"].apply(normalizar_texto)
    out["ciudad_norm"] = out["ciudad"].apply(normalizar_texto)
    return out

divipola = pd.DataFrame(consultar_socrata(FUENTES["divipola"], {"$limit": 1200}))
divipola["departamento_norm"] = divipola["dpto"].apply(normalizar_texto)
divipola["ciudad_norm"] = divipola["nom_mpio"].apply(normalizar_texto)
divipola["latitud_num"] = pd.to_numeric(divipola["latitud"].str.replace(",", ".", regex=False), errors="coerce")
divipola["longitud_num"] = pd.to_numeric(divipola["longitud"].str.replace(",", ".", regex=False), errors="coerce")

def cruzar_territorio(df):
    base = preparar_contratos(df)
    return base.merge(
        divipola[[
            "cod_dpto", "cod_mpio", "dpto", "nom_mpio",
            "departamento_norm", "ciudad_norm", "latitud_num", "longitud_num"
        ]],
        on=["departamento_norm", "ciudad_norm"],
        how="left",
    )

lote_1_geo = cruzar_territorio(lote_1)
print("Cruces DIVIPOLA lote_1:", lote_1_geo["cod_mpio"].notna().sum(), "de", len(lote_1_geo))
display(lote_1_geo[["id_contrato", "departamento", "ciudad", "valor_del_contrato", "cod_mpio"]].head(10))
    """),
    md("""
**Checkpoint del profesor**

Si hay contratos sin DIVIPOLA, no es falla automatica. El equipo debe reportar
el porcentaje de cruce y explicar que los nombres territoriales reales no
siempre coinciden.
    """),
    md("""
---
# Reto 4. Integrar adiciones y ejecucion

Para cada lote, busquen adiciones y ejecucion solo de los contratos descargados.
Esto hace que el flujo sea incremental.

**Evidencia:** tabla con numero de adiciones y ultimo avance real.
    """),
    code("""
def construir_in_clause(ids):
    ids = [str(x).replace("'", "") for x in ids if pd.notna(x)]
    if not ids:
        return "('')"
    return "(" + ",".join([f"'{x}'" for x in ids]) + ")"

def descargar_adiciones(ids):
    params = {
        "$select": "id_contrato,tipo,descripcion,fecharegistro",
        "$where": f"fecharegistro >= '{FECHA_INICIO}' AND id_contrato in {construir_in_clause(ids)}",
        "$limit": 5000,
    }
    return pd.DataFrame(consultar_socrata(FUENTES["adiciones"], params))

def descargar_ejecucion(ids):
    params = {
        "$select": "identificadorcontrato,fechacreacion,porcentaje_de_avance_real,estado_del_contrato",
        "$where": f"fechacreacion >= '{FECHA_INICIO}' AND identificadorcontrato in {construir_in_clause(ids)}",
        "$limit": 5000,
    }
    return pd.DataFrame(consultar_socrata(FUENTES["ejecucion"], params))

def resumir_adiciones(df):
    if df.empty:
        return pd.DataFrame(columns=["id_contrato", "numero_adiciones", "ultima_adicion", "descripcion_adiciones"])
    tmp = df.copy()
    tmp["fecharegistro"] = pd.to_datetime(tmp["fecharegistro"], errors="coerce")
    return (
        tmp.groupby("id_contrato")
        .agg(
            numero_adiciones=("id_contrato", "size"),
            ultima_adicion=("fecharegistro", "max"),
            descripcion_adiciones=("descripcion", lambda s: " | ".join(s.dropna().astype(str).head(3))),
        )
        .reset_index()
    )

def resumir_ejecucion(df):
    if df.empty:
        return pd.DataFrame(columns=["id_contrato", "ultimo_avance_real", "estado_ejecucion", "ultima_fecha_ejecucion"])
    tmp = df.copy()
    tmp["fechacreacion"] = pd.to_datetime(tmp["fechacreacion"], errors="coerce")
    tmp["porcentaje_de_avance_real"] = pd.to_numeric(tmp["porcentaje_de_avance_real"], errors="coerce")
    tmp = tmp.sort_values("fechacreacion").drop_duplicates("identificadorcontrato", keep="last")
    return tmp.rename(columns={
        "identificadorcontrato": "id_contrato",
        "porcentaje_de_avance_real": "ultimo_avance_real",
        "estado_del_contrato": "estado_ejecucion",
        "fechacreacion": "ultima_fecha_ejecucion",
    })[["id_contrato", "ultimo_avance_real", "estado_ejecucion", "ultima_fecha_ejecucion"]]

def enriquecer_lote(df):
    geo = cruzar_territorio(df)
    ids = geo["id_contrato"].dropna().unique().tolist()
    adiciones = descargar_adiciones(ids)
    ejecucion = descargar_ejecucion(ids)
    out = (
        geo
        .merge(resumir_adiciones(adiciones), on="id_contrato", how="left")
        .merge(resumir_ejecucion(ejecucion), on="id_contrato", how="left")
    )
    out["numero_adiciones"] = out["numero_adiciones"].fillna(0).astype(int)
    out["ultimo_avance_real"] = out["ultimo_avance_real"].fillna(0)
    return out, adiciones, ejecucion

lote_1_enriquecido, adiciones_1, ejecucion_1 = enriquecer_lote(lote_1)
display(lote_1_enriquecido[[
    "id_contrato", "valor_del_contrato", "numero_adiciones",
    "ultimo_avance_real", "estado_ejecucion"
]].head(10))
    """),
    md("""
---
# Reto 5. Hacer claro el dato no estructurado

Este es el reto clave.

Un dato estructurado tiene columnas limpias: valor, fecha, municipio, NIT.  
Un dato no estructurado es texto libre: el objeto contractual o la descripcion
de una adicion.

Ejemplo:

```text
Prestacion de servicios profesionales para apoyar la gestion administrativa...
```

Ese texto no dice directamente "tema = servicios profesionales". Ustedes deben
crear una regla simple que lea el texto y detecte temas.

**Tarea del equipo**

1. Crear un campo `texto_busqueda` uniendo objeto contractual y descripcion de adiciones.
2. Limpiar ese texto.
3. Detectar temas con palabras clave.
4. Guardar los temas en MongoDB.
5. Mostrar un resumen por tema para el dashboard.

**Evidencia:** tabla con `id_contrato`, `texto_busqueda` y `temas_detectados`.
    """),
    code("""
TEMAS = {
    "alimentacion": ["ALIMENTACION", "ALIMENTOS", "CAFETERIA", "RESTAURANTE", "COMEDOR"],
    "infraestructura": ["OBRA", "VIAS", "VIA", "CONSTRUCCION", "MANTENIMIENTO", "INTERVENTORIA"],
    "salud": ["SALUD", "HOSPITAL", "MEDICAMENTO", "AMBULANCIA", "CLINICA"],
    "educacion": ["COLEGIO", "ESTUDIANTE", "ESCOLAR", "EDUCATIVO", "DOCENTE"],
    "tecnologia": ["SOFTWARE", "LICENCIA", "SISTEMA", "COMPUTADOR", "TECNOLOGIA", "PLATAFORMA"],
    "servicios_profesionales": ["PRESTACION DE SERVICIOS", "APOYO A LA GESTION", "CONSULTORIA", "ASESORIA"],
}

def limpiar_texto(x):
    if pd.isna(x):
        return ""
    x = normalizar_texto(x)
    x = re.sub(r"[^A-Z0-9 Ñ]", " ", x)
    return " ".join(x.split())

def detectar_temas(texto):
    limpio = limpiar_texto(texto)
    encontrados = []
    for tema, palabras in TEMAS.items():
        if any(p in limpio for p in palabras):
            encontrados.append(tema)
    return encontrados if encontrados else ["sin_tema_detectado"]

def agregar_texto(df):
    out = df.copy()
    out["objeto_texto"] = out["objeto_del_contrato"].fillna("")
    out["adiciones_texto"] = out["descripcion_adiciones"].fillna("")
    out["texto_busqueda"] = (out["objeto_texto"] + " " + out["adiciones_texto"]).apply(limpiar_texto)
    out["temas_detectados"] = out["texto_busqueda"].apply(detectar_temas)
    return out

lote_1_texto = agregar_texto(lote_1_enriquecido)
display(lote_1_texto[["id_contrato", "texto_busqueda", "temas_detectados"]].head(10))
    """),
    code("""
def resumen_temas(df):
    filas = []
    for _, row in df.iterrows():
        for tema in row["temas_detectados"]:
            filas.append({
                "tema": tema,
                "id_contrato": row["id_contrato"],
                "valor_del_contrato": row["valor_del_contrato"],
            })
    base = pd.DataFrame(filas)
    if base.empty:
        return pd.DataFrame(columns=["tema", "total_contratos", "valor_total"])
    return (
        base.groupby("tema")
        .agg(
            total_contratos=("id_contrato", "count"),
            valor_total=("valor_del_contrato", "sum"),
        )
        .reset_index()
        .sort_values("total_contratos", ascending=False)
    )

display(resumen_temas(lote_1_texto))
    """),
    md("""
**Checkpoint del profesor**

El equipo debe poder explicar con sus palabras:

- que columna es texto no estructurado;
- como la limpio;
- que palabras clave uso;
- que errores puede cometer este metodo;
- como se vera este resultado en MongoDB y en el dashboard.
    """),
    md("""
---
# Reto 6. Crear un indice de prioridad

Construyan un puntaje simple. Pueden usar estas reglas o modificarlas, pero
deben explicarlas.

**Evidencia:** ranking de contratos con prioridad alta, media o baja.
    """),
    code("""
def calcular_prioridad(df):
    out = df.copy()
    valor = out["valor_del_contrato"].fillna(0)
    p75 = valor.quantile(0.75) if len(valor) else 0
    p90 = valor.quantile(0.90) if len(valor) else 0

    out["puntaje_valor"] = np.select([valor >= p90, valor >= p75], [25, 15], default=0)
    out["puntaje_adiciones"] = np.select([out["numero_adiciones"] >= 2, out["numero_adiciones"] == 1], [20, 10], default=0)
    out["puntaje_ejecucion"] = np.where((out["ultimo_avance_real"] < 50) & (valor > p75), 15, 0)
    out["puntaje_modalidad"] = np.where(
        out["modalidad_de_contratacion"].fillna("").str.contains("Directa|Mínima|Minima", case=False, regex=True),
        10,
        0,
    )
    out["puntaje_texto"] = np.where(out["temas_detectados"].apply(lambda x: "sin_tema_detectado" in x), 5, 0)
    out["indice_prioridad_revision"] = (
        out["puntaje_valor"] +
        out["puntaje_adiciones"] +
        out["puntaje_ejecucion"] +
        out["puntaje_modalidad"] +
        out["puntaje_texto"]
    ).clip(0, 100)
    out["nivel_prioridad"] = pd.cut(
        out["indice_prioridad_revision"],
        bins=[-1, 39, 69, 100],
        labels=["baja", "media", "alta"],
    ).astype(str)
    return out

lote_1_scored = calcular_prioridad(lote_1_texto)
display(lote_1_scored.sort_values("indice_prioridad_revision", ascending=False)[[
    "id_contrato", "nombre_entidad", "proveedor_adjudicado",
    "valor_del_contrato", "numero_adiciones", "temas_detectados",
    "indice_prioridad_revision", "nivel_prioridad"
]].head(15))
    """),
    md("""
---
# Reto 7. Disenar el modelo documental NoSQL

Aqui aparece el reto NoSQL. No basta con guardar una tabla como JSON. Deben
decidir que informacion queda embebida dentro del documento para que el usuario
pueda consultar rapido.

Decision de modelo:

| Parte del documento | Decision NoSQL | Razon |
|---|---|---|
| entidad | embebida | se consulta junto con el contrato |
| proveedor | embebido | permite ver ficha del contrato sin `JOIN` |
| territorio | embebido | facilita filtros y dashboard territorial |
| adiciones | embebidas/resumidas | son eventos ligados al contrato |
| ejecucion | embebida/resumida | da estado operativo del contrato |
| texto no estructurado | embebido | permite busqueda textual y temas |
| prioridad | embebida | alimenta alertas y tablero |

**Evidencia:** un documento JSON de ejemplo con texto, temas y prioridad.
    """),
    code("""
def limpiar_nan(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor.isoformat()
    if isinstance(valor, np.generic):
        return valor.item()
    return valor

def contrato_documento(row, lote):
    return {
        "_id": row["id_contrato"],
        "id_contrato": row["id_contrato"],
        "lote": lote,
        "fecha_ingesta": datetime.now(timezone.utc).isoformat(),
        "valor": limpiar_nan(row.get("valor_del_contrato")),
        "objeto": limpiar_nan(row.get("objeto_del_contrato")),
        "entidad": {
            "nombre": limpiar_nan(row.get("nombre_entidad")),
            "nit": limpiar_nan(row.get("nit_entidad")),
            "sector": limpiar_nan(row.get("sector")),
        },
        "proveedor": {
            "nombre": limpiar_nan(row.get("proveedor_adjudicado")),
            "documento": limpiar_nan(row.get("documento_proveedor")),
        },
        "territorio": {
            "departamento": limpiar_nan(row.get("departamento")),
            "municipio": limpiar_nan(row.get("ciudad")),
            "codigo_divipola": limpiar_nan(row.get("cod_mpio")),
            "latitud": limpiar_nan(row.get("latitud_num")),
            "longitud": limpiar_nan(row.get("longitud_num")),
        },
        "adiciones": {
            "numero": limpiar_nan(row.get("numero_adiciones")),
            "ultima": limpiar_nan(row.get("ultima_adicion")),
            "descripcion": limpiar_nan(row.get("descripcion_adiciones")),
        },
        "ejecucion": {
            "avance_real": limpiar_nan(row.get("ultimo_avance_real")),
            "estado": limpiar_nan(row.get("estado_ejecucion")),
        },
        "texto_no_estructurado": {
            "texto_busqueda": limpiar_nan(row.get("texto_busqueda")),
            "temas_detectados": limpiar_nan(row.get("temas_detectados")),
        },
        "prioridad": {
            "indice": limpiar_nan(row.get("indice_prioridad_revision")),
            "nivel": limpiar_nan(row.get("nivel_prioridad")),
        },
        "estado_revision": "pendiente",
    }

docs_lote_1 = [
    contrato_documento(row, "lote_1")
    for _, row in lote_1_scored.iterrows()
    if pd.notna(row.get("id_contrato"))
]

docs_lote_1[0]
    """),
    md("""
---
# Reto 8. Cargar MongoDB y demostrar capacidades NoSQL

Si tienen MongoDB Atlas o local, carguen con `upsert`. Si no, generen JSON y
carguen MongoDB antes de la sustentacion.

El reto NoSQL minimo incluye:

1. Cargar documentos con estructura anidada.
2. Usar `upsert` para no duplicar contratos.
3. Crear indices sobre campos anidados.
4. Crear indice de texto sobre `texto_no_estructurado.texto_busqueda`.
5. Ejecutar consultas por prioridad, proveedor, entidad y texto.
6. Ejecutar una agregacion con `$group` para alimentar el dashboard.

**Evidencia:** conteos de carga, indices creados y al menos cuatro consultas
NoSQL ejecutadas.
    """),
    code("""
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "observatorio_secop_2021"
mongo_ok = False
db = None

try:
    from pymongo import MongoClient, UpdateOne
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DB_NAME]
    mongo_ok = True
    print("MongoDB conectado.")
except Exception as e:
    print("MongoDB no conectado. Se usara respaldo JSON.")
    print("Detalle:", e)

def cargar_contratos(documentos, lote):
    if mongo_ok:
        ops = [UpdateOne({"_id": d["_id"]}, {"$set": d}, upsert=True) for d in documentos]
        result = db.contratos_operativos.bulk_write(ops)
        db.metadata_pipeline.insert_one({
            "lote": lote,
            "fecha": datetime.now(timezone.utc).isoformat(),
            "documentos": len(documentos),
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": len(result.upserted_ids),
        })
        return {"mongo_ok": True, "documentos": len(documentos), "upserted": len(result.upserted_ids)}

    ruta = SALIDA / f"{lote}_contratos_operativos.json"
    ruta.write_text(json.dumps(documentos, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"mongo_ok": False, "documentos": len(documentos), "archivo": str(ruta)}

resultado_carga_1 = cargar_contratos(docs_lote_1, "lote_1")
resultado_carga_1
    """),
    code("""
# Evidencia NoSQL: indices y consultas.
# Si MongoDB no esta conectado, esta celda deja claro que debe ejecutarse
# en la entrega final con Atlas o Mongo local.

if mongo_ok:
    db.contratos_operativos.create_index("prioridad.nivel")
    db.contratos_operativos.create_index("entidad.nit")
    db.contratos_operativos.create_index("proveedor.documento")
    db.contratos_operativos.create_index([("texto_no_estructurado.texto_busqueda", "text")])

    print("Indices creados:")
    for idx in db.contratos_operativos.list_indexes():
        print(idx["name"], idx["key"])

    print("\\nConsulta 1: contratos de prioridad alta")
    display(pd.DataFrame(list(db.contratos_operativos.find(
        {"prioridad.nivel": "alta"},
        {"_id": 0, "id_contrato": 1, "valor": 1, "entidad.nombre": 1, "prioridad": 1}
    ).limit(5))))

    print("\\nConsulta 2: busqueda textual por tema")
    display(pd.DataFrame(list(db.contratos_operativos.find(
        {"$text": {"$search": "salud tecnologia infraestructura"}},
        {"_id": 0, "id_contrato": 1, "objeto": 1, "texto_no_estructurado.temas_detectados": 1}
    ).limit(5))))

    print("\\nAgregacion: valor por tema detectado")
    pipeline_temas = [
        {"$unwind": "$texto_no_estructurado.temas_detectados"},
        {"$group": {
            "_id": "$texto_no_estructurado.temas_detectados",
            "total_contratos": {"$sum": 1},
            "valor_total": {"$sum": "$valor"}
        }},
        {"$sort": {"total_contratos": -1}}
    ]
    display(pd.DataFrame(list(db.contratos_operativos.aggregate(pipeline_temas))))
else:
    print("MongoDB no esta conectado.")
    print("Para la entrega final deben ejecutar esta celda con MongoDB y anexar evidencia de indices, consultas y agregacion.")
    """),
    md("""
---
# Reto 9. Crear colecciones para dashboard

El dashboard debe salir de datos preparados, no de calculos improvisados.

**Evidencia:** tablas o colecciones de KPIs, entidades, proveedores, temas y alertas.
    """),
    code("""
def frames_dashboard(df):
    kpis = pd.DataFrame([{
        "fecha_calculo": datetime.now(timezone.utc).isoformat(),
        "total_contratos": int(len(df)),
        "valor_total": float(df["valor_del_contrato"].sum()),
        "contratos_con_adiciones": int((df["numero_adiciones"] > 0).sum()),
        "prioridad_alta": int((df["nivel_prioridad"] == "alta").sum()),
    }])

    entidades = (
        df.groupby(["nit_entidad", "nombre_entidad"], dropna=False)
        .agg(
            total_contratos=("id_contrato", "count"),
            valor_total=("valor_del_contrato", "sum"),
            prioridad_promedio=("indice_prioridad_revision", "mean"),
        )
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    proveedores = (
        df.groupby(["documento_proveedor", "proveedor_adjudicado"], dropna=False)
        .agg(
            total_contratos=("id_contrato", "count"),
            valor_total=("valor_del_contrato", "sum"),
            entidades_distintas=("nit_entidad", "nunique"),
        )
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    temas = resumen_temas(df)

    alertas = df[df["nivel_prioridad"].isin(["media", "alta"])][[
        "id_contrato", "nombre_entidad", "proveedor_adjudicado",
        "valor_del_contrato", "numero_adiciones", "temas_detectados",
        "indice_prioridad_revision", "nivel_prioridad"
    ]].sort_values("indice_prioridad_revision", ascending=False)

    return {
        "dashboard_kpis": kpis,
        "dashboard_entidades": entidades,
        "dashboard_proveedores": proveedores,
        "dashboard_temas": temas,
        "alertas_revision": alertas,
    }

dash_1 = frames_dashboard(lote_1_scored)
for nombre, frame in dash_1.items():
    print(nombre, frame.shape)
    display(frame.head(5))
    """),
    code("""
def guardar_dashboard(frames, lote):
    if mongo_ok:
        for nombre, frame in frames.items():
            registros = json.loads(frame.to_json(orient="records", force_ascii=False, date_format="iso"))
            db[nombre].delete_many({"lote": lote})
            for r in registros:
                r["lote"] = lote
                r["fecha_carga"] = datetime.now(timezone.utc).isoformat()
            if registros:
                db[nombre].insert_many(registros)
        return {"mongo_ok": True, "colecciones": list(frames.keys())}

    archivos = {}
    for nombre, frame in frames.items():
        ruta = SALIDA / f"{lote}_{nombre}.json"
        ruta.write_text(frame.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
        archivos[nombre] = str(ruta)
    return {"mongo_ok": False, "archivos": archivos}

resultado_dashboard_1 = guardar_dashboard(dash_1, "lote_1")
resultado_dashboard_1
    """),
    md("""
---
# Reto 10. Ejecutar segunda carga

Repitan el proceso con `lote_2`. El dashboard debe cambiar porque entran nuevos
contratos.

**Evidencia:** comparacion entre lote 1 y lote 2.
    """),
    code("""
lote_2_enriquecido, adiciones_2, ejecucion_2 = enriquecer_lote(lote_2)
lote_2_texto = agregar_texto(lote_2_enriquecido)
lote_2_scored = calcular_prioridad(lote_2_texto)
docs_lote_2 = [
    contrato_documento(row, "lote_2")
    for _, row in lote_2_scored.iterrows()
    if pd.notna(row.get("id_contrato"))
]

resultado_carga_2 = cargar_contratos(docs_lote_2, "lote_2")
dash_2 = frames_dashboard(lote_2_scored)
resultado_dashboard_2 = guardar_dashboard(dash_2, "lote_2")

print("Carga lote 2:", resultado_carga_2)
print("Dashboard lote 2:", resultado_dashboard_2)
display(lote_2_scored.sort_values("indice_prioridad_revision", ascending=False).head(10))
    """),
    md("""
## Comparacion obligatoria

Completen esta tabla en su informe:

| Indicador | Lote 1 | Lote 2 | Cambio observado |
|---|---:|---:|---|
| Total contratos |  |  |  |
| Valor total |  |  |  |
| Contratos con adiciones |  |  |  |
| Prioridad alta |  |  |  |
| Tema mas frecuente |  |  |  |
    """),
    md("""
---
# Reto 11. Consultas que debe soportar la solucion

Si MongoDB esta conectado, ejecuten consultas. Si no, expliquen como se harian
y entreguen evidencia con JSON.
    """),
    code("""
if mongo_ok:
    print("Contratos con prioridad alta")
    display(pd.DataFrame(list(db.contratos_operativos.find(
        {"prioridad.nivel": "alta"},
        {"_id": 0, "id_contrato": 1, "valor": 1, "entidad.nombre": 1, "proveedor.nombre": 1, "prioridad": 1}
    ).limit(10))))

    print("Temas detectados")
    display(pd.DataFrame(list(db.dashboard_temas.find({}, {"_id": 0}).sort("total_contratos", -1).limit(10))))

    print("Indice de texto recomendado:")
    print('db.contratos_operativos.create_index([("texto_no_estructurado.texto_busqueda", "text")])')
else:
    print("MongoDB no conectado. Revisen archivos en:", SALIDA.resolve())
    """),
    md("""
---
# Dashboard minimo

El dashboard debe tener:

1. KPI de contratos cargados.
2. KPI de valor total.
3. Tabla de alertas.
4. Ranking de entidades.
5. Ranking de proveedores.
6. Grafico de temas detectados desde texto no estructurado.
7. Evidencia de actualizacion despues del lote 2.

MongoDB Atlas Charts es recomendado, pero no obligatorio si el equipo demuestra
otra herramienta conectada a las colecciones o a los JSON generados.
    """),
    md("""
---
## PARTE 5 -- Rúbrica de Evaluación

El taller debe realizarse en grupos de máximo tres estudiantes. Deberán
compartir el notebook ejecutado, la evidencia de MongoDB/dashboard y el informe
ejecutivo en la fecha indicada por el profesor, enviándolo con el asunto:

`[BigData] Taller Final SECOP MongoDB`

Adicionalmente, deben informar el **día y hora de descarga** de los datos,
porque SECOP II recibe nuevos registros y actualizaciones diariamente.

**Total: 100 puntos + 10 puntos bonus**

### Componentes evaluables

| Componente | Producto esperado | Puntos |
|---|---|---:|
| **1. Fuentes desde 2021** | Prueba de contratos, adiciones y ejecución filtradas desde `2021-01-01`; registro de fecha/hora de descarga. | 10 |
| **2. Limpieza e integración** | Fechas, valores y texto convertidos; cruce con DIVIPOLA; integración con adiciones y ejecución. | 15 |
| **3. Datos no estructurados** | Campo `texto_busqueda`, reglas de temas, `temas_detectados` y resumen por tema. | 15 |
| **4. Índice de prioridad** | Reglas transparentes, ranking reproducible y lectura sin afirmar fraude. | 10 |
| **5. Reto NoSQL MongoDB** | Modelo documental anidado, `upsert`, índices, consulta por campos anidados, búsqueda textual y agregación. | 20 |
| **6. Dashboard operativo** | KPIs, alertas, entidades, proveedores, temas y evidencia de cambio entre lote 1 y lote 2. | 15 |
| **7. Informe ejecutivo** | Hallazgos, límites, recomendaciones y explicación de qué revisar primero. | 10 |
| **8. Reproducibilidad** | Notebook/script corre de nuevo, rutas claras, sin resultados pegados a mano. | 5 |

**Bonus +10:** usar un volumen ampliado de datos, por ejemplo 100.000+ contratos
desde 2021, o automatizar la ejecución con Airflow/Databricks Workflows sin
romper la reproducibilidad del notebook base.

---

### Criterios generales

| Criterio | Descripción | Puntos asociados |
|----------|-------------|------------------|
| **Limpieza de datos** | Convierte fechas, valores y texto correctamente. Maneja nulos sin eliminar filas innecesariamente. Normaliza municipio, entidad, proveedor y texto de búsqueda. | Incluido en componentes 2 y 3 |
| **Integración de bases** | Une contratos, adiciones, ejecución y DIVIPOLA con llaves claras. Reporta cruces fallidos y no los oculta. | Componente 2 |
| **Uso de datos no estructurados** | Usa texto libre del objeto contractual y/o adiciones. Construye `texto_busqueda`, detecta temas y explica limitaciones del método. | Componente 3 |
| **Uso correcto de NoSQL** | No guarda una tabla plana. Diseña documentos anidados, crea índices, usa `upsert`, ejecuta consultas por campos anidados y agregaciones. | Componente 5 |
| **Correctitud del resultado** | Los conteos, rankings, valores y alertas son reproducibles y coherentes con las reglas implementadas. | Todos los componentes |
| **Visualización / dashboard** | Dashboard con títulos claros, filtros útiles y evidencia de actualización después de la segunda carga. | Componente 6 |
| **Interpretación** | Explica qué muestra el resultado, qué implica para seguimiento público y qué no se puede concluir todavía. | Componente 7 |

---

### Tabla de niveles por criterio

| Criterio | Excelente (100%) | Satisfactorio (70%) | Insuficiente (40%) | No entregado (0%) |
|----------|-----------------|---------------------|--------------------|------------------|
| **Fuentes** | Todas las fuentes consultadas desde 2021, con fecha/hora de descarga documentada | Fuentes principales consultadas, falta una evidencia menor | Filtro temporal incompleto o fuente sin verificar | No consulta fuentes |
| **Limpieza e integración** | Tipos correctos, cruces documentados, nulos manejados y datos integrados | Integración funcional con algunos problemas menores | Integración parcial o con errores de tipo | Sin integración |
| **Texto no estructurado** | `texto_busqueda` claro, temas explicados, resumen por tema y limitaciones | Temas detectados pero con explicación limitada | Solo copia texto sin análisis real | No usa texto |
| **NoSQL MongoDB** | Documento anidado, índices, `upsert`, búsqueda textual, agregaciones y consultas evidenciadas | Carga documentos y algunas consultas, pero faltan índices o agregaciones | MongoDB usado como tabla plana o solo JSON | No usa NoSQL |
| **Prioridad** | Reglas claras, ranking reproducible, interpretación responsable | Ranking funcional con reglas poco justificadas | Ranking arbitrario o difícil de reproducir | Sin ranking |
| **Dashboard** | Conectado a MongoDB o datos exportados, muestra cambio lote 1 vs lote 2 | Dashboard básico con pocos filtros | Gráficas sueltas sin actualización clara | Sin dashboard |
| **Informe** | Ejecutivo, claro, con hallazgos, límites y recomendación de revisión | Describe resultados pero con poca profundidad | Informe superficial o sin límites | Sin informe |

---

### Penalizaciones

| Situación | Penalización |
|-----------|-------------:|
| No informar fecha/hora de descarga | -5 puntos |
| No filtrar desde `2021-01-01` | -15 puntos |
| Resultados hardcodeados o pegados sin computar | -20 puntos |
| Código que no corre por errores no explicados | -10 puntos |
| Usar MongoDB solo como tabla plana sin documentos anidados | -10 puntos |
| No demostrar `upsert` o actualización entre lote 1 y lote 2 | -10 puntos |
| No usar texto no estructurado | -15 puntos |
| Afirmar fraude/corrupción sin evidencia causal | -10 puntos |
| No entregar dashboard ni evidencia equivalente | -15 puntos |

---

### Nota sobre tamaño de descarga

Para clase se trabaja con dos micro-lotes de 100 contratos para validar el flujo.
Para la entrega final, cada equipo debe ampliar el volumen según su capacidad de
cómputo. Recomendación mínima:

- **mínimo aceptable:** 2 lotes de 1.000 contratos;
- **bueno:** 20.000+ contratos desde 2021;
- **excelente/bonus:** 100.000+ contratos desde 2021 o descarga paginada amplia.

Ejemplo de descarga paginada controlada:

```python
TOTAL_FILAS_OBJETIVO = 100_000
TAMANO_LOTE = 10_000
offsets = list(range(0, TOTAL_FILAS_OBJETIVO, TAMANO_LOTE))

partes = []
for offset in offsets:
    parte = descargar_lote(offset=offset, limit=TAMANO_LOTE)
    partes.append(parte)
    print(f"Descargadas {min(offset + TAMANO_LOTE, TOTAL_FILAS_OBJETIVO):,} filas")

contratos_ampliados = pd.concat(partes, ignore_index=True)
```

No sobrecarguen la API. Si hacen descarga amplia, documenten el día, hora,
tamaño descargado y cualquier error de red.

---

# Matriz de verificacion del profesor

| Criterio | Evidencia esperada | Cumple |
|---|---|---|
| Fuentes desde 2021 | Muestras filtradas de contratos, adiciones y ejecucion |  |
| Dos lotes | Conteos de lote 1 y lote 2 |  |
| Cruce territorial | Conteo de contratos con DIVIPOLA |  |
| Integracion | Adiciones y avance de ejecucion por contrato |  |
| Texto no estructurado | `texto_busqueda`, `temas_detectados`, resumen por tema |  |
| Prioridad | Ranking y reglas explicadas |  |
| MongoDB/JSON | Documento completo de contrato operativo |  |
| Dashboard | KPIs, alertas, entidades, proveedores y temas |  |
| Actualizacion | Comparacion entre lote 1 y lote 2 |  |
| Interpretacion | No afirma fraude; explica limites |  |
    """),
    md("""
## Cierre del reto

La entrega debe convencer al profesor de que el equipo construyo un prototipo
operativo, no solo un analisis aislado.

La frase final del informe debe responder:

> Que debe revisar primero una oficina de control interno y que evidencia del
> pipeline soporta esa recomendacion?

Referencias:

- SECOP II contratos: https://www.datos.gov.co/resource/jbjy-vk9h.json
- SECOP II adiciones: https://www.datos.gov.co/resource/cb9c-h8sn.json
- SECOP II ejecucion: https://www.datos.gov.co/resource/mfmm-jqmq.json
- DIVIPOLA: https://www.datos.gov.co/resource/gdxc-w37w.json
- API Socrata: https://dev.socrata.com/
- MongoDB Atlas Charts: https://www.mongodb.com/docs/charts/
    """),
]


if __name__ == "__main__":
    validate(cells)
    save(cells, "Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb")
