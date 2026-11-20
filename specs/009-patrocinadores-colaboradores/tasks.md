---
description: "Tareas de implementación de la feature 009-patrocinadores-colaboradores"
---

# Tasks: Patrocinadores y colaboradores

**Tests**: Incluidas (constitución V).

## Phase 1: Foundational

- [X] T001 Crear `backend/app/models/entidades.py` con `Entidad` (data-model.md `Entidad.id`, `Entidad.tipo`, `Entidad.slug`, `Entidad.nombre`, `Entidad.logo`, `Entidad.web`, `Entidad.orden`, `Entidad.publicada`, `Entidad.version`, `Entidad.creado_en`), registrarla, escribir `backend/alembic/versions/0009_entidades.py` y crear `backend/app/schemas/entidades.py` (`EntidadEntrada` con las reglas de esos campos)

## Phase 2: User Story 1 + 2 (P1) 🎯 MVP

- [X] T002 [P] [US1] Escribir `backend/tests/test_entidades.py`: crear, publicar, ordenar, retirar y borrar en cada sección; independencia entre secciones (mismo id en ambas); contrato público y privado; 409; doble envío; validaciones; protección; persistencia; importación de los 8 sin web y sin pisar datos
- [X] T003 [US1] Implementar `backend/app/services/entidades.py` y `backend/app/api/admin_entidades.py`, registrarlo, servir `sponsors` y `collaborators` en `backend/app/services/contenido.py` e importar en `backend/app/services/importacion.py`
- [X] T004 [US1] Añadir `sponsors` y `collaborators` a `frontend/src/lib/persistencia.ts` con su prueba

## Phase 3: Polish

- [X] T005 Crear y ejecutar `frontend/scripts/verificar-entidades.mjs` (quickstart, con `object-fit: contain` de los logos) y la regresión completa
- [X] T006 Ejecutar ruff, pytest, vitest, `typecheck` y `build`, y actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`
