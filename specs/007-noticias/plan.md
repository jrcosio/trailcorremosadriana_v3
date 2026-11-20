# Implementation Plan: Noticias

**Branch**: `007-noticias` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Tabla `noticias` (0007), endpoints de administración por recurso con versión (siguiendo el
patrón de la 004), contrato `news` desde PostgreSQL con orden explícito, importación de las 2
noticias existentes e integración en `persistencia.ts`. Las pantallas no cambian. Detalle en
[research.md](research.md).

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Pantallas de la propuesta sin cambios | ✅ |
| II | Tabla con versión y 409; los borradores son privados | ✅ |
| III | Protección de la 002 | ✅ |
| IV | `/noticias/proxima-edicion` conservada; noticia de producción recuperada con su procedencia | ✅ |
| V | PostgreSQL real y Playwright | ✅ |
| VI | Sin categoría ni fecha inventadas | ✅ |

## Project Structure

```text
backend/alembic/versions/0007_noticias.py · app/models/noticias.py · app/schemas/noticias.py
backend/app/services/{noticias,importacion,contenido}.py · app/api/admin_noticias.py
backend/seed/noticias/2026-07-13-gracias-trail-2026.json · tests/test_noticias.py
frontend/public/reused/noticias/gracias_2026.webp · src/lib/persistencia.ts · scripts/verificar-noticias.mjs
```

## Complexity Tracking

Sin violaciones.
