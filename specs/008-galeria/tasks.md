---
description: "Tareas de implementación de la feature 008-galeria"
---

# Tasks: Galería

**Tests**: Incluidas (constitución V).

## Phase 1: Foundational

- [X] T001 Crear `backend/app/models/galeria.py` con `Album` (data-model.md `Album.id`, `Album.slug`, `Album.titulo`, `Album.anio`, `Album.portada`, `Album.url_externa`, `Album.publicado`, `Album.orden`, `Album.version`) y `Fotografia` (`Fotografia.id`, `Fotografia.album_id`, `Fotografia.imagen`, `Fotografia.alt`, `Fotografia.orden`), registrarlos y escribir `backend/alembic/versions/0008_galeria.py`
- [X] T002 Crear `backend/app/schemas/galeria.py` (`AlbumEntrada`, con las reglas de data-model.md de los campos de T001 y un máximo de 500 fotos)

## Phase 2: User Story 1 + 2 - Álbumes, fotos e históricos (P1) 🎯 MVP

- [X] T003 [P] [US1] Escribir `backend/tests/test_galeria.py`: crear borrador con fotos, publicar, quitar una foto (los archivos no se borran), retirar, borrar; orden público; `photoAlts` por defecto; 409; doble envío; validaciones; protección; persistencia; importación de los 3 históricos sin pisar datos
- [X] T004 [US1] Implementar `backend/app/services/galeria.py` y `backend/app/api/admin_albumes.py`, registrarlo, servir `albums` en `backend/app/services/contenido.py` e importar los históricos en `backend/app/services/importacion.py`
- [X] T005 [US1] Añadir la sección `albums` a `frontend/src/lib/persistencia.ts` con su prueba

## Phase 3: User Story 3 - Visor accesible (P2)

- [X] T006 [US3] En `frontend/src/components/Site.tsx`: atrapar el foco en el visor, devolverlo a la miniatura al cerrar y usar `photoAlts`; sin cambios visuales

## Phase 4: Polish

- [X] T007 Crear y ejecutar `frontend/scripts/verificar-galeria.mjs` (quickstart), comprobar el desbordamiento de `/galeria` y del detalle a 4 anchos y la regresión completa
- [X] T008 Ejecutar ruff, pytest, vitest, `typecheck` y `build`, y actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`
