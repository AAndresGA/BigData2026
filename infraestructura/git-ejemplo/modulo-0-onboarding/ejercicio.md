# 🧪 Ejercicio 0: Validar entorno de trabajo

## Objetivo

Comprobar que tu entorno está listo para iniciar el curso sin errores de configuración.

## Pasos

1. Verificar nombre en Git:

```bash
git config --global --get user.name
```

2. Verificar correo en Git:

```bash
git config --global --get user.email
```

3. **[IMPORTANTE] Conectar a GitHub con SSH:**

Para hacer push exitoso, necesitas una clave SSH configurada.

```bash
# Generar clave SSH
ssh-keygen -t rsa -b 4096 -C "tu-correo@ejemplo.com"
```

Presiona `Enter` tres veces cuando te lo pida.

```bash
# Ver tu clave pública
cat ~/.ssh/id_rsa.pub
```

Copia TODA esa salida y agrégala en: https://github.com/settings/keys

4. Revisar estado del repositorio:

```bash
git status
```

5. Confirmar rama actual:

```bash
git branch --show-current
```

6. Crear archivo `entorno-listo.txt` con tu nombre y fecha.
7. Crear una rama para este ejercicio:

```bash
git switch -c feature/onboarding
```

8. Hacer commit y push:

```bash
git add .
git commit -m "Valida entorno inicial del curso"
git push origin feature/onboarding
```

## Qué se evalúa

- entorno configurado correctamente
- conexión SSH a GitHub funcionando
- uso de rama de trabajo
- commit claro
- push exitoso
