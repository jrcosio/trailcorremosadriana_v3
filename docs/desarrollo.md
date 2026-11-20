# Desarrollo local

Requisitos: Docker con Compose v2. Para trabajar con el frontend fuera de contenedores: Node
≥ 22.13 y npm. No hacen falta `datos_iniciales/` ni credenciales de producción.

## Arranque (flujo único)

```bash
cp .env.example .env            # opcional: Compose ya trae los mismos valores de desarrollo
docker compose build
docker compose up -d db
docker compose run --rm api alembic upgrade head    # paso explícito de esquema
docker compose run --rm api python -m app.cli importar-inicial   # datos aprobados (solo partes vacías)
docker compose up -d
curl -s localhost:8080/api/ready                     # {"estado":"disponible"}
```

La web queda en <http://localhost:8080>.

### Administrador local

```bash
docker compose run --rm api python -m app.cli crear-admin admin   # pide la contraseña dos veces
```

El panel está en <http://localhost:8080/admin>. Otros comandos de operador: `restablecer-password`,
`desactivar`, `activar`, `revocar-sesiones` y `listar-admins`
(`specs/002-administrador/contracts/cli-operador.md`).

Para desbloquear el acceso en local tras 8 intentos fallidos:
`docker compose exec db psql -U trail -c 'DELETE FROM limites_login'`. PostgreSQL y la API no publican puertos con
`compose.yaml`.

Cada vez que una feature añada migraciones hay que repetir `alembic upgrade head`. Mientras
falten, `/api/ready` responde `migraciones_pendientes`.

## Clasificaciones reales de 2026 (una vez, en local)

Los CSV contienen datos personales y no se versionan. Se importan desde los archivos originales:

```bash
D=datos_iniciales/trailcorremosadriana_v2/datos/2026
docker compose run --rm -T api python -m app.cli importar-clasificacion --carrera trail-27k --edicion 2026 \
  --titulo "Clasificación Trail Peñasagra 2026" --archivo Clasificacion_27km.csv --publicar < $D/Clasificacion_27km.csv
# Igual para speed-14k (Clasificacion_14km.csv) y familiar-7k (Clasificacion_marcha.csv)
```

## Almacenamiento S3 en desarrollo

```bash
docker compose -f compose.yaml -f compose.s3.yaml up -d   # API con ALMACENAMIENTO=s3 contra moto (s3-dev)
docker compose up -d                                       # volver al almacenamiento local
```

Los archivos subidos en un modo no están en el otro: la base guarda la referencia, pero los
bytes se quedan en su almacenamiento. En producción (Cloudflare R2) se configuran las variables
`S3_*` reales en el entorno del servidor, nunca en el repositorio.

## Frontend con recarga en caliente

```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d db api   # API en 127.0.0.1:8000
cd frontend && npm ci && npm run dev                               # http://localhost:5173
```

El servidor de Vite hace proxy de `/api` y `/media` a `127.0.0.1:8000` (variable
`API_DESARROLLO`).

## Pruebas

```bash
# Backend contra PostgreSQL real (bases temporales trail_test_*) y S3 real por HTTP (moto, s3-dev)
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test

# Frontend
cd frontend && npm run typecheck && npm test && npm run build

# Verificaciones en navegador (con el entorno arrancado; requiere `npx playwright install chromium`)
node scripts/verificar-rutas.mjs          # todas las rutas, al abrir y al recargar
node scripts/verificar-admin.mjs          # acceso erróneo genérico; vistas de diseño sin escritura
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-acceso.mjs --bloqueo   # acceso real de extremo a extremo
node scripts/capturas.mjs http://localhost:8080 capturas/local   # 360/768/1024/1440 + desbordamiento
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-subida.mjs   # subida real desde el panel
# Una verificación por feature (cada una restaura los datos al terminar):
#   verificar-evento-carreras, verificar-inscripciones, verificar-clasificaciones,
#   verificar-noticias, verificar-galeria, verificar-entidades, verificar-reglamento-contacto
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-reglamento-contacto.mjs
```

`verificar-respaldo.mjs` se ejecuta con la API detenida (`docker compose stop api`).
`verificar-reglamento-contacto.mjs` reinicia la API y usa `docker compose exec db` para restaurar
el reglamento, así que se lanza desde `frontend/` con Compose en marcha.

## Comandos útiles

| Tarea | Comando |
|---|---|
| Estado de los servicios | `docker compose ps` |
| Registros de la API | `docker compose logs -f api` |
| Revisión de esquema aplicada | `docker compose run --rm api alembic current` |
| Copia de seguridad (base y archivos locales) | `infra/scripts/backup.sh` |
| Restaurar una copia | `infra/scripts/restore.sh <archivo.dump> [media.tgz]` |
| Parar sin borrar datos | `docker compose down` |
| Borrar también los datos (¡destructivo!) | `docker compose down -v` |

## Lint del backend

```bash
cd backend && uvx ruff@0.17.6 check . && uvx ruff@0.17.6 format --check .
```
