---
description: "Tareas de implementación de la feature 007-noticias"
---

# Tasks: Noticias

**Tests**: Incluidas (constitución V).

## Phase 1: Foundational

- [ ] T001 Crear `backend/app/models/noticias.py` con `Noticia` (data-model.md `Noticia.id`, `Noticia.slug`, `Noticia.titulo`, `Noticia.categoria`, `Noticia.fecha`, `Noticia.imagen`, `Noticia.extracto`, `Noticia.cuerpo`, `Noticia.publicada`, `Noticia.version`, `Noticia.creado_en`, `Noticia.actualizado_en`), registrarla y escribir `backend/alembic/versions/0007_noticias.py` con sus restricciones
- [ ] T002 Crear `backend/app/schemas/noticias.py` (`NoticiaEntrada`, con las reglas de data-model.md de los campos de T001 y la regla de referencias para `Noticia.imagen`)

## Phase 2: User Story 1 - Redactar y publicar (P1) 🎯 MVP

- [ ] T003 [P] [US1] Escribir `backend/tests/test_noticias.py`: crear borrador, publicar, retirar, borrar; contrato público solo con publicadas y en el orden de FR-003; privado con versión; 409; doble envío sin duplicar; validaciones (título, cuerpo, fecha, imagen y longitudes); protección; persistencia en otra instancia
- [ ] T004 [US1] Implementar `backend/app/services/noticias.py` y `backend/app/api/admin_noticias.py`, registrarlo y servir `news` en `backend/app/services/contenido.py`
- [ ] T005 [US1] Añadir la sección `news` a `frontend/src/lib/persistencia.ts` con su prueba en `frontend/tests/persistencia.test.ts`

## Phase 3: User Story 2 - Noticias existentes (P1)

- [ ] T006 [US2] Copiar la imagen de producción a `frontend/public/reused/noticias/gracias_2026.webp`, guardar el contenido en `backend/seed/noticias/2026-07-13-gracias-trail-2026.json`, importar ambas noticias en `backend/app/services/importacion.py` (solo si no hay noticias) con su prueba, y documentar la procedencia en `docs/PROCEDENCIA_RECURSOS.md`

## Phase 4: Polish

- [ ] T007 Crear y ejecutar `frontend/scripts/verificar-noticias.mjs` (quickstart), las capturas de `/`, `/noticias` y del detalle a 4 anchos, y la regresión completa
- [ ] T008 Ejecutar ruff, pytest, vitest, `typecheck` y `build`, y actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`
