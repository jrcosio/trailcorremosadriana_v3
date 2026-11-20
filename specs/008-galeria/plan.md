# Implementation Plan: Galería

**Branch**: `008-galeria` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Tablas `albumes` y `fotografias` (0008), endpoints por recurso con versión, contrato `albums`
desde PostgreSQL con `photoAlts`, importación de los álbumes históricos y mejora del foco del visor
sin cambios visuales. Detalle en [research.md](research.md).

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Sin cambios visuales; solo comportamiento de foco y textos alternativos | ✅ |
| II | Tablas con versión y 409; los borradores son privados | ✅ |
| III | Protección de la 002 | ✅ |
| IV | Enlaces históricos y `/galeria/edicion-2026` conservados | ✅ |
| V | PostgreSQL real y Playwright (teclado y foco) | ✅ |
| VI | No se finge la importación de fotos externas | ✅ |

## Project Structure

```text
backend/alembic/versions/0008_galeria.py · app/models/galeria.py · app/schemas/galeria.py
backend/app/services/{galeria,importacion,contenido}.py · app/api/admin_albumes.py · tests/test_galeria.py
frontend/src/components/Site.tsx (foco del visor, alt) · src/lib/persistencia.ts · scripts/verificar-galeria.mjs
```

## Complexity Tracking

Sin violaciones.
