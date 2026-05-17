# -*- coding: utf-8 -*-
"""
Genera Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb

Guia de taller final: observatorio operativo de contratacion publica con
SECOP II desde 2021, texto no estructurado, MongoDB y dashboard.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header


cells = [
    *uce_header(
        title="Taller final: observatorio operativo de contratacion publica con MongoDB",
        session=13,
        github_path="main/Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb",
        nota_plataforma="Jupyter, Colab o Databricks. MongoDB Atlas recomendado para dashboard.",
    ),
    md("""
# Guia de taller

Este taller construye una solucion aplicada para un problema real de analitica
publica: una oficina de control interno necesita revisar contratacion publica
reciente, detectar casos que merecen seguimiento y consultar la informacion sin
reconstruir cruces manuales cada vez.

El equipo trabajara solo con informacion desde `2021-01-01`.

No se espera demostrar fraude ni irregularidades. El producto debe priorizar
revision con reglas descriptivas, trazables y explicables.
    """),
    md("""
## Contexto de negocio

Una entidad publica recibe solicitudes frecuentes de seguimiento:

- revisar contratos nuevos de alto valor;
- identificar contratos con adiciones o modificaciones;
- consultar rapidamente la ficha de un proveedor;
- saber que entidades concentran mayor valor contratado;
- buscar contratos por temas escritos en lenguaje natural, por ejemplo
  alimentacion, salud, infraestructura, educacion o tecnologia;
- presentar un tablero actualizado despues de cada nueva carga.

El problema no es solo tecnico. La informacion esta distribuida en varias bases:
contratos, adiciones, ejecucion contractual y territorio. Ademas, una parte
importante viene como texto no estructurado en el objeto contractual y en las
descripciones de adiciones.

El resultado del taller debe funcionar como un pequeno observatorio operativo.
    """),
    md("""
## Producto que debe entregar cada equipo

Al finalizar, cada equipo debe entregar una carpeta o repositorio con:

1. Notebook ejecutado con evidencia de consulta de fuentes desde 2021.
2. Diagrama de arquitectura seguido por el equipo.
3. Diccionario corto de datos usados.
4. Script o notebook de ingesta y transformacion.
5. Base MongoDB cargada o evidencia equivalente de carga.
6. Colecciones MongoDB para consulta operativa y dashboard.
7. Dashboard conectado a MongoDB o capturas verificables.
8. Evidencia de dos cargas: `lote_1` y `lote_2`.
9. Informe ejecutivo de maximo 3 paginas con hallazgos, limites y recomendaciones.

Airflow es opcional. Si el equipo lo usa, debe ser una extension de la solucion,
no el centro del taller.
    """),
    md("""
## Arquitectura que deben seguir

```text
Datos Abiertos Colombia
  - SECOP II contratos
  - SECOP II adiciones
  - SECOP II ejecucion
  - DIVIPOLA municipios
        |
        v
Micro-batch 1 y Micro-batch 2
        |
        v
Limpieza y normalizacion
  - fechas
  - valores monetarios
  - entidad/proveedor
  - departamento/municipio
        |
        v
Enriquecimiento
  - cruce territorial
  - resumen de adiciones
  - ultimo avance de ejecucion
  - temas desde texto no estructurado
        |
        v
Indice descriptivo de prioridad
        |
        v
MongoDB
  - contratos_operativos
  - alertas_revision
  - dashboard_kpis
  - dashboard_entidades
  - dashboard_proveedores
  - dashboard_temas
  - metadata_pipeline
        |
        v
Dashboard operativo
  - KPIs
  - alertas
  - proveedores
  - entidades
  - temas detectados
```

La arquitectura debe aparecer en la entrega del equipo. Puede ser este diagrama
adaptado, una imagen, o un diagrama propio, pero debe conservar las mismas capas.
    """),
    md("""
## Fuentes obligatorias

| Fuente | Endpoint | Uso |
|---|---|---|
| SECOP II contratos electronicos | `https://www.datos.gov.co/resource/jbjy-vk9h.json` | contratos, entidad, proveedor, valor, fechas, objeto |
| SECOP II adiciones | `https://www.datos.gov.co/resource/cb9c-h8sn.json` | eventos de modificacion o adicion |
| SECOP II ejecucion | `https://www.datos.gov.co/resource/mfmm-jqmq.json` | avance y estado de ejecucion |
| DIVIPOLA municipios | `https://www.datos.gov.co/resource/gdxc-w37w.json` | departamento, municipio, codigo y coordenadas |

El equipo puede agregar poblacion, IPM u otra fuente social, pero esas fuentes
son extension. El taller base se verifica con las cuatro fuentes anteriores.
    """),
    md("""
## Metodologia de trabajo

El taller se desarrolla en siete etapas. Cada etapa deja una evidencia que el
profesor puede revisar.

| Etapa | Trabajo del equipo | Evidencia verificable |
|---|---|---|
| 1. Verificar fuentes | Probar endpoints y filtro desde 2021 | tabla con filas de muestra por fuente |
| 2. Descargar micro-batch | Descargar `lote_1` y `lote_2` | conteo de contratos por lote |
| 3. Limpiar datos | Convertir fechas, valores y textos | muestra de datos limpios |
| 4. Enriquecer | Unir contratos con adiciones, ejecucion y DIVIPOLA | tabla de contratos enriquecidos |
| 5. Usar texto | Detectar temas desde objeto contractual | tabla con `temas_detectados` |
| 6. Cargar MongoDB | Crear o actualizar documentos con `upsert` | conteos de carga y metadata |
| 7. Dashboard | Mostrar KPIs, alertas y temas | capturas antes/despues o enlace |
    """),
    md("""
## Criterios minimos de aceptacion

El taller se considera completo si se puede verificar:

- hay datos desde 2021;
- hay al menos dos cargas diferenciadas;
- existe una ficha operativa por contrato;
- MongoDB recibe documentos con entidad, proveedor, territorio, ejecucion,
  adiciones, prioridad y texto no estructurado;
- se crea una coleccion de alertas;
- se crea al menos una coleccion resumen para dashboard;
- el dashboard o sus datos cambian despues de la segunda carga;
- el informe explica que no se detecta fraude, solo prioridad descriptiva.
    """),
    md("""
---
# Etapa 1. Preparacion del entorno

Ejecuta esta celda para instalar dependencias si hacen falta. En equipos con
entorno ya preparado, la celda solo confirma disponibilidad.
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
    print("Instalando:", faltantes)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *faltantes])
else:
    print("Dependencias principales disponibles.")
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
    params = params or {}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()
    """),
    md("""
## Verificacion docente de la etapa 1

El profesor debe ver que las dependencias cargan y que `FECHA_INICIO` queda
definida como `2021-01-01T00:00:00`.
    """),
    md("""
---
# Etapa 2. Verificacion de fuentes desde 2021

Antes de descargar lotes grandes, el equipo debe demostrar que las fuentes
responden y que el filtro temporal funciona.
    """),
    code("""
def mostrar_muestra(nombre, params):
    datos = consultar_socrata(FUENTES[nombre], params=params)
    df = pd.DataFrame(datos)
    print(f"{nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
    display(df.head(3))
    return df

muestra_contratos = mostrar_muestra(
    "contratos",
    {
        "$select": "id_contrato,fecha_de_firma,ultima_actualizacion,departamento,ciudad,valor_del_contrato",
        "$where": f"fecha_de_firma >= '{FECHA_INICIO}'",
        "$limit": 3,
    },
)

muestra_adiciones = mostrar_muestra(
    "adiciones",
    {
        "$select": "id_contrato,tipo,descripcion,fecharegistro",
        "$where": f"fecharegistro >= '{FECHA_INICIO}'",
        "$limit": 3,
    },
)

muestra_ejecucion = mostrar_muestra(
    "ejecucion",
    {
        "$select": "identificadorcontrato,tipoejecucion,fechacreacion,porcentaje_de_avance_real,estado_del_contrato",
        "$where": f"fechacreacion >= '{FECHA_INICIO}'",
        "$limit": 3,
    },
)

muestra_divipola = mostrar_muestra("divipola", {"$limit": 3})
    """),
    md("""
## Verificacion docente de la etapa 2

Revisar que aparezcan filas de las cuatro fuentes. Si una fuente falla por
conexion, el equipo debe documentar el error y reintentar. No se acepta cambiar
el periodo del taller para evitar el filtro desde 2021.
    """),
    md("""
---
# Etapa 3. Descarga de micro-batches

El taller no exige descargar todo SECOP. Se trabaja con lotes pequenos para
probar el flujo completo. El equipo puede aumentar `BATCH_SIZE` si su entorno
lo permite.
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

def descargar_contratos_batch(limit=BATCH_SIZE, offset=0):
    params = {
        "$select": CONTRATOS_SELECT,
        "$where": f"fecha_de_firma >= '{FECHA_INICIO}'",
        "$limit": limit,
        "$offset": offset,
        "$order": "fecha_de_firma DESC",
    }
    return pd.DataFrame(consultar_socrata(FUENTES["contratos"], params=params))

contratos_lote_1 = descargar_contratos_batch(BATCH_SIZE, 0)
contratos_lote_2 = descargar_contratos_batch(BATCH_SIZE, BATCH_SIZE)

print("lote_1", contratos_lote_1.shape)
print("lote_2", contratos_lote_2.shape)
display(contratos_lote_1.head(5))
    """),
    md("""
## Verificacion docente de la etapa 3

Revisar que existan dos lotes. Deben tener identificadores de contrato y fechas
desde 2021. El equipo debe reportar cuantas filas descargo en cada lote.
    """),
    md("""
---
# Etapa 4. Limpieza de contratos y cruce territorial

En esta etapa se convierten tipos y se intenta cruzar municipio/departamento con
DIVIPOLA. El cruce puede no ser perfecto: esa es una condicion normal de datos
reales.
    """),
    code("""
def normalizar_texto(x):
    if pd.isna(x):
        return ""
    x = str(x).strip().upper()
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))
    return " ".join(x.split())

def a_numero(x):
    return pd.to_numeric(x, errors="coerce").fillna(0)

def preparar_contratos(df):
    out = df.copy()
    for col in ["fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "ultima_actualizacion"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    for col in ["valor_del_contrato", "valor_pagado", "dias_adicionados"]:
        if col in out.columns:
            out[col] = a_numero(out[col])
    out["departamento_norm"] = out.get("departamento", "").apply(normalizar_texto)
    out["ciudad_norm"] = out.get("ciudad", "").apply(normalizar_texto)
    return out

def preparar_divipola(df):
    out = df.copy()
    out["departamento_norm"] = out["dpto"].apply(normalizar_texto)
    out["ciudad_norm"] = out["nom_mpio"].apply(normalizar_texto)
    out["latitud_num"] = pd.to_numeric(out["latitud"].str.replace(",", ".", regex=False), errors="coerce")
    out["longitud_num"] = pd.to_numeric(out["longitud"].str.replace(",", ".", regex=False), errors="coerce")
    return out

divipola = pd.DataFrame(consultar_socrata(FUENTES["divipola"], params={"$limit": 1200}))
divipola_limpia = preparar_divipola(divipola)

def cruzar_divipola(df):
    limpio = preparar_contratos(df)
    return limpio.merge(
        divipola_limpia[[
            "cod_dpto", "cod_mpio", "dpto", "nom_mpio",
            "departamento_norm", "ciudad_norm", "latitud_num", "longitud_num"
        ]],
        on=["departamento_norm", "ciudad_norm"],
        how="left",
    )

contratos_geo_1 = cruzar_divipola(contratos_lote_1)
print("Contratos lote 1 con codigo DIVIPOLA:", contratos_geo_1["cod_mpio"].notna().sum(), "de", len(contratos_geo_1))
display(contratos_geo_1[["id_contrato", "departamento", "ciudad", "valor_del_contrato", "cod_mpio"]].head(10))
    """),
    md("""
## Verificacion docente de la etapa 4

Revisar que `valor_del_contrato` sea numerico y que el equipo reporte cuantos
contratos cruzaron con DIVIPOLA. No se exige 100% de cruce porque los nombres
territoriales pueden venir con diferencias.
    """),
    md("""
---
# Etapa 5. Integracion con adiciones y ejecucion

Cada lote de contratos define que adiciones y registros de ejecucion se deben
consultar. Asi se simula un proceso incremental y no una descarga innecesaria
de toda la base.
    """),
    code("""
def construir_in_clause(ids):
    ids_limpios = [str(x).replace("'", "") for x in ids if pd.notna(x)]
    if not ids_limpios:
        return "('')"
    return "(" + ",".join([f"'{x}'" for x in ids_limpios]) + ")"

def descargar_adiciones(ids_contrato):
    in_clause = construir_in_clause(ids_contrato)
    params = {
        "$select": "id_contrato,tipo,descripcion,fecharegistro",
        "$where": f"fecharegistro >= '{FECHA_INICIO}' AND id_contrato in {in_clause}",
        "$limit": 5000,
    }
    return pd.DataFrame(consultar_socrata(FUENTES["adiciones"], params=params))

def descargar_ejecucion(ids_contrato):
    in_clause = construir_in_clause(ids_contrato)
    params = {
        "$select": "identificadorcontrato,tipoejecucion,fechacreacion,porcentaje_de_avance_real,estado_del_contrato",
        "$where": f"fechacreacion >= '{FECHA_INICIO}' AND identificadorcontrato in {in_clause}",
        "$limit": 5000,
    }
    return pd.DataFrame(consultar_socrata(FUENTES["ejecucion"], params=params))

def resumir_adiciones(df):
    if df.empty:
        return pd.DataFrame(columns=["id_contrato", "numero_adiciones", "ultima_adicion", "tipos_adicion", "descripcion_adiciones"])
    tmp = df.copy()
    tmp["fecharegistro"] = pd.to_datetime(tmp["fecharegistro"], errors="coerce")
    return (
        tmp.groupby("id_contrato")
        .agg(
            numero_adiciones=("id_contrato", "size"),
            ultima_adicion=("fecharegistro", "max"),
            tipos_adicion=("tipo", lambda s: sorted(set([str(x) for x in s.dropna()]))[:5]),
            descripcion_adiciones=("descripcion", lambda s: list(s.dropna().astype(str).head(3))),
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

def enriquecer_lote(df_contratos):
    geo = cruzar_divipola(df_contratos)
    ids = geo["id_contrato"].dropna().unique().tolist()
    adiciones = descargar_adiciones(ids)
    ejecucion = descargar_ejecucion(ids)
    enriquecido = (
        geo
        .merge(resumir_adiciones(adiciones), on="id_contrato", how="left")
        .merge(resumir_ejecucion(ejecucion), on="id_contrato", how="left")
    )
    enriquecido["numero_adiciones"] = enriquecido["numero_adiciones"].fillna(0).astype(int)
    enriquecido["ultimo_avance_real"] = enriquecido["ultimo_avance_real"].fillna(0)
    return enriquecido, adiciones, ejecucion

contratos_enriquecidos_1, adiciones_1, ejecucion_1 = enriquecer_lote(contratos_lote_1)
display(contratos_enriquecidos_1[[
    "id_contrato", "valor_del_contrato", "numero_adiciones",
    "ultimo_avance_real", "estado_ejecucion", "proveedor_adjudicado"
]].head(10))
    """),
    md("""
## Verificacion docente de la etapa 5

Revisar que el equipo muestre `numero_adiciones` y `ultimo_avance_real`. Si no
hay adiciones para el lote, debe quedar reportado como cero, no como error.
    """),
    md("""
---
# Etapa 6. Uso simple de datos no estructurados

El texto libre del objeto contractual y de las adiciones es el componente no
estructurado del taller. Para mantenerlo simple se usaran diccionarios de
palabras clave. No se requiere machine learning.
    """),
    code("""
TEMAS_CONTRATACION = {
    "alimentacion": ["alimentacion", "alimentos", "restaurante", "cafeteria", "comedor"],
    "infraestructura": ["obra", "via", "mantenimiento", "construccion", "interventoria", "adecuacion"],
    "salud": ["salud", "hospital", "medicamento", "ambulancia", "clinica"],
    "educacion": ["colegio", "estudiante", "educativo", "escolar", "docente"],
    "tecnologia": ["software", "licencia", "sistema", "computador", "tecnologia", "plataforma"],
    "servicios_profesionales": ["prestacion de servicios", "apoyo a la gestion", "consultoria", "asesoria"],
}

def limpiar_texto_simple(x):
    if pd.isna(x):
        return ""
    x = normalizar_texto(x)
    x = re.sub(r"[^A-Z0-9 Ñ]", " ", x)
    return " ".join(x.split())

def detectar_temas(texto):
    texto_limpio = limpiar_texto_simple(texto)
    temas = []
    for tema, palabras in TEMAS_CONTRATACION.items():
        for palabra in palabras:
            if normalizar_texto(palabra) in texto_limpio:
                temas.append(tema)
                break
    return temas if temas else ["sin_tema_detectado"]

def agregar_texto_no_estructurado(df):
    out = df.copy()
    out["texto_contrato_limpio"] = out["objeto_del_contrato"].apply(limpiar_texto_simple)
    out["temas_detectados"] = out["objeto_del_contrato"].apply(detectar_temas)
    return out

contratos_texto_1 = agregar_texto_no_estructurado(contratos_enriquecidos_1)
display(contratos_texto_1[["id_contrato", "objeto_del_contrato", "temas_detectados"]].head(10))
    """),
    code("""
def resumen_temas(df):
    filas = []
    for _, row in df.iterrows():
        temas = row.get("temas_detectados", [])
        if not isinstance(temas, list):
            temas = ["sin_tema_detectado"]
        for tema in temas:
            filas.append({
                "tema": tema,
                "id_contrato": row.get("id_contrato"),
                "valor_del_contrato": row.get("valor_del_contrato", 0),
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

display(resumen_temas(contratos_texto_1))
    """),
    md("""
## Verificacion docente de la etapa 6

Revisar que exista la columna `temas_detectados` y que el equipo explique el
metodo usado. La clasificacion por palabras clave no es perfecta; debe
presentarse como apoyo exploratorio, no como verdad absoluta.
    """),
    md("""
---
# Etapa 7. Indice descriptivo de prioridad

Este indice permite ordenar revision. No es una prueba de irregularidad.
    """),
    code("""
def calcular_prioridad(df):
    out = df.copy()
    valor = out["valor_del_contrato"].fillna(0)
    p75 = valor.quantile(0.75) if len(valor) else 0
    p90 = valor.quantile(0.90) if len(valor) else 0

    out["puntaje_valor"] = np.select([valor >= p90, valor >= p75], [25, 15], default=0)
    out["puntaje_adiciones"] = np.select(
        [out["numero_adiciones"] >= 2, out["numero_adiciones"] == 1],
        [20, 10],
        default=0,
    )
    out["puntaje_ejecucion"] = np.where((out["ultimo_avance_real"] < 50) & (valor > p75), 15, 0)
    out["puntaje_modalidad"] = np.where(
        out["modalidad_de_contratacion"].fillna("").str.contains("Directa|Mínima|Minima", case=False, regex=True),
        10,
        0,
    )
    out["puntaje_texto"] = np.where(
        out["temas_detectados"].apply(lambda temas: "sin_tema_detectado" in temas),
        5,
        0,
    )
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

contratos_scored_1 = calcular_prioridad(contratos_texto_1)
display(contratos_scored_1.sort_values("indice_prioridad_revision", ascending=False)[[
    "id_contrato", "nombre_entidad", "proveedor_adjudicado",
    "valor_del_contrato", "numero_adiciones", "temas_detectados",
    "indice_prioridad_revision", "nivel_prioridad"
]].head(10))
    """),
    md("""
## Verificacion docente de la etapa 7

Revisar que el equipo presente el ranking y explique las reglas de puntaje. La
redaccion debe decir "prioridad de revision", no "fraude".
    """),
    md("""
---
# Etapa 8. Modelo documental para MongoDB

MongoDB se usa como capa operativa. Cada contrato se guarda como una ficha con
datos basicos, entidad, proveedor, territorio, ejecucion, adiciones, texto y
prioridad.
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

def contrato_a_documento(row, lote):
    return {
        "_id": row.get("id_contrato"),
        "id_contrato": row.get("id_contrato"),
        "lote": lote,
        "fecha_ingesta": datetime.now(timezone.utc).isoformat(),
        "objeto": limpiar_nan(row.get("objeto_del_contrato")),
        "valor": limpiar_nan(row.get("valor_del_contrato")),
        "valor_pagado": limpiar_nan(row.get("valor_pagado")),
        "fechas": {
            "firma": limpiar_nan(row.get("fecha_de_firma")),
            "inicio": limpiar_nan(row.get("fecha_de_inicio_del_contrato")),
            "fin": limpiar_nan(row.get("fecha_de_fin_del_contrato")),
            "ultima_actualizacion": limpiar_nan(row.get("ultima_actualizacion")),
        },
        "entidad": {
            "nombre": limpiar_nan(row.get("nombre_entidad")),
            "nit": limpiar_nan(row.get("nit_entidad")),
            "sector": limpiar_nan(row.get("sector")),
            "orden": limpiar_nan(row.get("orden")),
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
        "contratacion": {
            "tipo": limpiar_nan(row.get("tipo_de_contrato")),
            "modalidad": limpiar_nan(row.get("modalidad_de_contratacion")),
            "estado": limpiar_nan(row.get("estado_contrato")),
        },
        "ejecucion": {
            "avance_real": limpiar_nan(row.get("ultimo_avance_real")),
            "estado": limpiar_nan(row.get("estado_ejecucion")),
            "ultima_fecha": limpiar_nan(row.get("ultima_fecha_ejecucion")),
        },
        "adiciones": {
            "numero": limpiar_nan(row.get("numero_adiciones")),
            "ultima": limpiar_nan(row.get("ultima_adicion")),
            "tipos": limpiar_nan(row.get("tipos_adicion")),
            "descripciones": limpiar_nan(row.get("descripcion_adiciones")),
        },
        "texto_no_estructurado": {
            "objeto_limpio": limpiar_nan(row.get("texto_contrato_limpio")),
            "temas_detectados": limpiar_nan(row.get("temas_detectados")),
        },
        "prioridad": {
            "indice": limpiar_nan(row.get("indice_prioridad_revision")),
            "nivel": limpiar_nan(row.get("nivel_prioridad")),
        },
        "estado_revision": "pendiente",
    }

documentos_lote_1 = [
    contrato_a_documento(row, "lote_1")
    for _, row in contratos_scored_1.iterrows()
    if pd.notna(row.get("id_contrato"))
]

documentos_lote_1[0]
    """),
    md("""
## Verificacion docente de la etapa 8

Revisar un documento de ejemplo. Debe contener `texto_no_estructurado`,
`temas_detectados`, `prioridad`, `adiciones` y `ejecucion`.
    """),
    md("""
---
# Etapa 9. Carga a MongoDB

Configura `MONGODB_URI` como variable de entorno si usaras Atlas. Si no hay
MongoDB disponible, el notebook genera archivos JSON de respaldo para revisar
la estructura. Para la entrega final, el equipo debe mostrar la carga real o
justificar la limitacion del entorno.
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
    print("Conexion a MongoDB: OK")
except Exception as e:
    print("No se pudo conectar a MongoDB.")
    print("Detalle:", e)
    print("Se usaran archivos JSON de respaldo para inspeccion.")

def cargar_contratos_mongo(documentos, etiqueta_lote):
    if not documentos:
        return {"documentos": 0, "mongo_ok": mongo_ok}

    if mongo_ok:
        ops = [
            UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            for doc in documentos
        ]
        result = db.contratos_operativos.bulk_write(ops)
        db.metadata_pipeline.insert_one({
            "lote": etiqueta_lote,
            "fecha": datetime.now(timezone.utc).isoformat(),
            "documentos_recibidos": len(documentos),
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": len(result.upserted_ids),
            "fuente": "SECOP II desde 2021",
        })
        return {
            "documentos": len(documentos),
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": len(result.upserted_ids),
            "mongo_ok": True,
        }

    salida = SALIDA / f"{etiqueta_lote}_contratos_operativos.json"
    salida.write_text(json.dumps(documentos, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"documentos": len(documentos), "mongo_ok": False, "archivo": str(salida)}

resultado_lote_1 = cargar_contratos_mongo(documentos_lote_1, "lote_1")
resultado_lote_1
    """),
    md("""
## Verificacion docente de la etapa 9

Revisar conteos de carga. Si `mongo_ok` es verdadero, debe existir metadata en
MongoDB. Si no, debe existir el archivo JSON de respaldo y el equipo debe cargar
MongoDB antes de la entrega final.
    """),
    md("""
---
# Etapa 10. Colecciones para dashboard

El dashboard no debe depender de calculos manuales. Se crean colecciones resumen
para KPIs, entidades, proveedores, temas y alertas.
    """),
    code("""
def construir_dashboard_frames(df):
    kpis = pd.DataFrame([{
        "fecha_calculo": datetime.now(timezone.utc).isoformat(),
        "total_contratos": int(len(df)),
        "valor_total": float(df["valor_del_contrato"].sum()),
        "contratos_prioridad_alta": int((df["nivel_prioridad"] == "alta").sum()),
        "contratos_con_adiciones": int((df["numero_adiciones"] > 0).sum()),
        "proveedores_unicos": int(df["documento_proveedor"].nunique()),
        "entidades_unicas": int(df["nit_entidad"].nunique()),
    }])

    entidades = (
        df.groupby(["nit_entidad", "nombre_entidad"], dropna=False)
        .agg(
            total_contratos=("id_contrato", "count"),
            valor_total=("valor_del_contrato", "sum"),
            prioridad_promedio=("indice_prioridad_revision", "mean"),
            contratos_con_adiciones=("numero_adiciones", lambda s: int((s > 0).sum())),
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
            prioridad_promedio=("indice_prioridad_revision", "mean"),
        )
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    temas = resumen_temas(df)

    alertas = df[df["nivel_prioridad"].isin(["media", "alta"])].copy()
    alertas = alertas[[
        "id_contrato", "nombre_entidad", "proveedor_adjudicado", "departamento",
        "ciudad", "valor_del_contrato", "numero_adiciones", "ultimo_avance_real",
        "indice_prioridad_revision", "nivel_prioridad", "temas_detectados"
    ]].sort_values("indice_prioridad_revision", ascending=False)

    return {
        "dashboard_kpis": kpis,
        "dashboard_entidades": entidades,
        "dashboard_proveedores": proveedores,
        "dashboard_temas": temas,
        "alertas_revision": alertas,
    }

dashboard_lote_1 = construir_dashboard_frames(contratos_scored_1)
for nombre, frame in dashboard_lote_1.items():
    print(nombre, frame.shape)
    display(frame.head(5))
    """),
    code("""
def cargar_dashboard_mongo(frames, etiqueta_lote):
    if mongo_ok:
        for nombre, frame in frames.items():
            registros = json.loads(frame.to_json(orient="records", date_format="iso", force_ascii=False))
            db[nombre].delete_many({"lote": etiqueta_lote})
            for r in registros:
                r["lote"] = etiqueta_lote
                r["fecha_carga"] = datetime.now(timezone.utc).isoformat()
            if registros:
                db[nombre].insert_many(registros)
        return {"mongo_ok": True, "colecciones_actualizadas": list(frames.keys())}

    salidas = {}
    for nombre, frame in frames.items():
        salida = SALIDA / f"{etiqueta_lote}_{nombre}.json"
        salida.write_text(frame.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
        salidas[nombre] = str(salida)
    return {"mongo_ok": False, "archivos": salidas}

resultado_dashboard_1 = cargar_dashboard_mongo(dashboard_lote_1, "lote_1")
resultado_dashboard_1
    """),
    md("""
## Verificacion docente de la etapa 10

Revisar que existan datos para `dashboard_kpis`, `dashboard_entidades`,
`dashboard_proveedores`, `dashboard_temas` y `alertas_revision`.
    """),
    md("""
---
# Etapa 11. Segunda carga y actualizacion

El segundo lote demuestra comportamiento operativo. No es necesario Airflow para
validar el taller; se ejecuta desde el notebook. Airflow, cron o Databricks
Workflows pueden quedar como extension.
    """),
    code("""
contratos_enriquecidos_2, adiciones_2, ejecucion_2 = enriquecer_lote(contratos_lote_2)
contratos_texto_2 = agregar_texto_no_estructurado(contratos_enriquecidos_2)
contratos_scored_2 = calcular_prioridad(contratos_texto_2)

documentos_lote_2 = [
    contrato_a_documento(row, "lote_2")
    for _, row in contratos_scored_2.iterrows()
    if pd.notna(row.get("id_contrato"))
]

resultado_lote_2 = cargar_contratos_mongo(documentos_lote_2, "lote_2")
dashboard_lote_2 = construir_dashboard_frames(contratos_scored_2)
resultado_dashboard_2 = cargar_dashboard_mongo(dashboard_lote_2, "lote_2")

print("Carga contratos lote 2:", resultado_lote_2)
print("Carga dashboard lote 2:", resultado_dashboard_2)
display(contratos_scored_2.sort_values("indice_prioridad_revision", ascending=False).head(10))
    """),
    md("""
## Verificacion docente de la etapa 11

El profesor debe poder comparar evidencia de `lote_1` y `lote_2`. La entrega
debe explicar que cambio: nuevos contratos, nuevos temas, nuevas alertas o
nuevos valores de KPI.
    """),
    md("""
---
# Etapa 12. Consultas de negocio

Estas consultas muestran que MongoDB actua como capa operativa. Si no hay
conexion a MongoDB durante la clase, el equipo debe ejecutarlas en su entrega
final.
    """),
    code("""
if mongo_ok:
    print("Contratos de prioridad alta")
    display(pd.DataFrame(list(db.contratos_operativos.find(
        {"prioridad.nivel": "alta"},
        {"_id": 0, "id_contrato": 1, "valor": 1, "entidad.nombre": 1, "proveedor.nombre": 1, "prioridad": 1}
    ).limit(10))))

    print("Top temas detectados")
    display(pd.DataFrame(list(db.dashboard_temas.find({}, {"_id": 0}).sort("total_contratos", -1).limit(10))))

    print("Indice de texto recomendado")
    print('db.contratos_operativos.create_index([("objeto", "text")])')
    print('db.contratos_operativos.find({"$text": {"$search": "alimentacion escolar infraestructura"}})')
else:
    print("MongoDB no esta conectado en este entorno.")
    print("Usa los archivos JSON de salidas_taller_final como respaldo, pero ejecuta MongoDB para la entrega final.")
    """),
    md("""
## Verificacion docente de la etapa 12

El equipo debe mostrar al menos tres consultas:

1. contratos de prioridad alta;
2. temas detectados desde texto no estructurado;
3. ficha completa de un contrato o proveedor.
    """),
    md("""
---
# Dashboard que debe construir el equipo

El dashboard debe leer desde MongoDB o desde las colecciones JSON exportadas si
hay una limitacion temporal del entorno. Para la entrega final se recomienda
MongoDB Atlas Charts.

Panel minimo:

1. KPIs: total contratos, valor total, contratos con adiciones, prioridad alta.
2. Alertas: tabla ordenada por indice de prioridad.
3. Entidades: ranking por valor total y prioridad promedio.
4. Proveedores: ranking por valor y numero de entidades.
5. Temas: grafico de `dashboard_temas`.
6. Evidencia antes/despues: captura del lote 1 y captura posterior al lote 2.
    """),
    md("""
---
# Matriz de verificacion para el profesor

| Elemento | Evidencia que debe mostrar el equipo | Cumple |
|---|---|---|
| Fuentes desde 2021 | Muestras de contratos, adiciones y ejecucion filtradas |  |
| Dos lotes | Conteo de `lote_1` y `lote_2` |  |
| Limpieza | Fechas y valores convertidos |  |
| Territorio | Cruce con DIVIPOLA y conteo de cruces exitosos |  |
| Adiciones | `numero_adiciones` por contrato |  |
| Ejecucion | `ultimo_avance_real` por contrato cuando exista |  |
| Texto no estructurado | `temas_detectados` y resumen por tema |  |
| Prioridad | Ranking con reglas explicadas |  |
| MongoDB | Documentos en `contratos_operativos` o JSON equivalente |  |
| Dashboard | KPIs, alertas, entidades, proveedores y temas |  |
| Actualizacion | Comparacion antes/despues de la segunda carga |  |
| Interpretacion | Informe sin afirmar fraude ni causalidad |  |

Esta matriz se puede usar como lista de chequeo durante la sustentacion.
    """),
    md("""
## Rubrica sugerida

| Criterio | Peso |
|---|---:|
| Consulta correcta de fuentes desde 2021 | 10% |
| Integracion de contratos, adiciones, ejecucion y territorio | 15% |
| Limpieza y calidad de datos | 10% |
| Uso simple de texto no estructurado | 10% |
| Indice descriptivo de prioridad | 10% |
| Modelo documental y carga en MongoDB | 15% |
| Dashboard operativo con evidencia de actualizacion | 15% |
| Informe ejecutivo y limites del analisis | 10% |
| Reproducibilidad de la entrega | 5% |
    """),
    md("""
## Cierre del taller

El taller termina cuando el equipo puede demostrar una historia completa:

1. se conecto a fuentes reales desde 2021;
2. integro varias bases;
3. uso texto no estructurado de forma simple;
4. calculo prioridad descriptiva;
5. publico fichas y resumenes en MongoDB;
6. mostro un dashboard que cambia con una segunda carga;
7. explico que se puede concluir y que no se puede concluir.

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
