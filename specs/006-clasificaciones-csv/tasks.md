---
description: "Tareas de implementación de la feature 006-clasificaciones-csv"
---

# Tasks: Clasificaciones CSV

**Tests**: Incluidas (constitución V).

## Phase 1: Foundational

- [X] T001 Crear `backend/app/models/clasificaciones.py` con `Clasificacion` (data-model.md `Clasificacion.id`, `Clasificacion.identificador`, `Clasificacion.carrera_edicion_id`, `Clasificacion.titulo`, `Clasificacion.publicada`, `Clasificacion.archivo_origen`, `Clasificacion.importada_en`, `Clasificacion.participantes`, `Clasificacion.version`), `Resultado` (`Resultado.id`, `Resultado.clasificacion_id`, `Resultado.orden`, `Resultado.posicion`, `Resultado.dorsal`, `Resultado.nombre`, `Resultado.tiempo`, `Resultado.categoria`, `Resultado.club`, `Resultado.sexo`, `Resultado.estado`, `Resultado.busqueda`) e `ImportacionCsv` (`ImportacionCsv.token`, `ImportacionCsv.sesion_id`, `ImportacionCsv.carrera_edicion_id`, `ImportacionCsv.archivo_origen`, `ImportacionCsv.filas`, `ImportacionCsv.sha256`, `ImportacionCsv.expira_en`), registrarlos y escribir `backend/alembic/versions/0006_clasificaciones.py` con todas las restricciones de data-model.md
- [X] T002 [P] Portar el lector a `backend/app/services/csv_clasificaciones.py` (`leer_csv`, `adivinar_mapeo`, `mapear`, alias con `meta`) y escribir `backend/tests/test_csv.py`, equivalente a `frontend/tests/clasificaciones.test.tsx`, más Windows-1252, CRLF y BOM, límites y el formato de producción (cabeceras `Pos…Meta…Estado`)
- [X] T003 [P] Añadir el alias `meta` en `frontend/src/lib/classifications.ts` y aceptar `participants` en `visibleClassifications`, con sus pruebas en `frontend/tests/clasificaciones.test.tsx`

## Phase 2: User Story 1 + 2 - Importar y sustituir (P1) 🎯 MVP

- [X] T004 [P] [US1] Escribir `backend/tests/test_clasificaciones.py`: vista previa (errores con fila, solidaria → 400, prueba sin ficha para el año → 400, duplicado prueba y edición → 409); crear con token; token de otra sesión, caducado o reutilizado → 400; sustitución total; fallo → sin cambios; metadatos (título y publicación) sin token; 409 de versión; borrar; borrar una prueba con clasificación → 409; protección
- [X] T005 [US1] Implementar `backend/app/services/clasificaciones.py`, `backend/app/schemas/clasificaciones.py` y `backend/app/api/admin_clasificaciones.py` (vista previa, PUT y DELETE) y registrarlos
- [X] T006 [US2] Adaptar `frontend/src/components/admin/ClassificationImport.tsx` (llamar a la vista previa del servidor al «Usar estos resultados» y guardar `importToken`), `ClassificationManager.tsx` (contador de `participants`) y `frontend/src/lib/persistencia.ts` (los `results` van a sus recursos), con pruebas en `frontend/tests/persistencia.test.ts`; sin cambios visuales

## Phase 3: User Story 3 - Consulta pública (P1)

- [X] T007 [P] [US3] Escribir `backend/tests/test_consulta_clasificaciones.py`: paginación de 50, búsqueda sin tildes ni mayúsculas en dorsal, nombre y club, filtros, orden con los no clasificados al final, columnas opcionales, borrador → 404, contrato público sin filas y con `participants`, privado con filas, `%` y `_` escapados, tiempo < 1 s con 5000 filas
- [X] T008 [US3] Implementar `backend/app/api/clasificaciones.py` y los `results` en `backend/app/services/contenido.py`
- [X] T009 [US3] Adaptar `frontend/src/components/ClassificationTable.tsx` (modo servidor con `classificationId`, mismo marcado), `Results.tsx` (`participants`, año inicial) y `Site.tsx` (`/clasificaciones/{año}`)

## Phase 4: User Story 4 + 5 - Exclusión solidaria e importación de 2026 (P2)

- [X] T010 [US5] Añadir el subcomando `importar-clasificacion` en `backend/app/cli.py` con su prueba en `backend/tests/test_clasificaciones.py` (crea, no sustituye sin `--sustituir`, Windows-1252)
- [X] T011 [US5] Importar en Compose los 3 CSV reales de 2026 como publicados (quickstart) y comprobar los totales 63/205/224

## Phase 5: Polish

- [X] T012 Crear y ejecutar `frontend/scripts/verificar-clasificaciones.mjs` (quickstart), las capturas de `/clasificaciones` y `/clasificaciones/2026` y la regresión completa
- [X] T013 Ejecutar ruff, pytest, vitest, `typecheck` y `build`, y actualizar `docs/arquitectura.md`, `docs/referencia/DISCREPANCIAS.md` (M5, C5, CSV no versionados), `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

---

## Phase 6: Convergence

- [X] T014 Limpiar las importaciones temporales caducadas también al guardar una clasificación y en cada acceso correcto al panel (`backend/app/services/clasificaciones.py`, `backend/app/api/sesion.py`), con prueba en `backend/tests/test_clasificaciones.py` per FR-014, Assumptions (partial)
