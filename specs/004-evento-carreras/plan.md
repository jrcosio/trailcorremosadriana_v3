# Implementation Plan: Evento y carreras

**Branch**: `004-evento-carreras` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-evento-carreras/spec.md`

## Summary

Se añaden las tablas `ediciones`, `carreras` y `carreras_edicion` (migración 0004) con versiones
y la fecha en Europe/Madrid. Un comando idempotente importa los datos aprobados.

Endpoints nuevos de administración:

- `GET` y `PUT` en `/api/admin/evento`.
- `PUT` y `DELETE` en `/api/admin/carreras/{id}`.

El adaptador `/api/content` pasa a leer de PostgreSQL la edición, la fecha, el contador y las
pruebas. En el panel, `Admin.tsx` delega su `save()` en `lib/persistencia.ts`, que reparte los
cambios por recurso. Las pantallas no cambian. Las decisiones están en [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13 · TypeScript 5.9 (sin dependencias nuevas; `zoneinfo` es de la
biblioteca estándar)

**Storage**: PostgreSQL (migración 0004)

**Testing**: pytest contra PostgreSQL real · vitest (`persistencia.ts`) · Playwright
(`verificar-evento-carreras.mjs`, `verificar-rutas.mjs`, `capturas.mjs`)

**Constraints**: la forma del contrato `SiteData` no cambia; mismo aspecto; Europe/Madrid; 409
ante conflictos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento | Estado |
|---|---|---|
| I. Preservación visual | No cambian las pantallas. `Admin.tsx` solo sustituye el destino de `save()`. Se comparan capturas con la 001 | ✅ |
| II. Persistencia real | Tablas relacionadas con versión y 409. La semilla solo se usa en una base sin inicializar (transitorio documentado) | ✅ |
| III. Seguridad | Escrituras con la protección de la 002 | ✅ |
| IV. Compatibilidad | Mismas URLs (`/carreras/trail-27k`, `/recorridos`) y mismo contrato. Importación idempotente sin sobrescribir | ✅ |
| V. Verificable | PostgreSQL real, Playwright extremo a extremo y reinicio | ✅ |
| VI. Alcance | Sin fecha inventada para 2027. La 2026 procede de producción | ✅ |

## Project Structure

```text
backend/
├── alembic/versions/0004_evento_carreras.py
├── app/models/evento.py                         # Edicion, Carrera, CarreraEdicion
├── app/schemas/evento.py                        # EventoEntrada, CarreraEntrada (validación de FR-006)
├── app/services/{fechas,evento,carreras,importacion}.py
├── app/services/contenido.py                    # adaptador: settings y races desde la BD
├── app/api/{admin_evento,admin_carreras}.py
├── app/cli.py                                   # + importar-inicial
└── tests/{test_fechas,test_evento,test_carreras,test_importacion,test_contenido_bd}.py
frontend/
├── src/lib/persistencia.ts · tests/persistencia.test.ts
├── src/components/admin/Admin.tsx               # save() → guardarCambios(); recarga tras guardar
└── scripts/verificar-evento-carreras.mjs
```

## Complexity Tracking

Sin violaciones.
