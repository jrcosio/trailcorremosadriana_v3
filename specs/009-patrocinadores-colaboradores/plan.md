# Implementation Plan: Patrocinadores y colaboradores

**Branch**: `009-patrocinadores-colaboradores` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Tabla `entidades` (0009) con tipo, endpoints por sección y recurso con versión, contrato
`sponsors` y `collaborators` desde PostgreSQL e importación de los 8 patrocinadores. Sin cambios
visuales. Detalle en [research.md](research.md).

## Constitution Check

I ✅ (sin cambios visuales; logos grandes) · II ✅ (tabla con versión) · III ✅ (protección de la
002) · IV ✅ (logos reutilizados con procedencia) · V ✅ (PostgreSQL y Playwright) · VI ✅ (sin
webs ni colaboradores inventados).

## Project Structure

```text
backend/alembic/versions/0009_entidades.py · app/models/entidades.py · app/schemas/entidades.py
backend/app/services/{entidades,importacion,contenido}.py · app/api/admin_entidades.py · tests/test_entidades.py
frontend/src/lib/persistencia.ts · scripts/verificar-entidades.mjs
```

## Complexity Tracking

Sin violaciones.
