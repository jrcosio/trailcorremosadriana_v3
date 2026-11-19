---
description: "Tareas de implementación de la feature 002-administrador"
---

# Tasks: Administrador

**Input**: Design documents from `/specs/002-administrador/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluidas (constitución V): pytest contra PostgreSQL real por historia, vitest de
`apiFetch` y Playwright de extremo a extremo a través de Caddy.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [ ] T001 Añadir `argon2-cffi>=25.1,<25.2` a `backend/pyproject.toml` y regenerar `backend/uv.lock`
- [ ] T002 [P] Añadir las variables de data-model.md «Configuración nueva» (`SESSION_HOURS`, `COOKIE_SECURE`, `ORIGENES_PERMITIDOS`, `LOGIN_MAX_INTENTOS`, `LOGIN_VENTANA_MINUTOS`) a `.env.example`, `compose.yaml` (`COOKIE_SECURE=false` y `FORWARDED_ALLOW_IPS=*` en desarrollo) y `compose.dev.yaml` (`ORIGENES_PERMITIDOS=http://localhost:5173`)
- [ ] T003 [P] Ampliar `backend/app/core/config.py` con esas variables, incluida la lista de orígenes permitidos normalizados

---

## Phase 2: Foundational (bloqueante)

- [ ] T004 Crear `backend/app/models/base.py` (DeclarativeBase y convención de nombres) y `backend/app/models/__init__.py`
- [ ] T005 Crear `backend/app/models/administracion.py` con `Administrador` (data-model.md `Administrador.id`, `Administrador.usuario`, `Administrador.hash_password`, `Administrador.activo`, `Administrador.creado_en`, `Administrador.actualizado_en`, `Administrador.ultimo_acceso_en`, `Administrador.password_cambiada_en`), `Sesion` (`Sesion.id`, `Sesion.administrador_id`, `Sesion.token_hash`, `Sesion.csrf_hash`, `Sesion.creada_en`, `Sesion.expira_en`, `Sesion.revocada_en`, `Sesion.ultimo_uso_en`) y `LimiteLogin` (`LimiteLogin.clave`, `LimiteLogin.intentos`, `LimiteLogin.inicio`)
- [ ] T006 Apuntar `backend/alembic/env.py` a `Base.metadata` y escribir `backend/alembic/versions/0002_administracion.py`, que crea las tres tablas con sus restricciones e índices de data-model.md (CHECK de `Administrador.usuario` y `LimiteLogin.intentos`, UNIQUE de `Sesion.token_hash`, FK `Sesion.administrador_id` ON DELETE CASCADE, índices de `Sesion.administrador_id` y `Sesion.expira_en`), con su `downgrade`
- [ ] T007 Implementar `backend/app/core/seguridad.py`: hash y verificación Argon2id con rehash, hash ficticio, generación de tokens, huella SHA-256, normalización y validación del usuario (patrón de data-model.md `Administrador.usuario`) y política de contraseña de 12 a 128 caracteres distinta del usuario
- [ ] T008 Añadir en `backend/app/main.py` el manejador que convierte los errores de validación de petición en `400 {"error":"Datos no válidos."}`
- [ ] T009 Ampliar `backend/tests/conftest.py` con ayudas para crear administradores en la base temporal, iniciar sesión con el cliente de pruebas (Origin correcto) y leer las cookies `penasagra_admin` y `penasagra_csrf`

**Checkpoint**: modelo y utilidades de seguridad listos.

---

## Phase 3: User Story 1 - Crear el administrador inicial (P1) 🎯 MVP

**Goal**: alta y recuperación de cuentas solo por comando de operador.

**Independent Test**: `crear-admin` con `--password-stdin` contra la base temporal; un segundo alta se rechaza.

- [ ] T010 [P] [US1] Escribir `backend/tests/test_cli.py`: alta correcta con hash `$argon2id$`, rechazo de usuario duplicado sin modificar la cuenta, rechazo por política (corta, igual al usuario, larga, no coinciden), usuario no válido, normalización, `restablecer-password` revoca sesiones, `activar`, `desactivar`, `revocar-sesiones`, y `listar-admins` sin hashes. Contraseña siempre por stdin, nunca como argumento
- [ ] T011 [US1] Implementar `backend/app/services/administradores.py` (crear, restablecer contraseña, activar, desactivar, listar), con revocación de sesiones al restablecer o desactivar
- [ ] T012 [US1] Implementar `backend/app/cli.py` (ejecutable con `python -m app.cli`), según contracts/cli-operador.md: getpass con confirmación, `--password-stdin` y códigos de salida 0/1/2
- [ ] T013 [US1] Ejecutar `test_cli.py` en `api-test` y probar el comando real en Compose (`docker compose run --rm -T api python -m app.cli crear-admin … --password-stdin`)

---

## Phase 4: User Story 2 - Entrar y salir del panel (P1)

**Goal**: acceso, sesión de 8 h persistente, cierre que revoca y resumen visible.

**Independent Test**: entrar en `/admin`, recargar, reiniciar la API, cerrar sesión y comprobar el rechazo posterior.

- [ ] T014 [P] [US2] Escribir `backend/tests/test_login.py`: acceso correcto con cookies (atributos HttpOnly, SameSite=Strict, Path=/, Max-Age 28800, Secure según configuración); mensaje idéntico para usuario inexistente, contraseña errónea y cuenta inactiva; 503 con la base caída; 400 con cuerpo mal formado; `ultimo_acceso_en` actualizado; el tiempo de respuesta con usuario inexistente es comparable al de contraseña errónea (ratio de medianas entre 0,5 y 2 en 5 intentos)
- [ ] T015 [P] [US2] Escribir `backend/tests/test_sesion.py`: `/api/session` con y sin sesión, nueva emisión de CSRF si falta, `?admin=1` con sesión devuelve borradores, un token inventado, manipulado o de una sesión revocada → sin sesión, caducidad (`expira_en` pasado → 401), logout revoca y borra cookies, la sesión sobrevive a una segunda instancia de la app sobre la misma base, y en la base solo hay huellas (data-model.md `Sesion.token_hash`, `Sesion.csrf_hash`)
- [ ] T016 [US2] Implementar `backend/app/services/sesiones.py`: crear (caducidad = `SESSION_HOURS`), validar (data-model.md «Sesión es válida si…»), revocar, emitir un nuevo CSRF, actualizar `Sesion.ultimo_uso_en` como mucho cada 5 minutos y limpiar sesiones antiguas
- [ ] T017 [US2] Implementar en `backend/app/api/deps.py` `requiere_origen`, `sesion_actual` y `requiere_admin`, y reescribir `backend/app/api/sesion.py` (`POST /api/login`, `GET /api/session`, `POST /api/logout`) según contracts/api-administracion.openapi.yaml
- [ ] T018 [US2] Conectar `GET /api/content?admin=1` a `requiere_admin` en `backend/app/api/contenido.py` (contenido completo sin filtrar)
- [ ] T019 [P] [US2] Crear `frontend/src/lib/api.ts` (`leerCookie`, `apiFetch` con `X-CSRF-Token` en escrituras) y `frontend/tests/api.test.ts`
- [ ] T020 [US2] Cambiar en `frontend/src/components/admin/Admin.tsx` las llamadas de escritura (`save`, cerrar sesión, subida) a `apiFetch`; si el cierre de sesión falla, mostrar el error sin ocultar el panel; sin cambios visuales
- [ ] T021 [US2] Crear `frontend/scripts/verificar-acceso.mjs` (Playwright): acceso con `ADMIN_USUARIO`/`ADMIN_PASSWORD` → resumen «Peñasagra 2027» en menos de 30 s (SC-001); con la API detenida → mensaje de error de servicio sin acceso; recarga → sigue dentro; credenciales erróneas → mensaje genérico; cerrar sesión → formulario; petición privada con la cookie anterior → 401
- [ ] T022 [US2] Actualizar `frontend/scripts/verificar-admin.mjs` al comportamiento de la 002 (acceso erróneo → «Usuario o contraseña incorrectos.» y sin cookies; vista de diseño sin escrituras)

---

## Phase 5: User Story 3 - Proteger lecturas privadas y escrituras (P1)

**Goal**: Origin → sesión → CSRF en todas las escrituras; las secciones sin persistencia responden 501 sin simular éxito.

**Independent Test**: matriz de peticiones sin sesión, sin CSRF, con CSRF ajeno y con origen ajeno o ausente sobre todas las rutas de escritura.

- [ ] T023 [P] [US3] Escribir `backend/tests/test_proteccion.py`: matriz sobre `PUT /api/content`, `POST /api/upload`, `POST /api/logout` y `POST /api/login` (origen ausente o ajeno → 403; sin sesión → 401; sin CSRF o con CSRF de otra sesión → 403; con todo válido → 501 en las secciones sin persistencia); `?admin=1` sin sesión → 401; los errores no contienen tokens ni detalles internos
- [ ] T024 [US3] Implementar `requiere_csrf` y la dependencia combinada `requiere_escritura` en `backend/app/api/deps.py`
- [ ] T025 [US3] Añadir `PUT /api/content` (501) en `backend/app/api/contenido.py` y crear `backend/app/api/archivos.py` (`POST /api/upload` → 501), ambos detrás de `requiere_escritura`, y registrarlos en `backend/app/main.py`
- [ ] T026 [US3] Verificar con Playwright, con sesión iniciada, que guardar en una sección del panel muestra «Esta sección del panel todavía no guarda cambios.» sin modificar datos (`frontend/scripts/verificar-acceso.mjs`)

---

## Phase 6: User Story 4 - Limitar los intentos de acceso (P2)

**Goal**: 8 fallos en 15 minutos por IP → 429 persistente.

**Independent Test**: 8 fallos, el 9.º correcto → 429; la ventana expirada (manipulada en la base) permite entrar; el bloqueo sigue tras reiniciar.

- [ ] T027 [P] [US4] Escribir `backend/tests/test_limites.py`: 9.º intento → 429 con `Retry-After`, incluso con la contraseña correcta; un acierto antes del umbral reinicia el contador; la ventana expirada reinicia; el bloqueo persiste con una segunda instancia de la app; los intentos con usuarios distintos suman; las IP distintas son independientes (`X-Forwarded-For` en las pruebas); la clave es una huella (data-model.md `LimiteLogin.clave`)
- [ ] T028 [US4] Implementar `backend/app/services/limites.py` con `SELECT … FOR UPDATE` según data-model.md `LimiteLogin.intentos` y `LimiteLogin.inicio`, e integrarlo en `POST /api/login`
- [ ] T029 [US4] Cambiar el arranque de uvicorn en `backend/Dockerfile` para que tome `FORWARDED_ALLOW_IPS` del entorno, y verificar a través de Caddy que el bloqueo se aplica por la IP del cliente
- [ ] T030 [US4] Añadir a `frontend/scripts/verificar-acceso.mjs` el bloqueo tras 8 fallos con el mensaje «Demasiados intentos…» y limpiar después `limites_login` en local

---

## Phase 7: User Story 5 - Revocar el acceso (P2)

**Goal**: desactivar, revocar sesiones y restablecer invalidan las sesiones abiertas.

**Independent Test**: con sesión abierta, ejecutar el comando y comprobar el 401 en la siguiente petición privada.

- [ ] T031 [P] [US5] Escribir `backend/tests/test_revocacion.py`: con sesión abierta, `desactivar` → 401 y no puede volver a entrar; `activar` → puede entrar; `revocar-sesiones` → 401 y puede volver a entrar; `restablecer-password` → 401 y la contraseña anterior no sirve; dos sesiones simultáneas son independientes al cerrar una
- [ ] T032 [US5] Ajustar `backend/app/services/administradores.py` y `backend/app/services/sesiones.py` hasta que `test_revocacion.py` pase, y comprobar con Compose `revocar-sesiones` sobre una sesión real del navegador

---

## Phase 8: Polish & cross-cutting

- [ ] T033 [P] Actualizar `docs/arquitectura.md` (sección de seguridad: sesiones, CSRF, Origin, límite e IP real) y `docs/desarrollo.md` (crear el administrador local y desbloquear intentos)
- [ ] T034 [P] Ejecutar ruff y la suite completa (pytest en `api-test`, typecheck, vitest, build) y corregir los fallos
- [ ] T035 Ejecutar quickstart.md §1–§6 a través de Caddy, más `verificar-rutas.mjs` como regresión de la 001, y registrar los resultados
- [ ] T036 Comprobar que no se versionan secretos (sin contraseñas ni tokens en el diff; `.env` ignorado) y actualizar `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

---

## Dependencies & Execution Order

- Setup (T001–T003) → Foundational (T004–T009) → US1 → US2 → US3 → US4 / US5 → Polish.
- US2 necesita una cuenta (US1) para sus pruebas de extremo a extremo; las de pytest crean la
  cuenta con la ayuda de T009.
- US3 depende de `deps.py` (T017). US4 se integra en el login (T017). US5 depende de US1 y US2.

## Parallel Opportunities

- T002/T003; T010; T014/T015/T019; T023; T027; T031; T033/T034.

## Implementation Strategy

MVP: US1 + US2 (cuenta y acceso real). Después la protección completa (US3) y, a continuación,
el límite (US4) y la revocación (US5). Cierre con quickstart, converge y merge local.
