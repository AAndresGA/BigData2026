# Setup Windows (resumen rapido)

Este archivo es un resumen. La guia principal esta en `INSTALACION_DESDE_CERO.md`.

## Pasos minimos

1. Instalar WSL2:

```powershell
wsl --install
```

2. Instalar Docker Desktop y abrirlo.
3. Verificar:

```powershell
docker --version
docker compose version
```

4. En la carpeta del proyecto:

```powershell
Copy-Item .env.example .env
docker compose --profile airflow --profile dask up -d
docker compose ps
```

## Referencia completa

- `INSTALACION_DESDE_CERO.md`
- `setup/docker.md`
