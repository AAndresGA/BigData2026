# Git setup para estudiantes

## Configuracion inicial

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

## Flujo recomendado por tarea

```bash
git switch -c feature/nombre-tarea
git add .
git commit -m "Describe tu cambio"
git push origin feature/nombre-tarea
```

## Si trabajas con fork del profesor

```bash
git remote add upstream <repo-profesor>
git fetch upstream
git switch main
git merge upstream/main
```
