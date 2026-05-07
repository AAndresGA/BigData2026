# -*- coding: utf-8 -*-
"""
utils/make_notebook.py
======================
Generador de cuadernos Jupyter para el curso Big Data – Universidad Central.

Uso rápido
----------
    from utils.make_notebook import md, code, sh, save, uce_header

    cells = [
        *uce_header(
            title="Mi Sesión",
            session=8,
            github_path="main/Cuadernos/8_mi_sesion.ipynb",
            nota_plataforma="Databricks Community Edition",
        ),
        md(\"\"\"
        ## Introducción
        Texto de la sección...
        \"\"\"),
        code(\"\"\"
        print("Hola Spark")
        \"\"\"),
        sh(\"\"\"
        pip install dask -q
        \"\"\"),
    ]

    save(cells, "Cuadernos/8_mi_sesion.ipynb")

Lecciones aprendidas (por qué existe este archivo)
----------------------------------------------------
- Los cuadernos .ipynb son JSON. Generarlos a mano causa errores de escaping
  cuando el código contiene docstrings, f-strings con llaves, o caracteres UTF-8.
- Este módulo centraliza el manejo de encoding y la conversión de multi-line
  strings al formato de lista que espera nbformat 4.
- Regla crítica: NUNCA usar triple-comillas dobles (\"\"\") dentro del texto que
  pasas a code() — usa triple-comillas simples (''') para docstrings internos.
  La función code() detecta esto y lanza un aviso útil.
"""

import json
import os
import re
import textwrap
from datetime import date
from typing import List, Dict, Any

# ─── Tipos ────────────────────────────────────────────────────────────────────

Cell = Dict[str, Any]
Notebook = Dict[str, Any]


# ─── Helpers de conversión ────────────────────────────────────────────────────

def _to_source(text: str) -> List[str]:
    """
    Convierte un string multi-línea al formato source[] de nbformat 4.

    Cada línea (menos la última) termina en \\n.
    El texto se dedenta automáticamente para que no importe cuánta
    indentación extra tenga el string literal en el código del generador.
    """
    text = textwrap.dedent(text).strip("\n")
    if not text:
        return [""]
    lines = text.split("\n")
    if len(lines) == 1:
        return [lines[0]]
    return [line + "\n" for line in lines[:-1]] + [lines[-1]]


# ─── Constructores de celdas ──────────────────────────────────────────────────

def md(text: str) -> Cell:
    """Crea una celda Markdown."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": _to_source(text),
    }


def code(text: str, warn_on_triple_quotes: bool = True) -> Cell:
    """
    Crea una celda de código Python.

    Detecta si el texto contiene triple-comillas dobles (\"\"\") que podrían
    romper futuros generadores y lanza un aviso.  Usa ''' para docstrings
    internos dentro de tus celdas.
    """
    if warn_on_triple_quotes and '"""' in text:
        # Mostrar advertencia pero continuar — mejor que fallar silenciosamente
        import warnings
        warnings.warn(
            "La celda contiene triple-comillas dobles (\"\"\"). "
            "Si vas a usar docstrings dentro del código de la celda, "
            "usa ''' en su lugar para evitar romper el generador.",
            stacklevel=2,
        )
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _to_source(text),
    }


def sh(text: str) -> Cell:
    """
    Crea una celda de código con magic %sh (shell).

    Equivalente a anteponer %sh automáticamente.
    """
    body = textwrap.dedent(text).strip("\n")
    return code("%sh\n" + body)


# ─── Plantillas de encabezado UCE ─────────────────────────────────────────────

def uce_header(
    title: str,
    session: int,
    github_path: str,
    nota_plataforma: str = "",
    autor: str = "jazaineam1",
) -> List[Cell]:
    """
    Devuelve una lista de celdas con el encabezado estándar del curso.

    Parámetros
    ----------
    title           : Título del cuaderno (ej. "Hadoop, YARN y Spark")
    session         : Número de sesión (ej. 7)
    github_path     : Path relativo al repo (ej. "main/Cuadernos/7_foo.ipynb")
    nota_plataforma : Texto de aviso de plataforma (ej. "Databricks Community Edition")
    autor           : Usuario de GitHub del repositorio
    """
    repo = f"https://github.com/{autor}/BigData2026"
    nb_url = f"https://colab.research.google.com/github/{autor}/BigData2026/blob/{github_path}"

    badge_cell = md(
        f'<a href="{nb_url}" target="_parent">'
        f'<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        f'alt="Open In Colab"/></a>'
        + (
            f'\n\n> ⚠️ **Plataforma recomendada: {nota_plataforma}**'
            if nota_plataforma
            else ""
        )
    )

    title_cell = md(f"""
    # {title}

    ## Universidad Central
    > ### Facultad de Ingeniería y Ciencias Básicas
    > ### Maestría en Analítica de Datos -- Big Data

    ![Universidad Central](https://www.ucentral.edu.co/themes/ucentral/img/template/Universidad%20Central.png)

    > **Sesión {session}** · {date.today().strftime("%Y")}
    """)

    return [badge_cell, title_cell]


def toc(sections: List[str]) -> Cell:
    """
    Genera una celda de Tabla de Contenidos como lista Markdown.

    Ejemplo:
        toc(["Sección 1 — Hadoop", "Sección 2 — YARN", "Sección 3 — Spark"])
    """
    items = "\n".join(f"- {s}" for s in sections)
    return md(f"## Contenido\n\n{items}")


def section_header(number: str, title: str, emoji: str = "") -> Cell:
    """
    Genera un divisor de sección estándar.

    Ejemplo:
        section_header("1", "Hadoop en Profundidad", "🏗️")
    """
    prefix = f"{emoji} " if emoji else ""
    return md(f"---\n# Sección {number} -- {prefix}{title}")


# ─── Constructor del notebook ─────────────────────────────────────────────────

def build(cells: List[Cell], python_version: str = "3.10.0") -> Notebook:
    """
    Ensambla la estructura JSON completa de un notebook nbformat 4.

    No necesitas llamar esto directamente — usa save() que lo hace internamente.
    """
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "version": python_version,
            },
        },
        "cells": cells,
    }


def save(
    cells: List[Cell],
    output_path: str,
    *,
    overwrite: bool = True,
) -> str:
    """
    Guarda el notebook en disco.

    Parámetros
    ----------
    cells       : Lista de celdas producidas por md(), code(), sh(), etc.
    output_path : Ruta de salida relativa al repo o absoluta.
    overwrite   : Si True, sobreescribe el archivo si ya existe.

    Retorna la ruta absoluta del archivo generado.
    """
    if not os.path.isabs(output_path):
        # Resolver relativo al directorio del repo (padre de utils/)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(repo_root, output_path)

    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"El archivo ya existe: {output_path}\n"
            "Pasa overwrite=True para sobreescribir."
        )

    nb = build(cells)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[OK] Notebook guardado: {output_path}")
    print(f"     {len(cells)} celdas  |  {size_kb:.1f} KB")
    return output_path


# ─── Utilidad de diagnóstico ──────────────────────────────────────────────────

def validate(cells: List[Cell]) -> None:
    """
    Revisa los problemas más comunes antes de guardar.

    Lanza ValueError con un mensaje detallado si encuentra algún problema.
    """
    errors = []
    for i, cell in enumerate(cells):
        src = "".join(cell.get("source", []))
        cell_type = cell.get("cell_type", "?")

        # Detectar triple-comillas dobles en celdas de código
        if cell_type == "code" and '"""' in src:
            preview = src[:60].replace("\n", " ")
            errors.append(
                f"  · Celda {i} (code): contiene triple-comillas dobles. "
                f"Usa ''' para docstrings internos.\n    Preview: {preview!r}"
            )

        # Detectar celdas vacías
        if not src.strip():
            errors.append(f"  · Celda {i} ({cell_type}): está vacía.")

    if errors:
        raise ValueError(
            "Problemas encontrados en las celdas:\n" + "\n".join(errors)
        )
    print(f"[OK] Validacion completada: {len(cells)} celdas sin problemas")


# ─── Demo / smoke test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    print("=== Smoke test de make_notebook.py ===\n")

    cells = [
        *uce_header(
            title="Notebook de Prueba",
            session=99,
            github_path="main/Cuadernos/99_test.ipynb",
            nota_plataforma="Databricks Community Edition",
        ),
        toc(["Sección 1 -- Introducción", "Sección 2 -- Código", "Sección 3 -- Shell"]),
        section_header("1", "Introducción", "📖"),
        md("""
        ## Texto de ejemplo

        Este cuaderno es un **smoke test** del generador.
        Incluye celdas Markdown, código Python y comandos shell.
        """),
        section_header("2", "Código Python", "🐍"),
        code("""
        import sys
        print(f"Python {sys.version}")
        x = [i**2 for i in range(5)]
        print(x)
        """),
        code("""
        # Función con docstring usando comillas simples (correcto dentro de code())
        def cuadrado(n):
            '''Devuelve el cuadrado de n.'''
            return n * n

        print(cuadrado(7))
        """),
        section_header("3", "Shell", "💻"),
        sh("""
        echo "Sistema operativo:"
        uname -a || ver
        """),
        md("## Referencias\n\n- [Documentación nbformat](https://nbformat.readthedocs.io/)"),
    ]

    # Validar antes de guardar
    validate(cells)

    # Guardar en un archivo temporal
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False, mode="w") as f:
        tmp_path = f.name

    out = save(cells, tmp_path)
    print(f"\nArchivo temporal: {out}")

    # Verificar que el JSON es válido
    with open(out, encoding="utf-8") as f:
        nb = json.load(f)
    print(f"Verificación JSON: OK  ({len(nb['cells'])} celdas)")
    os.unlink(tmp_path)
    print("\n=== Smoke test completado ===")
