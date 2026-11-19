# Implementation Plan: Archivos

**Branch**: `003-archivos` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-archivos/spec.md`

## Summary

La subida autenticada de JPEG, PNG, WebP, PDF y GPX (`POST /api/upload`) sustituye al 501 de la
feature 002. El tipo se detecta por su contenido, el GPX se analiza de forma segura con
`defusedxml` y el límite es de 10 MB. Las claves son aleatorias (`uuid4().hex` más la extensión)
y la tabla `archivos` guarda los metadatos.

El almacenamiento se elige por configuración: local, en el volumen `media`, o S3/R2 con `boto3`.
Se prueba con el servidor S3 de moto. Los archivos se entregan públicamente en `/media/{clave}`
con caché inmutable, ETag/304, CSP `sandbox` y `nosniff`. Se añade la regla común de referencias
y se amplían las copias de seguridad para incluir los archivos. Las decisiones están en
[research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13 · TypeScript 5.9

**Primary Dependencies**: se añaden `boto3` 1.44, `python-multipart` 0.0.34 y `defusedxml` 0.7.1.
En desarrollo, el servicio `motoserver/moto:5.2.5`.

**Storage**: PostgreSQL (`archivos`, migración `0003_archivos`) y almacenamiento de objetos local
o S3/R2

**Testing**: pytest contra PostgreSQL real; adaptador S3 contra el servidor moto por HTTP;
Playwright para la subida desde el panel

**Target Platform / Project Type**: igual que en las features 001 y 002

**Performance Goals**: subida de 10 MB en menos de 10 s en local (SC-004)

**Constraints**: credenciales solo en el servidor; sin borrado físico; mismo origen

**Scale/Scope**: cientos o pocos miles de archivos de como máximo 10 MB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento | Estado |
|---|---|---|
| I. Preservación visual | Sin cambios visuales; el panel usa su control de subida existente | ✅ |
| II. Persistencia real | Metadatos en PostgreSQL, bytes en un volumen o en R2; persisten tras reiniciar | ✅ |
| III. Seguridad del administrador | Subida tras Origin → sesión → CSRF; credenciales S3 solo en el servidor | ✅ |
| IV. Compatibilidad de datos y URLs | Se mantiene el contrato `POST /api/upload` → `{url:'/media/…'}` y `/media/:key`; los recursos `/reused/` no cambian | ✅ |
| V. Funcionalidades verificables | PostgreSQL real, S3 real por HTTP (moto) y Playwright | ✅ |
| VI. Alcance controlado | No se importan los `/media` de prueba (D2/D3); sin borrado ni CDN en esta feature | ✅ |

Re-evaluación tras el diseño: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/003-archivos/{plan,research,data-model,quickstart}.md · contracts/api-archivos.openapi.yaml · checklists/{requirements,seguridad}.md · tasks.md
```

### Source Code

```text
backend/
├── pyproject.toml / uv.lock                     # + boto3, python-multipart, defusedxml
├── Dockerfile                                   # /data/media con propietario app
├── alembic/versions/0003_archivos.py
├── app/core/config.py                           # ALMACENAMIENTO, MEDIA_DIR, UPLOAD_MAX_BYTES, S3_*
├── app/core/referencias.py                      # referencia_valida()
├── app/models/archivos.py                       # Archivo
├── app/storage/{__init__,local,s3}.py           # Almacenamiento + adaptadores + fábrica
├── app/services/archivos.py                     # detectar_tipo, validar_gpx, guardar_subida, obtener
├── app/api/archivos.py                          # POST /api/upload (real)
├── app/api/media.py                             # GET /media/{clave}
└── tests/{test_tipos,test_subida,test_media,test_almacenamiento_s3,test_referencias}.py

compose.yaml (volumen media, variables) · compose.dev.yaml (s3-dev moto; api-test con S3_TEST_*)
infra/caddy/Caddyfile (request_body 11MB en /api/upload) · infra/scripts/{backup,restore}.sh (media)
frontend/scripts/verificar-subida.mjs
```

**Structure Decision**: se añade `app/storage/`, tal como prevé la DOC 14.

## Complexity Tracking

Sin violaciones.
