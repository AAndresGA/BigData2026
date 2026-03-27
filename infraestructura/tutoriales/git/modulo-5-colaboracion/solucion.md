# ✅ Solución sugerida

## Escenario resuelto

- el profesor publica el repositorio base
- Ana hace fork
- Luis hace fork
- el equipo decide usar el fork de Ana como repositorio del grupo
- Ana agrega a Luis como colaborador
- ambos trabajan en ramas separadas dentro del repositorio del equipo

## Flujo de Ana

```bash
git switch -c feature/estructura
git status
git add .
git commit -m "Agrega estructura inicial de la solucion"
git push origin feature/estructura
```

## Flujo de Luis

```bash
git switch -c feature/contenido
git status
git add .
git commit -m "Agrega contenido complementario a la solucion"
git push origin feature/contenido
```

## Pull Requests entre ellos

1. Ana abre PR hacia `main` del repositorio del equipo
2. Luis revisa y deja comentarios
3. Ana corrige y vuelve a hacer `push` en la misma rama
4. Luis abre su PR hacia `main`
5. Ana revisa y deja comentarios
6. Luis corrige y actualiza su PR

## Sincronización con el profesor

```bash
git remote add upstream https://github.com/PROFESOR/REPOSITORIO.git
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

## Explicación

- el repo del profesor no recibe cambios de los estudiantes
- la solución final vive en el repositorio del equipo
- cada estudiante trabaja en su propio workspace
- la colaboración ocurre mediante ramas, PR y revisión cruzada
