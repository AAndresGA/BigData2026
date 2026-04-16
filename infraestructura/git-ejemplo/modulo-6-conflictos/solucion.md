# ✅ Solución sugerida

## Ejemplo de conflicto

```text
<<<<<<< HEAD
Hola, me llamo Ana y soy estudiante de Git.
=======
Hola, me llamo Luis y estoy practicando conflictos.
>>>>>>> feature/luis
```

## Resolución posible

El archivo final puede quedar así:

```text
Hola, somos Ana y Luis y estamos practicando conflictos en Git.
```

## Comandos de cierre

```bash
git add nombre-del-archivo
git commit -m "Resuelve conflicto en nombre-del-archivo"
```

## Explicación

- primero se analizan ambas versiones
- luego se decide cuál contenido final debe permanecer
- se eliminan las marcas del conflicto
- `git add` marca el archivo como resuelto
- el commit deja constancia de la resolución
