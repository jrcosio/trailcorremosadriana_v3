---
description: "Tareas de implementación de la feature 010-reglamento-contacto"
---

# Tasks: Reglamento y contacto

**Input**: documentos de diseño de `specs/010-reglamento-contacto/`

**Tests**: incluidos (constitución V). pytest contra PostgreSQL real, vitest y Playwright.

## Phase 1: Foundational (bloquea todas las historias)

- [ ] T001 Añadir `Edicion.reglamento` en `backend/app/models/evento.py` y crear `Configuracion` en `backend/app/models/configuracion.py`. Campos y restricciones de data-model.md: `Edicion.reglamento`, `Configuracion.id`, `Configuracion.correo`, `Configuracion.telefono`, `Configuracion.instagram`, `Configuracion.version` y `Configuracion.actualizado_en`. Registrar `Configuracion` en `backend/app/models/__init__.py`
- [ ] T002 Escribir `backend/alembic/versions/0010_reglamento_contacto.py` (columna, CHECK y tabla de T001; `downgrade` reversible)

## Phase 2: User Story 1 — Mantener el reglamento (P1) 🎯 MVP

**Goal**: el reglamento de la edición actual se edita, se conserva íntegro y se muestra con respaldo a la edición más reciente que tenga texto.

**Independent Test**: guardar un texto, leer `/api/content` y reiniciar; cambiar a una edición sin reglamento y comprobar el respaldo.

- [ ] T003 [US1] Escribir las pruebas de reglamento en `backend/tests/test_reglamento_contacto.py`:
  - semilla importada en 2026 sin «PRUEBA»;
  - respaldo a la edición más reciente;
  - guardado en la edición actual sin tocar 2026;
  - 200 000 caracteres íntegros; 200 001 rechazados;
  - CRLF normalizado; vacío rechazado con «reglamento»;
  - versión compartida con evento e inscripciones (409 cruzado);
  - 404 sin edición actual; 401 sin sesión;
  - persistencia con un cliente nuevo.
- [ ] T004 [US1] Crear `backend/app/schemas/reglamento.py` con `ReglamentoEntrada`, que valida y normaliza según data-model.md `Edicion.reglamento` y research R3
- [ ] T005 [US1] Implementar `backend/app/services/reglamento.py` (`mostrado(db)` según research R2 y `guardar(db, entrada)` con la versión de la edición actual) y `backend/app/api/admin_reglamento.py` (`PUT /api/admin/reglamento`, `requiere_escritura`). Registrar el router y la etiqueta `regulation` → «reglamento» en `backend/app/main.py`
- [ ] T006 [US1] Servir `regulation` desde la base en `backend/app/services/contenido.py` e importar el reglamento de la semilla en la edición 2026 en `backend/app/services/importacion.py` (research R8)
- [ ] T007 [US1] Enviar `regulation` a `/api/admin/reglamento` en `frontend/src/lib/persistencia.ts`, después del evento y las inscripciones y encadenando la versión, con su caso en `frontend/tests/persistencia.test.ts`

## Phase 3: User Story 2 — Mantener los datos de contacto (P1)

**Goal**: correo, teléfono e Instagram persistentes y aplicados en todas las ubicaciones públicas.

**Independent Test**: cambiar los tres datos, comprobar `/api/content` y las páginas, reiniciar y restaurar.

- [ ] T008 [US2] Añadir a `backend/tests/test_reglamento_contacto.py` las pruebas de contacto:
  - creación con versión 0, edición, 409 y doble envío;
  - validaciones de cada campo con su etiqueta: correo, teléfono (letras, menos de 6 dígitos, más de 15) e Instagram (`http`, otro dominio, credenciales);
  - `contactVersion` solo en la vista privada;
  - importación sin pisar datos editados;
  - persistencia con un cliente nuevo.
- [ ] T009 [US2] Crear `backend/app/schemas/contacto.py` con `ContactoEntrada` según data-model.md `Configuracion.correo`, `Configuracion.telefono` y `Configuracion.instagram` (research R5)
- [ ] T010 [US2] Implementar `backend/app/services/contacto.py` (`a_contrato`, `guardar` con versión) y `backend/app/api/admin_contacto.py` (`PUT /api/admin/contacto`). Registrar el router y las etiquetas `email`, `phone` e `instagram` en `backend/app/main.py`
- [ ] T011 [US2] Servir `settings.email/phone/instagram` (y `contactVersion` en la vista privada) en `backend/app/services/contenido.py` e importar el contacto de la semilla en `backend/app/services/importacion.py`
- [ ] T012 [US2] Enviar los cambios de contacto a `/api/admin/contacto` con `contactVersion` en `frontend/src/lib/persistencia.ts` (añadir `contactVersion` a `CAMPOS_TECNICOS`), con su caso en `frontend/tests/persistencia.test.ts`
- [ ] T013 [US2] Crear `usuarioInstagram` en `frontend/src/lib/contacto.ts` (research R7) con su prueba en `frontend/tests/contacto.test.ts`, y usarla en `Contact` de `frontend/src/components/Site.tsx`

## Phase 4: User Story 3 — Panel guardado por recursos (P2)

**Goal**: sin guardado del documento completo; los cambios sin recurso se rechazan en el cliente.

**Independent Test**: `PUT /api/content` → 405; `planificar` con un ajuste desconocido → error local.

- [ ] T014 [US3] Retirar `PUT /api/content` de `backend/app/api/contenido.py`. Pasar las pruebas de protección de `backend/tests/test_proteccion.py` a `PUT /api/admin/contacto` (research R6) y añadir la comprobación de 405
- [ ] T015 [US3] Cambiar `frontend/src/lib/persistencia.ts`: un cambio sin recurso devuelve un error local («Esta sección del panel todavía no guarda cambios.») sin llamar al servidor. Actualizar `frontend/tests/persistencia.test.ts`

## Phase 5: Polish

- [ ] T016 Capturar el texto de `/reglamento`, `/contacto` y el pie con la versión anterior en marcha. Después, reconstruir, migrar e importar en local (`alembic upgrade head`, `importar-inicial`) y comprobar que el texto es idéntico (SC-005)
- [ ] T017 Crear y ejecutar `frontend/scripts/verificar-reglamento-contacto.mjs` (quickstart: reglamento, persistencia tras reinicio, contacto en todas las ubicaciones, `mailto`, validación sin éxito simulado, restauración). Actualizar el paso 4 de `frontend/scripts/verificar-acceso.mjs` (error del servidor en `/admin/ajustes`)
- [ ] T018 Ejecutar ruff, pytest, vitest, `typecheck`, `build` y la regresión de Playwright. Actualizar `docs/arquitectura.md`, `docs/ROADMAP.md`, `docs/ESTADO_PROYECTO.md` y `docs/referencia/DISCREPANCIAS.md` (C2 y M1)

## Dependencies & Execution Order

- **Orden de las fases**: Phase 1 → US1 y US2 (independientes entre sí) → US3 (necesita US1 y US2, porque antes de retirar el guardado del documento completo no puede quedar ninguna sección sin recurso) → Polish.
- **Dentro de cada historia**: prueba → esquema → servicio y API → contenido e importación → cliente.
- **En paralelo**: US1 y US2 pueden avanzar a la vez en el backend; sus pruebas comparten `test_reglamento_contacto.py`, así que se escriben una tras otra.

## Implementation Strategy

- **MVP**: US1 (reglamento).
- **Después**: US2 (contacto) y, por último, US3, que cierra la transición M1.
