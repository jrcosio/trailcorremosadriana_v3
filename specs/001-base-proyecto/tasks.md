---
description: "Tareas de implementación de la feature 001-base-proyecto"
---

# Tasks: Base del proyecto

**Input**: Design documents from `/specs/001-base-proyecto/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluidas por exigencia de la constitución (principio V): pytest contra PostgreSQL
real, vitest con las comprobaciones existentes de la propuesta, capturas Playwright y ejecución
del quickstart.

**Organization**: Tareas agrupadas por historia de usuario.

Fuente de referencia (solo lectura): `datos_iniciales/Trail_Penasagra_Desarrollo/proyecto/`
(en adelante `PROP/`).

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (infraestructura compartida)

- [X] T001 Crear la estructura `frontend/`, `backend/`, `infra/caddy/`, `infra/scripts/` según plan.md
- [X] T002 [P] Crear `frontend/package.json` (react 19.2.6, react-dom 19.2.6, lucide-react 1.31.0; dev: vite 8.0.13, @vitejs/plugin-react 6.0.2, typescript 5.9.3, @types/react 19.2.14, @types/react-dom 19.2.3, @types/node 22.19.19, vitest 5.1.1, playwright 1.65.1; scripts dev, build, preview, typecheck, test, capturas) y `frontend/.npmrc`
- [X] T003 [P] Crear `frontend/tsconfig.json` (alias `@/*` → `src/*`, jsx react-jsx, sin plugin next ni tipos de Workers) y `frontend/vite.config.ts` (alias `@`, proxy `/api` y `/media` → `http://127.0.0.1:8000`, configuración de vitest)
- [X] T004 [P] Crear `backend/pyproject.toml` (Python 3.13; fastapi, uvicorn[standard], sqlalchemy, psycopg[binary], alembic, pydantic, pydantic-settings; dev: pytest, httpx, ruff) y generar `backend/uv.lock` con `uv lock`
- [X] T005 [P] Crear `.env.example` con las variables de data-model.md «Configuración del entorno» (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `PUBLIC_ORIGIN`, `WEB_PORT`, `ENTORNO`, `LOG_LEVEL`) con valores de desarrollo
- [X] T006 [P] Crear `frontend/.dockerignore` y `backend/.dockerignore` (node_modules, dist, capturas, .venv, __pycache__, .env*)

---

## Phase 2: Foundational (bloqueante)

- [X] T007 Implementar `backend/app/core/config.py` (pydantic-settings con las variables de data-model.md «Configuración del entorno»)
- [X] T008 Implementar `backend/app/core/db.py` (engine SQLAlchemy con `pool_pre_ping=True` y `connect_timeout=3`, fábrica de sesiones)
- [X] T009 Configurar Alembic: `backend/alembic.ini`, `backend/alembic/env.py` (URL desde config), `backend/alembic/script.py.mako` y revisión `backend/alembic/versions/0001_base.py` (data-model.md «Esquema PostgreSQL»)
- [X] T010 Implementar `backend/app/main.py` (FastAPI, registro de routers, cabeceras `Cache-Control: no-store` y `X-Content-Type-Options: nosniff` en `/api/*`, OpenAPI en `/api/docs` solo con `ENTORNO=desarrollo`, según research.md R5)
- [X] T011 Crear `backend/Dockerfile` multietapa (`base` con dependencias sin dev, `test` con dev y tests, `runtime` con uvicorn y alembic) usando uv
- [X] T012 Crear `compose.yaml` (servicios `db` postgres:17-alpine sin puertos y con healthcheck y volumen `pgdata`; `api` dependiente de `db` sano, con healthcheck; `web` Caddy publicando `${WEB_PORT:-8080}`; red `interna`; valores por defecto de desarrollo)
- [X] T013 Crear `compose.dev.yaml` (publica `api` en `127.0.0.1:8000` y `db` en `127.0.0.1:5432`; servicio `api-test` con target `test` y perfil `test`)
- [X] T014 Crear `infra/caddy/Caddyfile` según contracts/rutas-web.md (proxy `/api/*` y `/media/*`, resolución de HTML por ruta, `/admin*` y `/pantallas*`, fallback `app.html`, cabeceras y caché)
- [X] T015 Crear `frontend/Dockerfile` (etapa node:22-alpine con `npm ci` y `npm run build` con `PUBLIC_ORIGIN`; etapa final caddy:2.11-alpine con `dist/` en `/srv`)
- [X] T016 Implementar `backend/tests/conftest.py` (creación y borrado de bases temporales en el PostgreSQL de Compose, aplicación de Alembic, cliente de pruebas con settings sobrescritos)

**Checkpoint**: base técnica lista.

---

## Phase 3: User Story 1 - Web pública con la apariencia aprobada (P1) 🎯 MVP

**Goal**: servir todas las pantallas del mapa con apariencia idéntica a la propuesta.

**Independent Test**: abrir cada ruta de FR-001 directamente y al recargar; capturas a
360/768/1024/1440 px comparadas con la referencia publicada.

- [X] T017 [P] [US1] Copiar `PROP/app/globals.css` → `frontend/src/styles/globals.css` sin cambios
- [X] T018 [P] [US1] Copiar `PROP/public/{reused,images,fonts,templates}` y `robots.txt` → `frontend/public/` (con `fonts/licencias/*_OFL.txt`); no copiar `favicon.svg` del starter
- [X] T019 [P] [US1] Copiar `PROP/lib/{data,classifications,registration}.ts` → `frontend/src/lib/`
- [X] T020 [US1] Copiar `PROP/components/{Site,Results,ClassificationTable,DorsalSolidario}.tsx` y `PROP/components/admin/*.tsx` → `frontend/src/components/` quitando solo `'use client'`
- [X] T021 [US1] Crear `frontend/index.html` (lang es, metadatos genéricos, favicon `/reused/logos/logo1.webp`, `#root`) y `frontend/src/main.tsx` (normaliza la barra final y renderiza `<Site path>`)
- [X] T022 [P] [US1] Portar a `frontend/tests/solidario.test.tsx` las comprobaciones puras de `PROP/scripts/check-solidarity.tsx` (matriz de disponibilidad y render de `DorsalSolidario` en banner y tarjeta)
- [X] T023 [P] [US1] Portar a `frontend/tests/clasificaciones.test.tsx` las comprobaciones puras de `PROP/scripts/check-classifications.tsx` (parseo, mapeo, DNF sin posición, exclusión solidaria, render de tabla y resultados)
- [X] T024 [US1] Instalar dependencias y ejecutar `npm run typecheck`, `npm test` y `npm run build` en `frontend/` hasta que pasen
- [X] T025 [US1] Crear `frontend/scripts/capturas.mjs` (Playwright: rutas clave × 360/768/1024/1440, captura de página completa, `innerText`, detección de `scrollWidth > innerWidth`, `informe.json`)
- [X] T026 [US1] Ejecutar las capturas en local (requiere T037: API sirviendo contenido) y en la referencia, comparar y registrar el resultado en `specs/001-base-proyecto/revision-visual.md`
- [X] T053 [US1] Crear y ejecutar `frontend/scripts/verificar-rutas.mjs` (Playwright): todas las rutas de FR-001 incluidas `/carreras/{id}`, `/recorridos/{id}`, `/noticias/proxima-edicion`, `/galeria/edicion-2026`, `/pantallas/admin/*` y una ruta inexistente; HTTP 200, pantalla esperada al abrir y al recargar

**Checkpoint**: la web se ve igual que la propuesta.

---

## Phase 4: User Story 2 - Arrancar y comprobar el entorno (P1)

**Goal**: entorno reproducible con salud y disponibilidad.

**Independent Test**: quickstart pasos 1–3 desde cero.

- [X] T027 [P] [US2] Escribir `backend/tests/test_salud.py` (`/api/health` 200 `viva` aunque la base sea inaccesible)
- [X] T028 [P] [US2] Escribir `backend/tests/test_ready.py` (200 `disponible` con esquema aplicado; 503 `migraciones_pendientes` en base nueva; 503 `base_de_datos_inaccesible` en menos de 5 s con URL inaccesible; sin datos internos en la respuesta)
- [X] T029 [US2] Implementar `backend/app/services/esquema.py` (revisión actual frente a cabeza de Alembic)
- [X] T030 [US2] Implementar `backend/app/api/salud.py` (`/api/health`, `/api/ready` según contracts/api-base.openapi.yaml)
- [X] T031 [US2] Ejecutar pytest en `api-test` contra PostgreSQL y corregir fallos
- [X] T032 [US2] Ejecutar quickstart §1–§3 (build, migración explícita, arranque, salud, base detenida, reinicio) y registrar los resultados en `docs/ESTADO_PROYECTO.md`

**Checkpoint**: entorno verificable.

---

## Phase 5: User Story 3 - Contenido público servido por el servicio propio (P2)

**Goal**: `GET /api/content` sirve la semilla curada con el contrato existente.

**Independent Test**: quickstart §4 y comportamiento de respaldo con la API detenida.

- [X] T033 [US3] Generar `backend/seed/contenido_inicial.json` evaluando `seed` de `PROP/lib/data.ts` (data-model.md `Settings.edition` = 2027 y `Settings.date` vacío; colecciones según «Colecciones»), compararla con `datos_iniciales/Trail_Penasagra_Desarrollo/contenido/contenido-publicado.json` y documentar procedencia, diferencias y exclusiones D1–D4 en `backend/seed/README.md`
- [X] T034 [P] [US3] Implementar `backend/app/schemas/contenido.py` (Pydantic `SiteData` con `extra=allow`; reglas de data-model.md `Settings.edition`, `Settings.date`, `Settings.solidarityRegistration`, `Settings.registrationMessage`, `Settings.email`, `Settings.phone`, `Settings.instagram`, `Item.id`, `Item.published`, límites de `races`, `news`, `albums`, `results`, `sponsors`, `collaborators` y `regulation`)
- [X] T035 [P] [US3] Escribir `backend/tests/test_contenido.py` (forma del contrato; solo publicados; sin datos D1–D4; `?admin=1` → 401; cabeceras `no-store` y `nosniff`; semilla inválida impide arrancar)
- [X] T036 [US3] Implementar `backend/app/services/contenido.py` (carga y validación de la semilla al arrancar y filtro `publicData` de data-model.md «Reglas de la vista pública»)
- [X] T037 [US3] Implementar `backend/app/api/contenido.py` (`GET /api/content` con `revision: 0`)
- [X] T038 [US3] Verificar con Playwright que, con `api` detenida, la web muestra el contenido de referencia y el aviso «No se han podido comprobar las últimas novedades» (añadir comprobación a `frontend/scripts/capturas.mjs` o script `frontend/scripts/verificar-respaldo.mjs`)

**Checkpoint**: contenido servido por la API.

---

## Phase 6: User Story 4 - Títulos y descripciones por página (P2)

**Goal**: metadatos propios en el documento inicial de cada ruta pública estática.

**Independent Test**: `curl` de cada ruta y comparación de títulos.

- [X] T039 [P] [US4] Crear `frontend/src/seo/rutas.ts` con la tabla de contracts/rutas-web.md
- [X] T040 [US4] Implementar `frontend/plugins/metadatos-rutas.ts` (genera `dist/<ruta>/index.html`, `dist/app.html`, `dist/admin/index.html` y `dist/pantallas/index.html` con título, descripción, OG, Twitter, canonical y `noindex` donde corresponda) y registrarlo en `frontend/vite.config.ts`
- [X] T041 [P] [US4] Escribir `frontend/tests/metadatos.test.ts` (11 títulos distintos; `noindex` en admin y pantallas; `og:image` absoluta con `PUBLIC_ORIGIN`)
- [X] T042 [US4] Verificar a través de Caddy los títulos de las 11 rutas y `robots.txt`

**Checkpoint**: metadatos por ruta.

---

## Phase 7: User Story 5 - Vistas de revisión y acceso al panel (P3)

**Goal**: `/pantallas` y vistas de diseño sin escritura; `/admin` sin acceso hasta 002.

**Independent Test**: intentar acceso en `/admin` y guardar en una vista de diseño.

- [X] T043 [P] [US5] Escribir `backend/tests/test_sesion.py` (`/api/session` → `{"authenticated": false}`; `/api/login` → 503 con `error` y sin `Set-Cookie`)
- [X] T044 [US5] Implementar `backend/app/api/sesion.py`
- [X] T045 [US5] Verificar con Playwright que `/admin` muestra el error de acceso sin conceder acceso y que guardar en `/pantallas/admin/noticias/nuevo` muestra el aviso de vista de diseño sin peticiones de escritura (`frontend/scripts/verificar-admin.mjs`)

**Checkpoint**: todas las historias funcionan.

---

## Phase 8: Polish & cross-cutting

- [X] T046 [P] Escribir `docs/arquitectura.md` (estructura, procesos, mismo origen, decisiones de research.md)
- [X] T047 [P] Escribir `docs/PROCEDENCIA_RECURSOS.md` (recursos y código reutilizados, origen y licencia)
- [X] T048 [P] Escribir `docs/desarrollo.md` (flujo único de arranque, desarrollo con Vite, pruebas) y `README.md` en la raíz
- [X] T049 [P] Crear `infra/scripts/backup.sh` y `infra/scripts/restore.sh` (pg_dump/pg_restore vía `docker compose exec`, documentados; prueba completa en 011)
- [X] T050 Comprobar independencia: clon limpio sin `datos_iniciales` construye y queda disponible siguiendo la documentación (cronometrado, objetivo < 15 min, SC-003); `git ls-files` sin `datos_iniciales` ni `.env`; imágenes sin `datos_iniciales` ni secretos
- [X] T051 Ejecutar quickstart completo (§1–§8), verificar que `db` no publica puertos con `compose.yaml` (`docker compose port db 5432` sin resultado, FR-013) y anotar resultados
- [X] T052 Actualizar `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

---

## Dependencies & Execution Order

- Setup (T001–T006) → Foundational (T007–T016) → historias.
- US1 depende de T014/T015 para la verificación en Caddy; su construcción (T017–T024) solo de
  T002/T003. T026 y T053 se ejecutan cuando US3 (T037) sirve contenido.
- US2 depende de T007–T013 y T016.
- US3 depende de US2 (API en marcha) para su verificación; T038 depende de US1.
- US4 depende de US1 (build del frontend) y de T014.
- US5 depende de US1 y de T010.
- Polish al final; T051 tras todas las historias.

## Parallel Opportunities

- T002–T006 en paralelo.
- T017–T019 en paralelo; T022/T023 en paralelo tras T020.
- T027/T028, T034/T035, T039/T041 y T046–T049 en paralelo.

## Implementation Strategy

1. MVP: Setup + Foundational + US1 + US2 (web servida y entorno comprobable).
2. US3 conecta el contrato de contenido; US4 añade metadatos; US5 cierra panel y vistas.
3. Polish, quickstart completo y cierre de la feature.

---

## Phase 9: Convergence

- [X] T054 Registrar en `docs/ESTADO_PROYECTO.md` y `docs/ROADMAP.md` los resultados reales de las pruebas (quickstart §1–§8, pytest, vitest, verificaciones Playwright, clon limpio cronometrado), decisiones y punto de continuidad per T032, T052, Constitución «Flujo de desarrollo» (partial)
- [X] T055 Limitar `Settings.instagram` a vacío o https sin credenciales en `backend/app/schemas/contenido.py` y cubrirlo en `backend/tests/test_contenido.py` per data-model.md `Settings.instagram` (partial)
- [X] T056 Aclarar en `.env.example` que `DATABASE_URL` solo se usa al ejecutar la API fuera de Compose (dentro se deriva de `POSTGRES_*`) per FR-012 (partial)
- [X] T057 Registrar el ajuste A-001 (`frontend/src/styles/ajustes.css`, desbordamiento de cabecera a 360 px) como trabajo trazable de la feature y verificar su documentación en `revision-visual.md` y `docs/arquitectura.md` per SC-002, Constitución I (unrequested)
