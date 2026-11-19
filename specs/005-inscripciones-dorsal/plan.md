# Implementation Plan: Inscripciones y Dorsal Solidario

**Branch**: `005-inscripciones-dorsal` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Se añaden apertura, mensaje y URL del Dorsal Solidario a la edición (migración 0005), con
`GET` y `PUT` en `/api/admin/inscripciones`. La regla «no abrir sin destino» se comprueba en el
servidor. Los destinos externos se validan en el servidor (solo HTTPS, sin credenciales), también
los enlaces por prueba. `/api/content` sirve estos campos desde PostgreSQL y el panel los reparte
con `persistencia.ts`. Las pantallas no cambian: el componente `DorsalSolidario` de la propuesta
ya implementa la matriz con estos datos. Detalle en [research.md](research.md).

## Technical Context

Python 3.13 / TypeScript 5.9 sin dependencias nuevas · PostgreSQL (0005) · pytest con
PostgreSQL real, vitest y Playwright.

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Sin cambios visuales; la matriz usa el componente aprobado | ✅ |
| II | Columnas en `ediciones` con versión y 409 | ✅ |
| III | Protección de la 002; validación de destinos en el servidor | ✅ |
| IV | El contrato `settings` no cambia; la importación no pisa datos editados | ✅ |
| V | Matriz verificada en navegador y pytest con PostgreSQL | ✅ |
| VI | Sin enlaces inventados; pagos fuera de la web | ✅ |

## Project Structure

```text
backend/alembic/versions/0005_inscripciones.py · app/models/evento.py (columnas)
backend/app/core/referencias.py (url_externa_segura) · app/schemas/evento.py (InscripcionesEntrada, registration)
backend/app/services/{inscripciones,importacion,contenido}.py · app/api/admin_inscripciones.py
backend/tests/{test_inscripciones,test_referencias}.py
frontend/src/lib/persistencia.ts · tests/persistencia.test.ts · scripts/verificar-inscripciones.mjs
```

## Complexity Tracking

Sin violaciones.
