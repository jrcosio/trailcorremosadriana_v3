---
description: "Tareas de implementación de la feature 004-evento-carreras"
---

# Tasks: Evento y carreras

**Input**: Design documents from `/specs/004-evento-carreras/`

**Tests**: Incluidas (constitución V).

## Phase 1: Setup

- [X] T001 Crear `backend/app/services/fechas.py` (ISO a UTC, hora local sin zona interpretada en Europe/Madrid con `fold=0`, salida `…Z` con milisegundos) y `backend/tests/test_fechas.py` (verano, invierno, hora inexistente, hora ambigua, vacío, formato no válido)

## Phase 2: Foundational

- [X] T002 Crear `backend/app/models/evento.py` con `Edicion` (data-model.md `Edicion.id`, `Edicion.anio`, `Edicion.fecha_hora`, `Edicion.mostrar_contador`, `Edicion.es_actual`, `Edicion.version`, `Edicion.creado_en`, `Edicion.actualizado_en`), `Carrera` (`Carrera.id`, `Carrera.slug`, `Carrera.nombre`, `Carrera.etiqueta`, `Carrera.color`, `Carrera.orden`) y `CarreraEdicion` (`CarreraEdicion.id`, `CarreraEdicion.carrera_id`, `CarreraEdicion.edicion_id`, `CarreraEdicion.km`, `CarreraEdicion.desnivel`, `CarreraEdicion.precio`, `CarreraEdicion.hora_salida`, `CarreraEdicion.terreno`, `CarreraEdicion.descripcion`, `CarreraEdicion.avituallamientos`, `CarreraEdicion.imagen`, `CarreraEdicion.ruta`, `CarreraEdicion.wikiloc`, `CarreraEdicion.gpx`, `CarreraEdicion.url_inscripcion`, `CarreraEdicion.publicada`, `CarreraEdicion.version`, `CarreraEdicion.actualizado_en`), y registrarlos en `backend/app/models/__init__.py`
- [X] T003 Escribir `backend/alembic/versions/0004_evento_carreras.py` con los CHECK, UNIQUE, índice parcial y FK de data-model.md, con su `downgrade`
- [X] T004 Crear `backend/app/schemas/evento.py` con `EventoEntrada` y `CarreraEntrada`, que aplican las reglas de data-model.md a todos los campos citados en T002 y usan `referencia_valida` (003) en `CarreraEdicion.imagen`, `CarreraEdicion.ruta` y `CarreraEdicion.url_inscripcion`; `CarreraEdicion.gpx` se limita a vacío, `/media/<clave>.gpx` o https

## Phase 3: User Story 3 - Datos iniciales (P1)

- [X] T005 [P] [US3] Escribir `backend/tests/test_importacion.py`: base vacía → ediciones 2026 (11/07/2026 09:00 Madrid, sin contador) y 2027 (actual, sin fecha) y 3 pruebas con fichas de 2026 publicadas en orden; segunda ejecución sin cambios; con datos existentes no toca nada; `--reemplazar` sin confirmación no hace nada
- [X] T006 [US3] Implementar `backend/app/services/importacion.py` y el subcomando `importar-inicial` en `backend/app/cli.py`

## Phase 4: User Story 1 - Configurar la edición y su fecha (P1) 🎯 MVP

- [X] T007 [P] [US1] Escribir `backend/tests/test_evento.py`: GET y PUT con protección de la 002; guarda fecha y contador; cambiar de año convierte otra edición en la actual y conserva la anterior; solo una edición actual; 409 con versión obsoleta; 400 con datos no válidos
- [X] T008 [US1] Implementar `backend/app/services/evento.py` y `backend/app/api/admin_evento.py` y registrarlo en `backend/app/main.py`

## Phase 5: User Story 2 - Gestionar las pruebas (P1)

- [X] T009 [P] [US2] Escribir `backend/tests/test_carreras.py`: crear como borrador o publicada; editar; cambiar la edición conserva la ficha anterior; 409 con versión obsoleta y al crear un id existente; borrar con versión; 404 si no existe; validaciones de FR-006 (cada regla); protección de la 002. El rechazo del borrado con clasificaciones (FR-009) se prueba en la feature 006, cuando exista la tabla
- [X] T010 [US2] Implementar `backend/app/services/carreras.py` y `backend/app/api/admin_carreras.py` y registrarlo en `backend/app/main.py`

## Phase 6: User Story 4 - Web pública desde la base de datos (P2)

- [X] T011 [P] [US4] Escribir `backend/tests/test_contenido_bd.py`: el contrato público toma edición, fecha, contador y pruebas de la base (solo publicadas, la ficha de año más alto entre las publicadas, km y desnivel como texto); la variante privada incluye borradores, `version` y `settings.eventVersion`; base sin inicializar → semilla; los demás campos de `settings` y las colecciones siguen saliendo de la semilla
- [X] T012 [US4] Adaptar `backend/app/services/contenido.py` y `backend/app/api/contenido.py` para montar `SiteData` desde la base

## Phase 7: Panel (US1 + US2)

- [X] T013 [P] [US2] Crear `frontend/src/lib/persistencia.ts` (`guardarCambios`: comparar secciones, reparto por recurso, recarga de la vista privada, primer error) y `frontend/tests/persistencia.test.ts`
- [X] T014 [US2] Cambiar `save()` en `frontend/src/components/admin/Admin.tsx` para usar `guardarCambios` y fijar los datos devueltos por el servidor; sin cambios visuales
- [X] T015 [US2] Crear `frontend/scripts/verificar-evento-carreras.mjs` (Playwright, quickstart §3 con restauración posterior, incluido que el detalle de una prueba retirada muestra «Este sendero no está en el mapa.») y ejecutarlo

## Phase 8: Polish

- [X] T016 Desplegar en Compose (migración e importación), ejecutar `verificar-rutas.mjs`, capturas a 4 anchos con comparación de textos frente a la 001, la regresión de 002/003 y el reinicio (SC-003)
- [X] T017 Ejecutar ruff, la suite completa y `typecheck`/`build`, y actualizar `docs/arquitectura.md`, `docs/desarrollo.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Dependencies

T001 → T002–T004 → US3 (la importación da datos al resto) → US1, US2 → US4 → panel → Polish.

---

## Phase 9: Convergence

- [X] T018 Verificar de extremo a extremo que, al subir un GPX en `/admin/recorridos/trail-27k`, el detalle `/carreras/trail-27k` ofrece la descarga de ese `/media/….gpx` (attachment) y que sin GPX no aparece; restaurar después (`frontend/scripts/verificar-evento-carreras.mjs`) per US4/AC2 (partial)
- [X] T019 Verificar que con una fecha pasada la portada muestra «Nos vemos en la montaña» y el contador a cero sin negativos, y restaurar sin fecha (`frontend/scripts/verificar-evento-carreras.mjs`) per spec «Edge Cases» (partial)
