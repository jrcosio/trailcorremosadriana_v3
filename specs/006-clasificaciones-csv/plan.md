# Implementation Plan: Clasificaciones CSV

**Branch**: `006-clasificaciones-csv` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Tablas `clasificaciones`, `resultados` e `importaciones_csv` (0006). El servidor incorpora un
lector CSV equivalente al de la propuesta y valida de forma autoritativa con una importación
temporal ligada a la sesión. La confirmación sustituye las filas en una transacción. Hay consulta
pública paginada con búsqueda sin tildes, un comando de operador para importar los CSV de 2026 y
la ruta `/clasificaciones/{año}`. El panel mantiene su experiencia (lectura en el cliente y
validación definitiva en el servidor). Detalle en [research.md](research.md).

## Technical Context

Python 3.13 / TS 5.9 sin dependencias nuevas · PostgreSQL (JSONB, índice por expresión) · pytest
con PostgreSQL real, vitest y Playwright.

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Mismo marcado en `Results`, `ClassificationTable` y en el panel; capturas comparadas | ✅ |
| II | Tablas relacionadas, transacción, versión y 409 | ✅ |
| III | Protección de la 002; importación ligada a la sesión | ✅ |
| IV | `/clasificaciones/{año}` conservada; el contrato `results` mantiene su forma (las filas se piden aparte) | ✅ |
| V | PostgreSQL real; extremo a extremo con los CSV reales | ✅ |
| VI | No se inventan participantes; los CSV reales no se versionan; la plantilla no se importa | ✅ |

## Project Structure

```text
backend/alembic/versions/0006_clasificaciones.py · app/models/clasificaciones.py
backend/app/services/{csv_clasificaciones,clasificaciones}.py · app/schemas/clasificaciones.py
backend/app/api/{admin_clasificaciones,clasificaciones}.py · app/cli.py (importar-clasificacion)
backend/tests/{test_csv,test_clasificaciones,test_consulta_clasificaciones}.py
frontend/src/lib/{classifications.ts (alias meta; participants), persistencia.ts (results)}
frontend/src/components/{Results,ClassificationTable,Site}.tsx · admin/{ClassificationImport,ClassificationManager}.tsx
frontend/tests/clasificaciones.test.tsx · scripts/verificar-clasificaciones.mjs
```

## Complexity Tracking

| Desviación | Motivo | Alternativa más simple descartada |
|---|---|---|
| Lector CSV duplicado (TS en el cliente y Python en el servidor) | Experiencia aprobada inmediata en el panel y validación autoritativa obligatoria en el servidor (DOC 14) | Solo cliente: incumple FR-005. Solo servidor: cambia la experiencia y añade latencia en cada cambio de mapeo |
