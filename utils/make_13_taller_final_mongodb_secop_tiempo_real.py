# -*- coding: utf-8 -*-
"""
Genera Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb

Enunciado de taller final: reto aplicado de observatorio operativo de
contratacion publica con SECOP II desde 2021, NoSQL, texto no estructurado,
MongoDB y dashboard.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import md, code, save, validate, uce_header


cells = [
    *uce_header(
        title="Taller final: Observatorio operativo de contratación pública con MongoDB",
        session=13,
        github_path="main/Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb",
        nota_plataforma="Entrega final con todos los datos disponibles desde 2021. MongoDB Atlas recomendado.",
    ),
    md("""
# Enunciado del taller final

Este taller no es una clase paso a paso. Es un **reto aplicado**.

Cada equipo debe construir un prototipo funcional de observatorio de contratación
pública usando datos reales de SECOP II desde `2021-01-01` hasta el día de la
descarga.

El profesor solo verificará que el flujo funcione, que los datos sean reales y
que la solución tenga sentido técnico y de negocio. No se calificará copiar
funciones de este cuaderno, sino la solución construida por el equipo.
    """),
    md("""
## Dolor real que debe superar la solución

Una oficina de control interno, planeación o seguimiento contractual recibe
contratos nuevos y modificaciones todos los días. El equipo de negocio necesita
responder preguntas como:

- ¿Qué contratos recientes deberían revisarse primero?
- ¿Qué proveedores concentran más valor contratado?
- ¿Qué entidades tienen más contratos con adiciones?
- ¿Qué temas aparecen con frecuencia en los objetos contractuales?
- ¿Qué contratos mezclan alto valor, adiciones, baja ejecución o textos poco claros?
- ¿Cómo mostrar esta información en un tablero sin rehacer manualmente todos los cruces?

Hoy el dolor es que la información está dispersa:

- contratos en una base;
- adiciones en otra;
- ejecución contractual en otra;
- municipio/departamento en otra;
- texto libre en objetos contractuales y descripciones;
- resultados finales que suelen quedar en archivos sueltos, no en una capa consultable.

El reto consiste en convertir ese desorden en una herramienta operativa.
    """),
    md("""
## Reto central

Construir un observatorio que integre contratos públicos desde 2021, detecte
señales descriptivas de prioridad y publique resultados consultables en MongoDB
para alimentar un dashboard.

La solución debe responder:

> ¿Qué contratos, proveedores, entidades, territorios y temas merecen revisión
> prioritaria, y qué evidencia de datos soporta esa recomendación?

Importante:

- No se debe afirmar fraude.
- No se debe afirmar corrupción.
- No se debe afirmar causalidad.
- Sí se debe priorizar revisión con reglas transparentes.
    """),
    md("""
## Alcance obligatorio de datos

La entrega final debe usar **todos los registros que el equipo pueda descargar
desde SECOP II a partir de `2021-01-01`**, no solo una muestra pequeña.

El equipo debe reportar:

| Elemento | Debe reportarse |
|---|---|
| Fecha y hora de descarga | Día, hora y zona horaria |
| Rango temporal | Desde `2021-01-01` hasta la fecha de descarga |
| Número de contratos descargados | Total de registros usados |
| Número de adiciones descargadas | Total de registros usados |
| Número de registros de ejecución | Total de registros usados |
| Fuente territorial | DIVIPOLA u otra fuente justificada |
| Limitaciones | Errores de API, cortes, columnas faltantes, registros sin cruce |

Para pruebas en clase pueden usar lotes pequeños. Para la entrega final deben
trabajar con el dataset completo descargado desde 2021, o justificar
técnicamente cualquier límite de descarga.
    """),
    md("""
## Fuentes mínimas obligatorias

| Fuente | Endpoint | Rol en la solución |
|---|---|---|
| SECOP II contratos electrónicos | `https://www.datos.gov.co/resource/jbjy-vk9h.json` | Base principal de contratos |
| SECOP II adiciones | `https://www.datos.gov.co/resource/cb9c-h8sn.json` | Modificaciones y adiciones |
| SECOP II ejecución contractual | `https://www.datos.gov.co/resource/mfmm-jqmq.json` | Avance y estado de ejecución |
| DIVIPOLA municipios | `https://www.datos.gov.co/resource/gdxc-w37w.json` | Normalización territorial |

Fuentes opcionales para subir nivel:

- población municipal;
- IPM o indicadores socioeconómicos;
- presupuesto territorial;
- datos sectoriales de salud, educación o infraestructura.
    """),
    md("""
## Arquitectura esperada

La solución debe seguir esta arquitectura mínima:

```text
Datos abiertos desde 2021
  SECOP contratos
  SECOP adiciones
  SECOP ejecución
  DIVIPOLA / territorio
        ↓
Zona raw
  archivos originales descargados
        ↓
Zona limpia
  fechas, valores, texto, territorio
        ↓
Integración
  contratos + adiciones + ejecución + territorio
        ↓
Tratamiento de texto no estructurado
  objeto contractual + descripción de adiciones
  texto_busqueda
  temas_detectados
        ↓
Índice descriptivo de prioridad
        ↓
MongoDB / NoSQL
  contratos_operativos
  alertas_revision
  entidades_resumen
  proveedores_resumen
  temas_resumen
  metadata_pipeline
        ↓
Dashboard operativo
  KPIs, alertas, proveedores, entidades, temas, actualización
```
    """),
    md("""
## Qué significa usar NoSQL de verdad

MongoDB no debe usarse como una tabla plana.

El valor de MongoDB en este taller es guardar **fichas operativas**. Cada
contrato debe quedar como un documento que concentre la información necesaria
para consulta:

```json
{
  "id_contrato": "...",
  "valor": 123000000,
  "entidad": {
    "nit": "...",
    "nombre": "...",
    "sector": "..."
  },
  "proveedor": {
    "documento": "...",
    "nombre": "..."
  },
  "territorio": {
    "departamento": "...",
    "municipio": "...",
    "codigo_divipola": "..."
  },
  "adiciones": {
    "numero": 2,
    "descripcion": "..."
  },
  "ejecucion": {
    "avance_real": 45.0,
    "estado": "..."
  },
  "texto_no_estructurado": {
    "texto_busqueda": "...",
    "temas_detectados": ["infraestructura", "servicios_profesionales"]
  },
  "prioridad": {
    "indice": 75,
    "nivel": "alta"
  }
}
```

El equipo debe demostrar:

- documentos anidados;
- carga con `upsert`;
- índices por prioridad, entidad, proveedor y texto;
- búsqueda textual;
- agregaciones por tema, entidad o proveedor;
- actualización después de una nueva carga.
    """),
    md("""
## Qué significa usar datos no estructurados

En este taller, el dato no estructurado es el **texto libre**.

Ejemplos:

- `objeto_del_contrato`;
- `descripcion` de adiciones;
- descripciones largas que no vienen como categoría limpia.

El equipo debe convertir ese texto en un insumo útil:

1. unir textos relevantes en un campo llamado `texto_busqueda`;
2. limpiar mayúsculas, tildes, signos y espacios;
3. crear reglas de temas por palabras clave;
4. producir una columna/lista `temas_detectados`;
5. guardar esos temas en MongoDB;
6. permitir búsqueda textual en MongoDB;
7. mostrar temas en el dashboard.

Ejemplo de temas:

| Tema | Palabras de referencia |
|---|---|
| alimentación | alimentación, alimentos, comedor, restaurante |
| infraestructura | obra, vía, construcción, mantenimiento |
| salud | salud, hospital, medicamento, ambulancia |
| educación | colegio, estudiante, escolar, docente |
| tecnología | software, licencia, sistema, plataforma |
| servicios profesionales | prestación de servicios, apoyo a la gestión, consultoría |

No se exige machine learning. Sí se exige explicar las reglas y sus limitaciones.
    """),
    md("""
## Actividades del taller

### Actividad 1. Descarga completa desde 2021

Descargar contratos, adiciones y ejecución contractual desde `2021-01-01`.
Guardar los datos crudos y reportar fecha/hora de descarga.

Resultado esperado:

- archivos raw;
- conteo de registros;
- evidencia del filtro temporal.

### Actividad 2. Limpieza e integración

Convertir tipos de datos y unir las bases.

Resultado esperado:

- contratos con valores numéricos;
- fechas convertidas;
- adiciones resumidas por contrato;
- último avance de ejecución;
- cruce territorial con DIVIPOLA;
- reporte de registros sin cruce territorial.

### Actividad 3. Texto no estructurado

Crear `texto_busqueda` y `temas_detectados`.

Resultado esperado:

- tabla con contratos y temas;
- resumen de contratos por tema;
- explicación de reglas y limitaciones.

### Actividad 4. Índice de prioridad

Diseñar un índice descriptivo.

Puede incluir:

- valor alto;
- número de adiciones;
- avance bajo;
- modalidad contractual;
- tema detectado;
- texto insuficiente o ambiguo.

Resultado esperado:

- ranking de contratos;
- niveles baja, media y alta;
- explicación de la fórmula.

### Actividad 5. Modelo NoSQL en MongoDB

Crear colecciones documentales.

Colecciones mínimas:

- `contratos_operativos`;
- `alertas_revision`;
- `entidades_resumen`;
- `proveedores_resumen`;
- `temas_resumen`;
- `metadata_pipeline`.

Resultado esperado:

- documentos anidados;
- índices;
- consultas;
- agregaciones;
- evidencia de actualización.

### Actividad 6. Dashboard

Construir un tablero con:

- total de contratos;
- valor total;
- contratos con prioridad alta;
- contratos con adiciones;
- ranking de entidades;
- ranking de proveedores;
- temas detectados;
- tabla de alertas.

Resultado esperado:

- dashboard o capturas;
- evidencia antes/después de una actualización.
    """),
    md("""
## Entregables

La entrega debe tener esta estructura:

```text
entrega_equipo/
  notebook_o_scripts/
  datos_muestra_o_enlaces/
  evidencia_mongodb/
  evidencia_dashboard/
  arquitectura.png
  informe_ejecutivo.pdf
  README.md
```

El `README.md` debe incluir:

- integrantes;
- fecha y hora de descarga;
- número de registros usados;
- instrucciones para reproducir;
- variables de entorno necesarias;
- decisiones de arquitectura;
- limitaciones encontradas.
    """),
    md("""
## Criterios de aceptación

El taller se acepta si cumple todo lo siguiente:

- usa datos desde 2021;
- reporta fecha/hora de descarga;
- trabaja con volumen completo descargado o justifica límite técnico;
- integra al menos contratos, adiciones, ejecución y territorio;
- usa texto no estructurado de forma verificable;
- crea un modelo documental NoSQL;
- carga o exporta documentos operativos;
- construye resumen para dashboard;
- presenta hallazgos sin afirmar fraude;
- permite reproducir la lógica principal.
    """),
    md("""
---
## PARTE 5 — Rúbrica de Evaluación

El taller debe realizarse en grupos de máximo tres estudiantes. Deberán
compartir el notebook/script, el análisis, la evidencia de MongoDB/dashboard y
el informe a más tardar en la fecha indicada por el profesor, enviándolo con el
asunto:

`[BigData] Taller Final SECOP MongoDB`

Adicionalmente deben informar el día y hora de la descarga, debido a que SECOP
II recibe nuevos registros y actualizaciones diariamente.

**Total: 100 puntos + 10 puntos bonus**

### Componentes evaluables

| Componente | Producto esperado | Puntos |
|---|---|---:|
| **1. Descarga completa desde 2021** | Datos desde `2021-01-01`, fecha/hora de descarga, conteos y evidencia de filtros. | 10 |
| **2. Limpieza de datos** | Fechas, valores, texto y nulos tratados correctamente. | 10 |
| **3. Integración de bases** | Contratos unidos con adiciones, ejecución y territorio. | 15 |
| **4. Datos no estructurados** | `texto_busqueda`, `temas_detectados`, resumen por tema y explicación de reglas. | 15 |
| **5. Índice de prioridad** | Fórmula clara, ranking reproducible y niveles de prioridad. | 10 |
| **6. NoSQL MongoDB** | Documentos anidados, `upsert`, índices, búsqueda textual, consultas y agregaciones. | 20 |
| **7. Dashboard operativo** | KPIs, alertas, entidades, proveedores, temas y evidencia de actualización. | 10 |
| **8. Informe ejecutivo** | Hallazgos, límites, recomendaciones y lectura responsable. | 10 |

**Bonus +10:** usar 100.000+ contratos desde 2021, incluir una fuente social
adicional o automatizar la actualización sin romper la reproducibilidad.

---

### Criterios generales

| Criterio | Descripción |
|----------|-------------|
| **Limpieza de datos** | Convierte tipos correctamente. Maneja nulos sin eliminar filas innecesariamente. Normaliza texto donde corresponde. |
| **Integración** | Une bases con llaves claras y reporta registros sin cruce. |
| **No estructurado** | Usa texto libre real, crea temas y explica limitaciones. |
| **NoSQL** | Usa MongoDB como modelo documental, no como tabla plana. |
| **Correctitud** | Resultados coherentes, reproducibles y no hardcodeados. |
| **Visualización** | Dashboard claro, con títulos, filtros y evidencia de actualización. |
| **Interpretación** | Explica qué se observa, qué implica y qué no se puede concluir. |

---

### Tabla de niveles por criterio

| Criterio | Excelente (100%) | Satisfactorio (70%) | Insuficiente (40%) | No entregado (0%) |
|----------|-----------------|---------------------|--------------------|------------------|
| **Descarga** | Descarga amplia desde 2021, documentada y reproducible | Descarga desde 2021 con volumen limitado justificado | Muestra pequeña sin justificación suficiente | Sin descarga válida |
| **Limpieza** | Tipos correctos, nulos tratados y texto normalizado | Limpieza funcional con errores menores | Tipos incorrectos o nulos mal manejados | Sin limpieza |
| **Integración** | Cruces completos y limitaciones documentadas | Cruces principales funcionan | Integración parcial o confusa | Sin integración |
| **Texto no estructurado** | Reglas claras, temas útiles, búsqueda textual y limitaciones | Temas básicos con explicación limitada | Texto usado de forma superficial | No usa texto |
| **NoSQL MongoDB** | Documentos anidados, índices, `upsert`, consultas y agregaciones | Carga documentos y algunas consultas | MongoDB como tabla plana o solo JSON | Sin NoSQL |
| **Dashboard** | Operativo, claro y actualizado | Dashboard básico | Gráficas sueltas sin conexión clara | Sin dashboard |
| **Informe** | Ejecutivo, crítico y responsable | Describe resultados básicos | Superficial o sin límites | Sin informe |

---

### Penalizaciones

| Situación | Penalización |
|-----------|-------------:|
| No informar fecha/hora de descarga | -5 |
| No filtrar desde `2021-01-01` | -15 |
| Usar solo micro-muestra sin justificar | -10 |
| Resultados hardcodeados | -20 |
| Código que no corre y no se explica | -10 |
| MongoDB usado como tabla plana | -10 |
| No demostrar consultas NoSQL | -10 |
| No usar texto no estructurado | -15 |
| Afirmar fraude/corrupción sin evidencia causal | -10 |
| No entregar dashboard ni evidencia equivalente | -15 |

---

### Nota sobre descarga completa

Para revisar en clase se puede probar con pocos registros. Para la entrega final
deben trabajar con todos los datos descargables desde 2021 según su capacidad
técnica.

Si el volumen completo es demasiado grande para el equipo, deben entregar:

- evidencia del intento de descarga;
- límite técnico encontrado;
- número máximo de registros procesados;
- justificación de por qué ese volumen sigue siendo representativo para el reto.

La descarga debe hacerse con paginación y sin sobrecargar la API.
    """),
    md("""
## Matriz de verificación para el profesor

| Elemento | Evidencia esperada | Cumple |
|---|---|---|
| Datos desde 2021 | Filtros, conteos y fecha/hora de descarga |  |
| Volumen usado | Total de contratos, adiciones y ejecución |  |
| Limpieza | Tipos convertidos y nulos tratados |  |
| Integración | Contratos + adiciones + ejecución + territorio |  |
| Texto no estructurado | `texto_busqueda`, `temas_detectados`, resumen por tema |  |
| Prioridad | Fórmula y ranking |  |
| MongoDB | Documentos anidados, índices y consultas |  |
| Dashboard | KPIs, alertas, entidades, proveedores y temas |  |
| Actualización | Evidencia de carga nueva o actualización |  |
| Informe | Hallazgos, límites y recomendaciones |  |
    """),
    md("""
## Anexo mínimo de verificación técnica

Este anexo no resuelve el taller. Solo ayuda al profesor o al equipo a probar
que los endpoints responden.
    """),
    code("""
import requests
import pandas as pd

BASE = "https://www.datos.gov.co/resource"
FECHA_INICIO = "2021-01-01T00:00:00"

pruebas = {
    "contratos": (
        f"{BASE}/jbjy-vk9h.json",
        {
            "$select": "id_contrato,fecha_de_firma,valor_del_contrato,objeto_del_contrato",
            "$where": f"fecha_de_firma >= '{FECHA_INICIO}'",
            "$limit": 3,
        },
    ),
    "adiciones": (
        f"{BASE}/cb9c-h8sn.json",
        {
            "$select": "id_contrato,tipo,descripcion,fecharegistro",
            "$where": f"fecharegistro >= '{FECHA_INICIO}'",
            "$limit": 3,
        },
    ),
    "ejecucion": (
        f"{BASE}/mfmm-jqmq.json",
        {
            "$select": "identificadorcontrato,fechacreacion,porcentaje_de_avance_real",
            "$where": f"fechacreacion >= '{FECHA_INICIO}'",
            "$limit": 3,
        },
    ),
    "divipola": (
        f"{BASE}/gdxc-w37w.json",
        {"$limit": 3},
    ),
}

for nombre, (url, params) in pruebas.items():
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    print(nombre, df.shape)
    display(df)
    """),
    md("""
## Cierre

La entrega final debe mostrar una solución que ayude a decidir qué revisar
primero. Si el resultado solo es una tabla o un gráfico aislado, no cumple el
propósito del taller.

Referencias:

- SECOP II contratos: https://www.datos.gov.co/resource/jbjy-vk9h.json
- SECOP II adiciones: https://www.datos.gov.co/resource/cb9c-h8sn.json
- SECOP II ejecución: https://www.datos.gov.co/resource/mfmm-jqmq.json
- DIVIPOLA: https://www.datos.gov.co/resource/gdxc-w37w.json
- API Socrata: https://dev.socrata.com/
- MongoDB Atlas Charts: https://www.mongodb.com/docs/charts/
    """),
]


if __name__ == "__main__":
    validate(cells)
    save(cells, "Cuadernos/13_Taller_Final_MongoDB_SECOP_Tiempo_Real.ipynb")
