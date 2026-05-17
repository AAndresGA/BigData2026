# -*- coding: utf-8 -*-
"""
Genera Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb

Taller final: observatorio casi en tiempo real de contratacion publica
con SECOP II, Dask/Spark conceptual, MongoDB y dashboard operativo.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header


TOTAL_Q = 10


def pregunta(num, tema, contexto, pregunta_texto, opciones, correcta, explicacion):
    opciones_html = "\n".join(
        f'<label style="display:block; margin:8px 0;"><input type="radio" name="q{num}" value="{chr(65+i)}"> {chr(65+i)}. {op}</label>'
        for i, op in enumerate(opciones)
    )
    return code(f"""
# Pregunta interactiva {num} de {TOTAL_Q}
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
        "### Interpretacion docente -- " + titulo + "\n\n" +
        "\n".join(f"- {p}" for p in puntos)
    )


cells = [
    *uce_header(
        title="Taller final: observatorio casi en tiempo real con SECOP II y MongoDB",
        session=13,
        github_path="main/Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb",
        nota_plataforma="Colab, Jupyter local o Databricks. MongoDB Atlas recomendado para dashboard.",
    ),
    md("""
## Vista rapida del taller

| Elemento | Detalle |
|---|---|
| Caso de negocio | Monitoreo operativo de contratacion publica territorial |
| Fuentes | SECOP II contratos, SECOP II adiciones, SECOP II ejecucion, DIVIPOLA, poblacion/IPM como extension |
| Datos no estructurados | Texto libre del objeto contractual y descripcion de adiciones |
| Periodo obligatorio | Solo registros desde `2021-01-01` |
| Tecnologias | Python, Pandas/Dask o Spark, MongoDB, Atlas Charts o dashboard equivalente |
| Producto final | Observatorio consultable de contratos, proveedores, entidades, municipios y alertas descriptivas |
| Tipo de ejecucion | Micro-batches: cargas pequenas repetidas que simulan monitoreo casi en tiempo real |

Este cuaderno no propone una tarea abstracta. Propone una solucion de datos que
podria necesitar una oficina de control interno, planeacion, veeduria o analitica
publica: saber que contratos nuevos o modificados merecen revision prioritaria.

### Alcance obligatorio y opcional

**Obligatorio en este taller:** ejecutar el flujo desde el cuaderno, cargar o
simular la carga en MongoDB, crear colecciones para dashboard y demostrar una
segunda actualizacion.

**Opcional:** automatizar el mismo flujo con Airflow, Databricks Workflows,
GitHub Actions, `cron` u otra herramienta de orquestacion. Esa automatizacion
puede sumar valor al proyecto final, pero no es necesaria para entender la
solucion ni para validar el papel de MongoDB.
    """),
    md("""
## Objetivos de aprendizaje

Al terminar el taller, deberias poder:

1. Verificar que las fuentes publicas existen y que se pueden consultar desde 2021.
2. Descargar contratos, adiciones, ejecucion y datos territoriales en micro-batches.
3. Integrar varias bases con distintos tipos de datos: transaccional, eventos, seguimiento, territorio y texto.
4. Usar texto no estructurado de forma simple para detectar temas del contrato.
5. Construir documentos MongoDB que representen fichas operativas de contratos.
6. Actualizar MongoDB con `upsert`, evitando duplicados.
7. Crear colecciones resumen para un dashboard.
8. Explicar por que MongoDB aporta valor real en esta solucion.
9. Presentar hallazgos y limites sin afirmar fraude ni causalidad.
    """),
    md("""
## Agenda sugerida

1. Caso de negocio y decisiones que debe soportar el observatorio.
2. Verificacion de fuentes y filtro desde 2021.
3. Diseno de arquitectura y modelo documental.
4. Descarga de un primer micro-batch.
5. Limpieza, union y enriquecimiento.
6. Tratamiento simple de texto no estructurado.
7. Calculo de senales descriptivas de prioridad.
8. Carga operativa a MongoDB.
9. Generacion de colecciones para dashboard.
10. Segunda carga para demostrar actualizacion.
11. Cierre: entregables, rubrica y limites del analisis.
    """),
    md("""
## Por que importa este taller

En analitica publica el problema no es solo calcular una tabla. El problema real
es transformar datos dispersos en una herramienta que ayude a decidir.

Un auditor no quiere reconstruir `JOIN` cada vez que revisa un contrato. Un
funcionario de planeacion no quiere abrir cinco archivos para saber que paso con
un proveedor. Un dashboard no deberia esperar a que alguien rehaga manualmente
todos los cruces.

Por eso este taller separa responsabilidades:

- **Pandas, Dask o Spark** procesan y calculan.
- **Parquet o CSV limpio** conservan salidas analiticas reproducibles.
- **MongoDB** guarda fichas completas, alertas y colecciones listas para consulta.
- **Atlas Charts o un dashboard equivalente** muestra cambios despues de cada carga.
    """),
    pregunta(
        1,
        "Caso de negocio",
        "El proyecto busca resolver una necesidad operativa, no solo demostrar una tecnologia.",
        "Cual es la pregunta mas cercana al caso real de este taller?",
        [
            "Cual libreria de Python es mas popular?",
            "Que contratos nuevos o modificados desde 2021 deben revisarse primero y por que?",
            "Como hacer un grafico bonito con cualquier CSV?",
            "Como reemplazar todas las bases SQL por MongoDB?"
        ],
        "B",
        "El observatorio existe para priorizar revision de contratos con datos integrados y actualizados."
    ),
    md("""
---
# Parte 1 -- Fuentes y verificacion de factibilidad

Antes de imponer una tarea, debemos probar que las fuentes existen y que el
filtro temporal funciona. En este taller se trabaja desde 2021 porque permite
un periodo reciente, suficiente y manejable para clase.

Fuentes principales:

| Fuente | Endpoint Socrata | Uso |
|---|---|---|
| SECOP II contratos electronicos | `jbjy-vk9h` | Contratos, entidad, proveedor, fechas, valores, objeto |
| SECOP II adiciones | `cb9c-h8sn` | Modificaciones, adiciones y eventos asociados al contrato |
| SECOP II ejecucion contratos | `mfmm-jqmq` | Avance esperado, avance real y estado |
| DIVIPOLA municipios | `gdxc-w37w` | Codigo, departamento, municipio, latitud y longitud |

Regla del taller:

> Todo analisis obligatorio debe filtrar datos desde `2021-01-01`.
    """),
    code("""
# Instalacion de dependencias para Colab, Jupyter local o entornos limpios.
# Esta celda revisa primero y solo instala lo que falta.
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
    paquete_pip
    for modulo, paquete_pip in paquetes.items()
    if importlib.util.find_spec(modulo) is None
]

if faltantes:
    print("Instalando dependencias faltantes:", faltantes)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *faltantes])
else:
    print("Dependencias principales ya disponibles.")

print("Entorno listo. Si vas a usar MongoDB Atlas, configura MONGODB_URI antes de cargar.")
    """),
    md("""
### Mini ficha de funciones usadas

Funcion usada: `requests.get()`

- Para que sirve: envia una solicitud HTTP a una API.
- Parametros usados: `url`, `params`, `timeout`.
- Que devuelve: una respuesta del servidor.
- Como interpretar la salida: si `status_code` es 200, la API respondio correctamente.

Funcion usada: `pandas.DataFrame()`

- Para que sirve: convierte una lista de registros en una tabla.
- Parametros usados: lista de diccionarios.
- Que devuelve: una estructura tabular con filas y columnas.
- Como interpretar la salida: cada fila representa un registro descargado.
    """),
    code("""
import requests
import pandas as pd
from datetime import datetime, timezone
from IPython.display import display

BASE = "https://www.datos.gov.co/resource"
FUENTES = {
    "contratos": f"{BASE}/jbjy-vk9h.json",
    "adiciones": f"{BASE}/cb9c-h8sn.json",
    "ejecucion": f"{BASE}/mfmm-jqmq.json",
    "divipola": f"{BASE}/gdxc-w37w.json",
}

FECHA_INICIO = "2021-01-01T00:00:00"

def consultar_socrata(url, params=None, timeout=45):
    params = params or {}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def muestra_fuente(nombre, params):
    datos = consultar_socrata(FUENTES[nombre], params=params)
    df = pd.DataFrame(datos)
    print(f"{nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
    display(df.head(3))
    return df

contratos_muestra = muestra_fuente(
    "contratos",
    {
        "$select": "id_contrato,fecha_de_firma,ultima_actualizacion,departamento,ciudad,valor_del_contrato",
        "$where": f"fecha_de_firma >= '{FECHA_INICIO}'",
        "$limit": 3,
    },
)

adiciones_muestra = muestra_fuente(
    "adiciones",
    {
        "$select": "id_contrato,tipo,descripcion,fecharegistro",
        "$where": f"fecharegistro >= '{FECHA_INICIO}'",
        "$limit": 3,
    },
)

ejecucion_muestra = muestra_fuente(
    "ejecucion",
    {
        "$select": "identificadorcontrato,tipoejecucion,fechacreacion,porcentaje_de_avance_real,estado_del_contrato",
        "$where": f"fechacreacion >= '{FECHA_INICIO}'",
        "$limit": 3,
    },
)

divipola_muestra = muestra_fuente("divipola", {"$limit": 3})
    """),
    interp("verificacion de fuentes", [
        "Si las cuatro tablas aparecen con filas, el taller es viable en terminos de acceso a datos.",
        "El filtro desde 2021 ya se prueba antes de construir el pipeline.",
        "Si una fuente falla por conexion, no se cambia el objetivo: se reintenta o se trabaja con una muestra guardada por el equipo."
    ]),
    pregunta(
        2,
        "Factibilidad",
        "El taller consulta primero una muestra minima de cada fuente antes de pedir el desarrollo completo.",
        "Por que se verifica la fuente con `$limit=3` antes de descargar mas datos?",
        [
            "Para reemplazar el analisis completo por tres filas.",
            "Para confirmar acceso, columnas y filtro temporal con bajo costo.",
            "Para evitar usar datos reales.",
            "Para que MongoDB haga automaticamente la limpieza."
        ],
        "B",
        "Una verificacion pequena reduce riesgo: confirma que la API responde y que las columnas existen."
    ),
    md("""
---
# Parte 2 -- Arquitectura de la solucion

La solucion tiene dos niveles:

1. **Nivel analitico:** procesa contratos, adiciones, ejecucion y territorio.
2. **Nivel operativo:** publica fichas y alertas en MongoDB para consulta y dashboard.

Flujo:

```text
SECOP II + DIVIPOLA + datos sociales
        ↓
Micro-batch de ingesta desde 2021
        ↓
Limpieza y enriquecimiento
        ↓
Calculo de indicadores de prioridad
        ↓
MongoDB: contratos, entidades, proveedores, municipios, alertas
        ↓
Dashboard: KPIs, alertas, proveedores, mapa/ranking territorial
```

La clave es que MongoDB no se usa como adorno. Se usa como **mostrador operativo**:
guarda documentos completos que una persona puede consultar sin reconstruir todas
las uniones.
    """),
    pregunta(
        3,
        "Papel de MongoDB",
        "Spark/Dask procesan; MongoDB publica fichas listas para consulta operativa.",
        "Cual es el papel mas realista de MongoDB en este proyecto?",
        [
            "Reemplazar toda limpieza y procesamiento distribuido.",
            "Guardar documentos enriquecidos, alertas y resumenes para consulta rapida.",
            "Descargar automaticamente todos los datos de SECOP.",
            "Eliminar la necesidad de interpretar resultados."
        ],
        "B",
        "MongoDB es la capa operativa posterior al procesamiento, no el motor principal de limpieza masiva."
    ),
    md("""
---
# Parte 3 -- Descarga del primer micro-batch

Para clase usaremos micro-batches pequenos. En un proyecto final, el equipo puede
aumentar `BATCH_SIZE` y usar paginacion por `offset`.

Este diseno permite demostrar el comportamiento casi en tiempo real:

- Primera carga: llegan contratos y se crean documentos.
- Segunda carga: llegan mas contratos o adiciones y se actualizan documentos.
- El dashboard cambia porque MongoDB cambia.
    """),
    code("""
BATCH_SIZE = 100
OFFSET_1 = 0
OFFSET_2 = 100

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

contratos_1 = descargar_contratos_batch(BATCH_SIZE, OFFSET_1)
print(contratos_1.shape)
display(contratos_1.head(5))
    """),
    interp("primer micro-batch", [
        "Cada fila representa un contrato reciente desde 2021.",
        "El objetivo no es descargar millones de filas en clase, sino validar el flujo completo.",
        "El mismo patron se escala aumentando el tamano de lote o moviendo el proceso a Spark/Databricks."
    ]),
    md("""
### Descarga de adiciones y ejecucion relacionadas

Para no descargar toda la tabla de adiciones, tomamos los `id_contrato` del lote
y consultamos solo eventos relacionados. Esto hace el taller mas liviano y mas
cercano a una operacion incremental.
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

ids_1 = contratos_1["id_contrato"].dropna().unique().tolist()
adiciones_1 = descargar_adiciones(ids_1)
ejecucion_1 = descargar_ejecucion(ids_1)
divipola = pd.DataFrame(consultar_socrata(FUENTES["divipola"], params={"$limit": 1200}))

print("adiciones", adiciones_1.shape)
print("ejecucion", ejecucion_1.shape)
print("divipola", divipola.shape)
display(adiciones_1.head(3))
display(ejecucion_1.head(3))
display(divipola.head(3))
    """),
    pregunta(
        4,
        "Micro-batch",
        "El lote de contratos define que adiciones y registros de ejecucion se consultan despues.",
        "Que ventaja tiene consultar adiciones solo para los contratos del lote?",
        [
            "Hace que el taller sea mas pesado.",
            "Reduce datos innecesarios y simula un pipeline incremental.",
            "Impide unir las bases.",
            "Elimina la necesidad de MongoDB."
        ],
        "B",
        "Un micro-batch operativo consulta lo necesario para actualizar el estado de los contratos del lote."
    ),
    md("""
---
# Parte 4 -- Limpieza y enriquecimiento

Ahora convertimos textos, fechas y valores. Tambien normalizamos municipio y
departamento para intentar cruzar con DIVIPOLA.

Error comun:

> Tratar los valores monetarios como texto. Si no convertimos `valor_del_contrato`,
> los rankings y sumas pueden quedar mal.
    """),
    code("""
import unicodedata
import numpy as np

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
    out["proveedor_norm"] = out.get("proveedor_adjudicado", "").apply(normalizar_texto)
    out["entidad_norm"] = out.get("nombre_entidad", "").apply(normalizar_texto)
    return out

def preparar_divipola(df):
    out = df.copy()
    out["departamento_norm"] = out["dpto"].apply(normalizar_texto)
    out["ciudad_norm"] = out["nom_mpio"].apply(normalizar_texto)
    out["latitud_num"] = pd.to_numeric(out["latitud"].str.replace(",", ".", regex=False), errors="coerce")
    out["longitud_num"] = pd.to_numeric(out["longitud"].str.replace(",", ".", regex=False), errors="coerce")
    return out

contratos_limpios = preparar_contratos(contratos_1)
divipola_limpia = preparar_divipola(divipola)

contratos_geo = contratos_limpios.merge(
    divipola_limpia[["cod_dpto", "cod_mpio", "dpto", "nom_mpio", "departamento_norm", "ciudad_norm", "latitud_num", "longitud_num"]],
    on=["departamento_norm", "ciudad_norm"],
    how="left",
)

display(contratos_geo[["id_contrato", "departamento", "ciudad", "valor_del_contrato", "cod_mpio", "latitud_num", "longitud_num"]].head(10))
print("Contratos con DIVIPOLA encontrado:", contratos_geo["cod_mpio"].notna().sum(), "de", len(contratos_geo))
    """),
    interp("cruce territorial", [
        "El cruce no siempre sera perfecto porque SECOP y DIVIPOLA pueden escribir municipios de forma distinta.",
        "Un resultado incompleto no invalida el proyecto: muestra un problema real de calidad de datos maestros.",
        "El equipo debe documentar cuantos contratos lograron georreferenciar y cuantos quedaron sin codigo territorial."
    ]),
    pregunta(
        5,
        "Calidad territorial",
        "SECOP y DIVIPOLA pueden escribir nombres de municipios de manera diferente.",
        "Que conclusion es correcta si algunos contratos no cruzan con DIVIPOLA?",
        [
            "Los datos no sirven y se debe abandonar el proyecto.",
            "Hay un problema real de normalizacion territorial que debe documentarse.",
            "MongoDB corrige automaticamente todos los nombres.",
            "Se deben borrar todos los contratos sin coordenadas."
        ],
        "B",
        "La calidad de datos maestros es parte del aprendizaje y debe medirse."
    ),
    md("""
---
# Parte 5 -- Integracion de adiciones y ejecucion

Un contrato operativo debe mostrar mas que los datos basicos. Debe incluir si
tiene adiciones y que estado de ejecucion aparece asociado.
    """),
    code("""
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

adiciones_resumen = resumir_adiciones(adiciones_1)
ejecucion_resumen = resumir_ejecucion(ejecucion_1)

contratos_enriquecidos = (
    contratos_geo
    .merge(adiciones_resumen, on="id_contrato", how="left")
    .merge(ejecucion_resumen, on="id_contrato", how="left")
)

contratos_enriquecidos["numero_adiciones"] = contratos_enriquecidos["numero_adiciones"].fillna(0).astype(int)
contratos_enriquecidos["ultimo_avance_real"] = contratos_enriquecidos["ultimo_avance_real"].fillna(0)

display(contratos_enriquecidos[[
    "id_contrato", "valor_del_contrato", "numero_adiciones",
    "ultimo_avance_real", "estado_ejecucion", "proveedor_adjudicado"
]].head(10))
    """),
    interp("contrato enriquecido", [
        "Ahora cada contrato contiene datos basicos, senales de adiciones y estado de ejecucion.",
        "Esta tabla ya no es una simple descarga: es una vista operativa que puede alimentar MongoDB.",
        "Todavia no afirmamos irregularidad; solo construimos variables para priorizar revision."
    ]),
    md("""
---
# Parte 6 -- Texto no estructurado: objeto contractual y adiciones

Hasta ahora trabajamos con datos estructurados: fechas, valores, codigos,
entidades y proveedores. Pero SECOP tambien trae texto libre, especialmente en:

- `objeto_del_contrato`;
- `descripcion_del_proceso`;
- `descripcion` de adiciones.

Ese texto es **dato no estructurado**. No tiene columnas limpias como "sector
real del contrato" o "tema de compra". En una solucion real, ese texto permite
buscar contratos por temas y construir senales sencillas.

Para mantener el taller realizable, no usaremos modelos avanzados de NLP.
Usaremos un metodo simple y transparente: diccionarios de palabras clave.

Ejemplo:

| Tema | Palabras de busqueda |
|---|---|
| Alimentacion | alimentacion, restaurante, cafeteria, suministro de alimentos |
| Infraestructura | obra, via, mantenimiento, construccion, interventoria |
| Salud | salud, hospital, medicamentos, ambulancia |
| Educacion | colegio, estudiantes, educativo, escolar |
| Tecnologia | software, licencias, sistemas, computadores |
| Servicios profesionales | prestacion de servicios, apoyo a la gestion, consultoria |

La ventaja pedagogica es que el estudiante entiende por que el texto debe
prepararse antes de buscarlo.
    """),
    md("""
### Mini ficha de funciones usadas

Funcion usada: `str.contains()`

- Para que sirve: busca si un texto contiene una palabra o patron.
- Parametros usados: patron de busqueda, `case=False`, `na=False`.
- Que devuelve: una serie de valores verdadero/falso.
- Como interpretar la salida: `True` indica que el texto contiene una senal del tema buscado.

Funcion usada: `re.sub()`

- Para que sirve: reemplaza partes de un texto usando expresiones regulares.
- Parametros usados: patron, reemplazo y texto.
- Que devuelve: texto limpio o transformado.
- Como interpretar la salida: permite quitar signos o espacios repetidos antes de analizar palabras.
    """),
    code("""
import re

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
    if not temas:
        temas.append("sin_tema_detectado")
    return temas

def palabras_frecuentes(textos, top=15):
    stopwords = {
        "DE", "LA", "EL", "LOS", "LAS", "Y", "EN", "PARA", "DEL", "CON", "POR",
        "A", "UN", "UNA", "QUE", "SE", "AL", "O", "SU", "SUS", "NO", "ES"
    }
    conteo = {}
    for texto in textos.dropna().astype(str):
        limpio = limpiar_texto_simple(texto)
        for palabra in limpio.split():
            if len(palabra) >= 5 and palabra not in stopwords:
                conteo[palabra] = conteo.get(palabra, 0) + 1
    return pd.DataFrame(
        sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:top],
        columns=["palabra", "frecuencia"]
    )

contratos_enriquecidos["texto_contrato_limpio"] = contratos_enriquecidos["objeto_del_contrato"].apply(limpiar_texto_simple)
contratos_enriquecidos["temas_detectados"] = contratos_enriquecidos["objeto_del_contrato"].apply(detectar_temas)

display(contratos_enriquecidos[["id_contrato", "objeto_del_contrato", "temas_detectados"]].head(10))
display(palabras_frecuentes(contratos_enriquecidos["objeto_del_contrato"], top=15))
    """),
    interp("texto no estructurado", [
        "El objeto contractual no viene como categoria limpia; hay que leerlo como texto libre.",
        "La clasificacion por palabras clave es simple, explicable y suficiente para un taller inicial.",
        "El resultado debe interpretarse como tema detectado automaticamente, no como clasificacion perfecta."
    ]),
    pregunta(
        6,
        "Datos no estructurados",
        "El objeto contractual es texto libre escrito por distintas entidades, con estilos y niveles de detalle diferentes.",
        "Cual es una forma simple y defendible de usar ese texto en este taller?",
        [
            "Ignorarlo porque no esta en columnas numericas.",
            "Detectar temas con palabras clave y guardar esos temas en MongoDB.",
            "Afirmar automaticamente que el texto prueba una irregularidad.",
            "Borrar todos los contratos con textos largos."
        ],
        "B",
        "La deteccion simple de temas permite usar texto no estructurado sin convertir el taller en un curso avanzado de NLP."
    ),
    md("""
---
# Parte 7 -- Indice descriptivo de prioridad

Este indice no detecta fraude. Solo ayuda a ordenar que revisar primero.

Regla pedagogica:

> Nunca digas que un contrato es irregular solo por aparecer en el ranking. Di
> que merece revision por las senales descriptivas encontradas.
    """),
    code("""
def calcular_prioridad(df):
    out = df.copy()
    valor = out["valor_del_contrato"].fillna(0)
    p75 = valor.quantile(0.75) if len(valor) else 0
    p90 = valor.quantile(0.90) if len(valor) else 0

    out["puntaje_valor"] = np.select(
        [valor >= p90, valor >= p75],
        [25, 15],
        default=0,
    )
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
        out["objeto_del_contrato"].fillna("").str.len() < 80,
        10,
        0,
    )
    out["indice_prioridad_revision"] = (
        out["puntaje_valor"] +
        out["puntaje_adiciones"] +
        out["puntaje_ejecucion"] +
        out["puntaje_modalidad"] +
        out["puntaje_texto"]
    ).clip(0, 100)

    def nivel(x):
        if x >= 70:
            return "alta"
        if x >= 40:
            return "media"
        return "baja"

    out["nivel_prioridad"] = out["indice_prioridad_revision"].apply(nivel)
    return out

contratos_scored = calcular_prioridad(contratos_enriquecidos)
display(
    contratos_scored.sort_values("indice_prioridad_revision", ascending=False)[[
        "id_contrato", "nombre_entidad", "proveedor_adjudicado", "valor_del_contrato",
        "numero_adiciones", "ultimo_avance_real", "modalidad_de_contratacion",
        "indice_prioridad_revision", "nivel_prioridad"
    ]].head(10)
)
    """),
    interp("indice de prioridad", [
        "El indice combina reglas transparentes que el equipo puede explicar.",
        "Un valor alto significa prioridad de revision, no culpabilidad.",
        "La ventaja para el negocio es ordenar recursos limitados de auditoria o seguimiento."
    ]),
    pregunta(
        7,
        "Prioridad descriptiva",
        "El indice ordena contratos para revision, pero no prueba causalidad ni irregularidad.",
        "Como debe interpretarse un contrato con prioridad alta?",
        [
            "Como prueba automatica de corrupcion.",
            "Como caso que merece revision por varias senales descriptivas.",
            "Como contrato que debe borrarse de la base.",
            "Como error de MongoDB."
        ],
        "B",
        "El ranking es una herramienta de priorizacion, no una sentencia."
    ),
    md("""
---
# Parte 8 -- Modelo documental de MongoDB

Aqui aparece la ganancia real de MongoDB. En vez de obligar al usuario a unir
tablas cada vez, guardamos una ficha completa por contrato.

Colecciones minimas:

| Coleccion | Proposito |
|---|---|
| `contratos_operativos` | ficha completa de cada contrato |
| `alertas_revision` | contratos con prioridad media o alta |
| `dashboard_kpis` | tarjetas ejecutivas |
| `dashboard_entidades` | resumen por entidad |
| `dashboard_proveedores` | resumen por proveedor |
| `dashboard_temas` | resumen de temas detectados en texto no estructurado |
| `metadata_pipeline` | trazabilidad de cargas |
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

def contrato_a_documento(row):
    return {
        "_id": row.get("id_contrato"),
        "id_contrato": row.get("id_contrato"),
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
        "texto_no_estructurado": {
            "objeto_limpio": limpiar_nan(row.get("texto_contrato_limpio")),
            "temas_detectados": limpiar_nan(row.get("temas_detectados")),
        },
        "adiciones": {
            "numero": limpiar_nan(row.get("numero_adiciones")),
            "ultima": limpiar_nan(row.get("ultima_adicion")),
            "tipos": limpiar_nan(row.get("tipos_adicion")),
            "descripciones": limpiar_nan(row.get("descripcion_adiciones")),
        },
        "prioridad": {
            "indice": limpiar_nan(row.get("indice_prioridad_revision")),
            "nivel": limpiar_nan(row.get("nivel_prioridad")),
        },
        "estado_revision": "pendiente",
    }

documentos_contratos = [
    contrato_a_documento(row)
    for _, row in contratos_scored.iterrows()
    if pd.notna(row.get("id_contrato"))
]

documentos_contratos[:1]
    """),
    pregunta(
        8,
        "Documento operativo",
        "El documento MongoDB guarda contrato, entidad, proveedor, territorio, adiciones, ejecucion y prioridad.",
        "Que gana el usuario de negocio con este modelo documental?",
        [
            "Debe hacer mas joins para ver una ficha.",
            "Puede consultar una ficha completa sin reconstruir tablas dispersas.",
            "Pierde la informacion de proveedor.",
            "Ya no necesita validar datos."
        ],
        "B",
        "MongoDB acerca el dato al modo como el usuario consulta: por contrato, proveedor, entidad o municipio."
    ),
    md("""
---
# Parte 9 -- Conexion y carga a MongoDB

Opciones:

1. **MongoDB Atlas recomendado:** configura una variable `MONGODB_URI`.
2. **MongoDB local:** levanta el perfil `nosql` o `final` del stack Docker del curso.

Comando local sugerido desde la carpeta `infraestructura/`:

```bash
docker compose --profile nosql up -d
```

La celda intenta conectarse. Si no hay Mongo disponible, guarda una muestra JSON
para que puedas revisar el modelo documental, pero el entregable final del equipo
debe cargar en MongoDB.
    """),
    code("""
import os
import json
from pathlib import Path

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
    print("No se pudo conectar a MongoDB en este entorno.")
    print("Detalle:", e)
    print("Se continuara con archivo JSON de respaldo para inspeccion.")

Path("salidas_taller_final").mkdir(exist_ok=True)

def cargar_contratos_mongo(documentos, etiqueta_lote):
    if not documentos:
        return {"insertados_o_actualizados": 0, "mongo_ok": mongo_ok}

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
            "insertados_o_actualizados": len(documentos),
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": len(result.upserted_ids),
            "mongo_ok": True,
        }

    salida = Path("salidas_taller_final") / f"{etiqueta_lote}_contratos_operativos.json"
    salida.write_text(json.dumps(documentos, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"insertados_o_actualizados": len(documentos), "mongo_ok": False, "archivo": str(salida)}

resultado_carga_1 = cargar_contratos_mongo(documentos_contratos, "lote_1")
resultado_carga_1
    """),
    interp("carga a MongoDB", [
        "`upsert` permite actualizar contratos existentes y crear contratos nuevos sin duplicar.",
        "La coleccion `metadata_pipeline` deja evidencia de cada corrida.",
        "Si Mongo no esta disponible, el JSON de respaldo sirve para inspeccionar el modelo, pero no reemplaza el entregable final."
    ]),
    md("""
### Mini ficha de funciones usadas

Funcion usada: `UpdateOne()`

- Para que sirve: define una operacion de actualizacion para MongoDB.
- Parametros usados: filtro por `_id`, documento con `$set`, `upsert=True`.
- Que devuelve: una operacion lista para ejecutarse en lote.
- Como interpretar la salida: si el contrato existe, se actualiza; si no existe, se crea.

Funcion usada: `bulk_write()`

- Para que sirve: ejecuta muchas operaciones de escritura en una sola llamada.
- Parametros usados: lista de operaciones.
- Que devuelve: conteos de documentos modificados, encontrados o insertados.
- Como interpretar la salida: permite verificar si el micro-batch realmente cambio MongoDB.
    """),
    pregunta(
        9,
        "Upsert",
        "El pipeline puede recibir contratos ya existentes o nuevos en cada micro-batch.",
        "Por que se usa `upsert=True`?",
        [
            "Para borrar contratos duplicados sin revisar.",
            "Para actualizar si existe y crear si no existe.",
            "Para impedir que MongoDB guarde documentos.",
            "Para convertir automaticamente MongoDB en Spark."
        ],
        "B",
        "`upsert` es clave en pipelines incrementales porque evita duplicar y permite refrescar fichas."
    ),
    md("""
---
# Parte 10 -- Colecciones para dashboard

Un dashboard no deberia calcular todo desde cero. Conviene dejar colecciones
resumen listas para graficar.

Estas colecciones se pueden leer desde Atlas Charts, Streamlit, Power BI,
Looker Studio u otra herramienta. En MongoDB Atlas Charts, el dashboard puede
refrescarse automaticamente segun la configuracion disponible del cluster.
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

    temas_rows = []
    for _, row in df.iterrows():
        temas = row.get("temas_detectados", [])
        if not isinstance(temas, list):
            temas = ["sin_tema_detectado"]
        for tema in temas:
            temas_rows.append({
                "tema": tema,
                "id_contrato": row.get("id_contrato"),
                "valor_del_contrato": row.get("valor_del_contrato", 0),
                "nivel_prioridad": row.get("nivel_prioridad"),
            })
    temas_base = pd.DataFrame(temas_rows)
    if temas_base.empty:
        temas = pd.DataFrame(columns=["tema", "total_contratos", "valor_total", "prioridad_alta"])
    else:
        temas = (
            temas_base.groupby("tema", dropna=False)
            .agg(
                total_contratos=("id_contrato", "count"),
                valor_total=("valor_del_contrato", "sum"),
                prioridad_alta=("nivel_prioridad", lambda s: int((s == "alta").sum())),
            )
            .reset_index()
            .sort_values("total_contratos", ascending=False)
        )

    alertas = df[df["nivel_prioridad"].isin(["media", "alta"])].copy()
    alertas = alertas[[
        "id_contrato", "nombre_entidad", "proveedor_adjudicado", "departamento", "ciudad",
        "valor_del_contrato", "numero_adiciones", "ultimo_avance_real",
        "indice_prioridad_revision", "nivel_prioridad", "temas_detectados"
    ]].sort_values("indice_prioridad_revision", ascending=False)

    return {
        "dashboard_kpis": kpis,
        "dashboard_entidades": entidades,
        "dashboard_proveedores": proveedores,
        "dashboard_temas": temas,
        "alertas_revision": alertas,
    }

dashboard_frames = construir_dashboard_frames(contratos_scored)

for nombre, frame in dashboard_frames.items():
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
        salida = Path("salidas_taller_final") / f"{etiqueta_lote}_{nombre}.json"
        salida.write_text(frame.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
        salidas[nombre] = str(salida)
    return {"mongo_ok": False, "archivos": salidas}

resultado_dashboard_1 = cargar_dashboard_mongo(dashboard_frames, "lote_1")
resultado_dashboard_1
    """),
    interp("dashboard", [
        "Las colecciones `dashboard_*` reducen trabajo para la herramienta visual.",
        "La coleccion `alertas_revision` representa la bandeja operativa de casos a revisar.",
        "El dashboard debe mostrar cambios despues de ejecutar una segunda carga."
    ]),
    md("""
---
# Parte 11 -- Segunda carga: simulacion casi en tiempo real

Ahora ejecutamos un segundo micro-batch. En una operacion real, este paso lo
haria un job programado, Databricks Workflows, un script con `cron` o, si el
equipo quiere ir mas alla, Airflow. Para este taller **Airflow es opcional**:
la evidencia principal debe verse en el notebook, MongoDB y el dashboard.

La evidencia esperada:

- se descargan nuevos contratos desde 2021;
- se recalculan indicadores;
- MongoDB actualiza o inserta documentos;
- las colecciones de dashboard cambian;
- `metadata_pipeline` registra una nueva corrida.
    """),
    code("""
contratos_2 = descargar_contratos_batch(BATCH_SIZE, OFFSET_2)
ids_2 = contratos_2["id_contrato"].dropna().unique().tolist()
adiciones_2 = descargar_adiciones(ids_2)
ejecucion_2 = descargar_ejecucion(ids_2)

contratos_2_limpios = preparar_contratos(contratos_2)
contratos_2_geo = contratos_2_limpios.merge(
    divipola_limpia[["cod_dpto", "cod_mpio", "dpto", "nom_mpio", "departamento_norm", "ciudad_norm", "latitud_num", "longitud_num"]],
    on=["departamento_norm", "ciudad_norm"],
    how="left",
)

contratos_2_enriquecidos = (
    contratos_2_geo
    .merge(resumir_adiciones(adiciones_2), on="id_contrato", how="left")
    .merge(resumir_ejecucion(ejecucion_2), on="id_contrato", how="left")
)
contratos_2_enriquecidos["numero_adiciones"] = contratos_2_enriquecidos["numero_adiciones"].fillna(0).astype(int)
contratos_2_enriquecidos["ultimo_avance_real"] = contratos_2_enriquecidos["ultimo_avance_real"].fillna(0)
contratos_2_enriquecidos["texto_contrato_limpio"] = contratos_2_enriquecidos["objeto_del_contrato"].apply(limpiar_texto_simple)
contratos_2_enriquecidos["temas_detectados"] = contratos_2_enriquecidos["objeto_del_contrato"].apply(detectar_temas)
contratos_2_scored = calcular_prioridad(contratos_2_enriquecidos)

documentos_contratos_2 = [
    contrato_a_documento(row)
    for _, row in contratos_2_scored.iterrows()
    if pd.notna(row.get("id_contrato"))
]

resultado_carga_2 = cargar_contratos_mongo(documentos_contratos_2, "lote_2")
dashboard_frames_2 = construir_dashboard_frames(contratos_2_scored)
resultado_dashboard_2 = cargar_dashboard_mongo(dashboard_frames_2, "lote_2")

print("Carga lote 2:", resultado_carga_2)
print("Dashboard lote 2:", resultado_dashboard_2)
display(contratos_2_scored.sort_values("indice_prioridad_revision", ascending=False).head(5))
    """),
    pregunta(
        10,
        "Actualizacion casi en tiempo real",
        "La segunda carga demuestra que el observatorio puede refrescar fichas, alertas y KPIs.",
        "Que evidencia muestra que el pipeline se actualizo?",
        [
            "Que el notebook tiene mas texto.",
            "Que MongoDB registra una nueva carga y las colecciones del dashboard cambian.",
            "Que se borra la primera muestra.",
            "Que se deja de filtrar desde 2021."
        ],
        "B",
        "La evidencia operacional esta en MongoDB: documentos, resumenes y metadata de la nueva corrida."
    ),
    md("""
---
# Parte 12 -- Consultas de negocio en MongoDB

Estas consultas solo se ejecutan si hay conexion a MongoDB. Sirven para probar
que Mongo no es decorativo: responde preguntas operativas.
    """),
    code("""
if mongo_ok:
    print("Contratos de prioridad alta")
    display(pd.DataFrame(list(db.contratos_operativos.find(
        {"prioridad.nivel": "alta"},
        {"_id": 0, "id_contrato": 1, "valor": 1, "entidad.nombre": 1, "proveedor.nombre": 1, "prioridad": 1}
    ).limit(10))))

    print("Top entidades del dashboard")
    display(pd.DataFrame(list(db.dashboard_entidades.find(
        {},
        {"_id": 0}
    ).sort("valor_total", -1).limit(10))))

    print("Busqueda textual sugerida")
    print("Para habilitar busqueda por objeto, crear un indice de texto sobre `objeto`.")
else:
    print("MongoDB no esta conectado. Revisa los archivos JSON de salidas_taller_final o configura MONGODB_URI.")
    """),
    md("""
### Indice de texto recomendado

En MongoDB se puede crear un indice de texto para buscar por objeto contractual.
Este punto conecta directamente con los datos no estructurados del taller:

```python
db.contratos_operativos.create_index([("objeto", "text")])
db.contratos_operativos.find({"$text": {"$search": "alimentacion escolar infraestructura"}})
```

Esto es una ganancia clara frente a una tabla plana: el observatorio permite
explorar contratos por temas y no solo por codigos.
    """),
    md("""
---
# Parte 13 -- Dashboard esperado

El equipo debe crear un dashboard en MongoDB Atlas Charts o herramienta
equivalente. Lo importante no es la herramienta visual: lo importante es que
lea desde las colecciones MongoDB actualizadas por el pipeline.

Panel minimo:

1. **KPIs ejecutivos**
   - total de contratos monitoreados;
   - valor total;
   - contratos con prioridad alta;
   - contratos con adiciones;
   - proveedores unicos;
   - entidades unicas.

2. **Alertas de revision**
   - tabla ordenada por `indice_prioridad_revision`;
   - filtros por departamento, entidad, proveedor y nivel.

3. **Entidades**
   - ranking por valor total;
   - contratos con adiciones;
   - prioridad promedio.

4. **Proveedores**
   - top por valor;
   - numero de entidades atendidas;
   - prioridad promedio.

5. **Territorio**
   - ranking por departamento o municipio;
   - extension: cruzar con poblacion o IPM.

6. **Texto no estructurado**
   - ranking de temas detectados;
   - buscador por palabra clave;
   - contratos cuyo objeto menciona alimentacion, infraestructura, salud, educacion o tecnologia.

Prueba obligatoria:

> Ejecuta el lote 1, toma captura del dashboard. Ejecuta el lote 2, refresca el
> dashboard y toma una segunda captura. Explica que cambio.
    """),
    md("""
---
# Parte 14 -- Entregables del taller final

Cada equipo debe entregar:

1. Cuaderno ejecutado con evidencia de fuentes desde 2021.
2. Diagrama de arquitectura.
3. Diccionario de datos de las fuentes usadas.
4. Modelo documental MongoDB.
5. Uso simple de datos no estructurados: temas detectados o busqueda textual.
6. Pipeline incremental con al menos dos cargas.
7. Colecciones MongoDB:
   - `contratos_operativos`
   - `alertas_revision`
   - `dashboard_kpis`
   - `dashboard_entidades`
   - `dashboard_proveedores`
   - `dashboard_temas`
   - `metadata_pipeline`
8. Dashboard conectado a MongoDB.
9. Capturas antes/despues de la segunda carga.
10. Informe ejecutivo con hallazgos, limites y recomendaciones.

## Rubrica sugerida

| Criterio | Peso |
|---|---:|
| Verificacion y uso correcto de fuentes desde 2021 | 15% |
| Integracion de multiples bases y tipos de datos | 15% |
| Limpieza, transformacion y enriquecimiento | 15% |
| Uso simple de texto no estructurado | 10% |
| Modelo documental MongoDB y carga con `upsert` | 15% |
| Dashboard actualizado desde MongoDB | 10% |
| Interpretacion de negocio y limites del analisis | 15% |
| Reproducibilidad y documentacion | 10% |
    """),
    md("""
## Cierre de sesion

### Recapitulacion

Construimos el plan ejecutable de un observatorio casi en tiempo real:
verificamos fuentes, descargamos micro-batches desde 2021, enriquecimos contratos,
calculamos prioridad descriptiva, modelamos documentos MongoDB y dejamos
colecciones listas para dashboard.

### Idea mas importante

MongoDB no reemplaza el procesamiento. MongoDB convierte el resultado procesado
en una capa operativa consultable: fichas, alertas, busquedas y dashboard.

### Errores comunes

- Llamar "fraude" a una senal descriptiva.
- No filtrar desde 2021.
- Guardar todo como una sola tabla sin modelo documental.
- Cargar MongoDB con duplicados en vez de usar `upsert`.
- Crear un dashboard desconectado del pipeline.

### Proxima sesion

Presentacion del proyecto final: arquitectura, evidencia de ejecucion,
dashboard actualizado y lectura critica de resultados.

## Referencias

- SECOP II Contratos Electronicos: https://www.datos.gov.co/resource/jbjy-vk9h.json
- SECOP II Adiciones: https://www.datos.gov.co/resource/cb9c-h8sn.json
- SECOP II Ejecucion Contratos: https://www.datos.gov.co/resource/mfmm-jqmq.json
- DIVIPOLA municipios: https://www.datos.gov.co/resource/gdxc-w37w.json
- Socrata API: https://dev.socrata.com/
- MongoDB Change Streams: https://www.mongodb.com/docs/manual/changestreams/
- MongoDB Atlas Charts: https://www.mongodb.com/docs/charts/
    """),
]


if __name__ == "__main__":
    validate(cells)
    save(cells, "Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb")
