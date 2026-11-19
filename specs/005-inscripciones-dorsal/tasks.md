---
description: "Tareas de implementación de la feature 005-inscripciones-dorsal"
---

# Tasks: Inscripciones y Dorsal Solidario

**Tests**: Incluidas (constitución V).

## Phase 1: Foundational

- [X] T001 Añadir a `Edicion` en `backend/app/models/evento.py` los campos de data-model.md `Edicion.inscripciones_abiertas`, `Edicion.mensaje_inscripciones` y `Edicion.url_dorsal_solidario`, y escribir `backend/alembic/versions/0005_inscripciones.py` (con el CHECK de longitud de `Edicion.mensaje_inscripciones`)
- [X] T002 Implementar `url_externa_segura` en `backend/app/core/referencias.py` y ampliar `backend/tests/test_referencias.py` (https con host; rechazar http, `javascript:`, credenciales, sin host, espacios y más de 2200 caracteres)
- [X] T003 Aplicar `url_externa_segura` a `CarreraEdicion.url_inscripcion` (campo `registration` de `CarreraEntrada`) y crear `InscripcionesEntrada` en `backend/app/schemas/evento.py` (data-model.md `Edicion.mensaje_inscripciones`, 1–2000; `Edicion.url_dorsal_solidario`)

## Phase 2: User Story 1 - Abrir y cerrar (P1) 🎯 MVP

- [X] T004 [P] [US1] Escribir `backend/tests/test_inscripciones.py`: GET y PUT; abrir sin destinos → 400; abrir solo con el dorsal; abrir con una prueba publicada con enlace; una prueba no publicada o retirada no cuenta; cerrar conserva los enlaces; enlaces peligrosos → 400; mensaje vacío o largo → 400; 409; protección; contrato público y privado; persistencia en otra instancia; una edición nueva empieza cerrada
- [X] T005 [US1] Implementar `backend/app/services/inscripciones.py` y `backend/app/api/admin_inscripciones.py`, registrarlo en `backend/app/main.py` y servir los campos en `backend/app/services/contenido.py`
- [X] T006 [US1] Completar los campos de inscripción en `backend/app/services/importacion.py` (solo si siguen en sus valores por defecto) con su prueba en `backend/tests/test_importacion.py`

## Phase 3: User Story 2 + 3 - Matriz y tarjetas (P1/P2)

- [X] T007 [US2] Añadir las inscripciones a `frontend/src/lib/persistencia.ts` (orden: pruebas → evento → inscripciones → resto) y ampliar `frontend/tests/persistencia.test.ts`
- [X] T008 [US2] Crear y ejecutar `frontend/scripts/verificar-inscripciones.mjs`: matriz 4 × 3 páginas (botón, `href` exacto, `target="_blank"`, mensajes, sin `/contacto` en el bloque del dorsal); tarjetas de `/inscripciones` con «Inscribirme» o «Inscripción pendiente…»; guardado desde `/admin/inscripciones`, incluido el rechazo de apertura sin destinos; restauración final

## Phase 4: Polish

- [X] T009 Desplegar en Compose (0005 e importación), reiniciar (SC-005), ejecutar la regresión (`verificar-rutas`, `verificar-evento-carreras`, `verificar-acceso`), ruff, la suite completa, `typecheck` y `build`, y actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

---

## Phase 5: Convergence

- [X] T010 Añadir a `backend/tests/test_inscripciones.py` la prueba de que una URL con espacios alrededor se acepta y se guarda recortada (dorsal y enlace de prueba) per spec «Edge Cases» (partial)
