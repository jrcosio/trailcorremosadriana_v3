# Implementation Plan: Reglamento y contacto

**Branch**: `010-reglamento-contacto` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Migración `0010`: el reglamento pasa a ser un texto de cada edición (`ediciones.reglamento`) y el
contacto, una configuración de fila única (`configuracion`), ambos con versión. Se añaden
`PUT /api/admin/reglamento` y `PUT /api/admin/contacto`. `/api/content` sirve `regulation` y
`settings.email/phone/instagram` desde PostgreSQL. Con esto el panel guarda todo por recursos: se
retira `PUT /api/content` (DISCREPANCIAS M1) y el cliente rechaza localmente cualquier cambio sin
recurso. `/contacto` deriva el usuario de Instagram del enlace, con el mismo texto que hoy.
Detalle en [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript 5.9 + React 19 (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, psycopg 3; Vite
**Storage**: PostgreSQL 17
**Testing**: pytest contra PostgreSQL real (`api-test`), vitest, Playwright
**Target Platform**: Docker Compose (Caddy + API + PostgreSQL)
**Project Type**: aplicación web (frontend + backend)
**Performance Goals**: guardar y mostrar un reglamento de 200 000 caracteres sin pérdida
**Constraints**: sin cambios visuales; `mailto` para el contacto; versión de la edición compartida
con evento e inscripciones
**Scale/Scope**: 1 columna, 1 tabla, 2 endpoints, 1 endpoint retirado

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Mismas pantallas; el usuario de Instagram derivado coincide con el texto actual | ✅ |
| II | Columna y tabla con versión y 409; persistencia tras reinicio; sin documento único | ✅ |
| III | Protección de la 002 en los dos endpoints; se retira un punto de escritura sin uso | ✅ |
| IV | URLs conservadas; importación idempotente que no pisa datos | ✅ |
| V | PostgreSQL real, vitest y Playwright con restauración | ✅ |
| VI | `mailto` sin envío por servidor; sin reglamento ni datos inventados (D4 excluido) | ✅ |

Re-evaluación tras el diseño: sin cambios. ✅

## Project Structure

```text
backend/alembic/versions/0010_reglamento_contacto.py
backend/app/models/{evento,configuracion}.py · app/schemas/{reglamento,contacto}.py
backend/app/services/{reglamento,contacto,importacion,contenido}.py
backend/app/api/{admin_reglamento,admin_contacto,contenido}.py · app/main.py (etiquetas)
backend/tests/{test_reglamento_contacto,test_proteccion}.py
frontend/src/lib/{persistencia,contacto}.ts · src/components/Site.tsx (usuario de Instagram)
frontend/tests/{persistencia,contacto}.test.ts · scripts/{verificar-reglamento-contacto,verificar-acceso}.mjs
```

## Complexity Tracking

Sin violaciones.
