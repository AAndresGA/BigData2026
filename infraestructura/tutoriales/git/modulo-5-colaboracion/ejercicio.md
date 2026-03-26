# 🧪 Ejercicio 5: Colaboración entre estudiantes usando forks

## Escenario

El profesor publica un repositorio base con instrucciones y archivos iniciales.

Ana y Luis no deben modificar ese repositorio del profesor. En cambio, deben construir su propia solución como equipo.

## Objetivo

Practicar un flujo real de colaboración donde:

- ambos parten del repositorio del profesor
- ambos hacen fork
- eligen uno de sus forks como repositorio del equipo
- trabajan desde workspaces separados
- colaboran entre ellos mediante ramas y Pull Requests

## Parte 1. Crear la base del equipo

1. Ana hace fork del repositorio del profesor
2. Luis hace fork del repositorio del profesor
3. El equipo decide usar el fork de Ana como repositorio compartido
4. Ana agrega a Luis como colaborador en su repositorio
5. Ambos verifican que pueden trabajar sobre `ana/repositorio`

## Parte 2. Trabajar en ramas separadas

### Ana

1. Crear rama:

```bash
git switch -c feature/estructura
```

2. Hacer un cambio
3. Hacer commit
4. Hacer push

### Luis

1. Crear rama:

```bash
git switch -c feature/contenido
```

2. Hacer un cambio distinto
3. Hacer commit
4. Hacer push

## Parte 3. Revisarse entre ellos

1. Ana abre PR hacia `main` del repositorio del equipo
2. Luis revisa el PR de Ana y deja al menos un comentario
3. Ana corrige y actualiza el mismo PR
4. Luis abre PR hacia `main`
5. Ana revisa el PR de Luis y deja al menos un comentario
6. Luis corrige y actualiza el mismo PR

## Parte 4. Sincronizar con el profesor

Agregar el repositorio del profesor como `upstream`:

```bash
git remote add upstream https://github.com/PROFESOR/REPOSITORIO.git
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

## 🎯 Resultado esperado

- el repositorio del profesor no recibe cambios de los estudiantes
- la solución del equipo vive en el fork elegido por Ana y Luis
- ambos trabajan desde workspaces diferentes
- ambos usan ramas separadas
- ambos practican revisión mediante Pull Requests

## Qué se evalúa

- si entendiste la diferencia entre repositorio base del profesor y repositorio del equipo
- si el equipo definió correctamente un fork compartido para trabajar
- si cada integrante trabajó en una rama propia
- si hubo revisión cruzada entre ambos
- si saben explicar para qué sirven `origin` y `upstream`
