# Quickstart / validación: Archivos (003)

Prerrequisitos: features 001 y 002 en marcha, administrador local creado. Contrato:
[`contracts/api-archivos.openapi.yaml`](contracts/api-archivos.openapi.yaml). Modelo:
[`data-model.md`](data-model.md).

## 1. Migración

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head   # 0003_archivos
docker compose up -d
```

## 2. Subida y entrega (curl, con sesión)

```bash
O='-H Origin:http://localhost:8080'
curl -s -c c.txt $O -H 'content-type: application/json' -d '{"username":"admin","password":"…"}' localhost:8080/api/login
T=$(awk '$6=="penasagra_csrf"{print $7}' c.txt)
curl -s -b c.txt $O -H "X-CSRF-Token: $T" -F file=@frontend/public/reused/img/trail_inscripciones.webp localhost:8080/api/upload
# → {"url":"/media/<32 hex>.webp"}
curl -sI localhost:8080/media/<clave>.webp   # 200 image/webp, immutable, ETag, CSP sandbox, nosniff
curl -s -o /dev/null -w '%{http_code}\n' -H 'If-None-Match: "<sha256>"' localhost:8080/media/<clave>.webp   # 304
```

Rechazos esperados:

| Caso | Respuesta |
|---|---|
| SVG | 400 |
| HTML renombrado a `.jpg` | 400 |
| GPX con `<!DOCTYPE` o entidades | 400 |
| 11 MB | 413 |
| Sin CSRF | 403 |
| Sin sesión | 401 |

## 3. Persistencia

`docker compose restart` y volver a pedir la misma `/media/…` → 200 con los mismos bytes
(misma huella).

## 4. Almacenamiento S3 (moto)

```bash
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test   # incluye las pruebas S3 contra s3-dev
```

## 5. Panel

En `/admin/noticias/nuevo`, «Subir imagen» → aparece la vista previa servida desde `/media/…`.
Guardar la noticia sigue respondiendo «Esta sección del panel todavía no guarda cambios.» hasta
la feature 007.

## 6. Copia de seguridad

`infra/scripts/backup.sh` → crea `copias/trail-<marca>.dump` y `copias/media-<marca>.tgz`, este
último con los archivos subidos.
