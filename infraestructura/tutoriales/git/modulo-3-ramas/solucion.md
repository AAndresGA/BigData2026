# ✅ Solución sugerida

## Flujo esperado

```bash
git switch -c feature/perfil
git status
git add .
git commit -m "Agrega archivo de perfil"
git push origin feature/perfil
```

## Ejemplo de contenido para `perfil.txt`

```text
Nombre: Ana
Rol: Desarrolladora
Descripcion: Estudiante del curso de Git
```

## Explicación

- `git switch -c feature/perfil` crea y activa una rama nueva
- el archivo `perfil.txt` representa el cambio de esta tarea
- el commit deja registrado el trabajo dentro de la rama
- `git push origin feature/perfil` publica la rama en GitHub sin tocar `main`
