# Desarrollo local

Requisitos: Docker con Compose v2. Para trabajar con el frontend fuera de contenedores: Node
≥ 22.13 y npm. No hacen falta `datos_iniciales/` ni credenciales de producción.

## Arranque (flujo único)

```bash
cp .env.example .env            # opcional: Compose ya trae los mismos valores de desarrollo
docker compose build
docker compose up -d db
docker compose run --rm api alembic upgrade head    # paso explícito de esquema
docker compose up -d
curl -s localhost:8080/api/ready                     # {"estado":"disponible"}
```

La web queda en <http://localhost:8080>. PostgreSQL y la API no publican puertos con
`compose.yaml`.

Cada vez que una feature añada migraciones hay que repetir `alembic upgrade head`. Mientras
falten, `/api/ready` responde `migraciones_pendientes`.

## Frontend con recarga en caliente

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d db api   # API en 127.0.0.1:8000
cd frontend && npm ci && npm run dev                               # http://localhost:5173
```

El servidor de Vite hace proxy de `/api` y `/media` a `127.0.0.1:8000` (variable
`API_DESARROLLO`).

## Pruebas

```bash
# Backend contra PostgreSQL real (crea y borra bases temporales trail_test_*)
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test

# Frontend
cd frontend && npm run typecheck && npm test && npm run build

# Verificaciones en navegador (con el entorno arrancado; requiere `npx playwright install chromium`)
node scripts/verificar-rutas.mjs          # todas las rutas, al abrir y al recargar
node scripts/verificar-admin.mjs          # /admin sin acceso; vistas de diseño sin escritura
node scripts/capturas.mjs http://localhost:8080 capturas/local   # 360/768/1024/1440 + desbordamiento
```

`verificar-respaldo.mjs` se ejecuta con la API detenida (`docker compose stop api`).

## Comandos útiles

| Tarea | Comando |
|---|---|
| Estado de los servicios | `docker compose ps` |
| Registros de la API | `docker compose logs -f api` |
| Revisión de esquema aplicada | `docker compose run --rm api alembic current` |
| Copia de seguridad de la base | `infra/scripts/backup.sh` |
| Restaurar una copia | `infra/scripts/restore.sh <archivo.dump>` |
| Parar sin borrar datos | `docker compose down` |
| Borrar también los datos (¡destructivo!) | `docker compose down -v` |

## Lint del backend

```bash
cd backend && uvx ruff@0.17.6 check . && uvx ruff@0.17.6 format --check .
```
