---
description: "Tareas de implementación de la feature 011-cierre"
---

# Tasks: Cierre para el lanzamiento

**Input**: documentos de diseño de `specs/011-cierre/`

**Tests**: incluidos (constitución V). pytest contra PostgreSQL real, Playwright + axe, scripts de copia y ensayo real de despliegue.

## Phase 1: Setup

- [X] T001 Capturar la referencia visual antes de los cambios: `frontend/scripts/capturas.mjs` a 360/768/1024/1440 en `frontend/capturas/antes-011` (carpeta ignorada) y el peso de `frontend/public/fonts/*.woff2`

## Phase 2: User Story 1 — 404 reales y metadatos de detalle (P1) 🎯 MVP

**Goal**: estado 404 real y metadatos propios en el HTML inicial de los detalles publicados.

**Independent Test**: `curl` de rutas inexistentes, borradores y detalles publicados; HTML inicial sin ejecutar JS.

- [X] T002 [P] [US1] Escribir `backend/tests/test_meta.py` (contrato de `contracts/meta-y-rutas.md`):
  - detalle publicado de noticia, álbum, prueba (`/carreras` y `/recorridos`) y `/clasificaciones/2026` con sus etiquetas;
  - escapado de `<`, `&` y comillas;
  - imagen absoluta y de reserva;
  - borrador, inexistente, identificador no válido y más de dos segmentos → `no-encontrada`;
  - año sin clasificaciones publicadas → `no-encontrada`;
  - 404/405 genéricos de la API en español.
- [X] T003 [US1] Implementar `backend/app/services/meta.py` con los campos de data-model.md `MetadatosPagina.titulo`, `MetadatosPagina.descripcion`, `MetadatosPagina.imagen`, `MetadatosPagina.canonica` y `MetadatosPagina.tipo`, y `backend/app/api/meta.py` (`GET /api/meta`, siempre 200 en texto). Registrar el router en `backend/app/main.py` y traducir allí los 404/405 genéricos
- [X] T004 [US1] Generar `plantilla.html` (plantilla de Caddy según research R1) y `404.html` (noindex) en `frontend/plugins/metadatos-rutas.ts`, con su prueba en `frontend/tests/metadatos.test.ts`
- [X] T005 [US1] Cambiar `infra/caddy/Caddyfile`: las rutas sin HTML estático pasan por la plantilla (`templates`); `handle_errors` sirve `404.html` con 404 en rutas que no son de la API y `app.html` con 200 si falla la plantilla
- [X] T006 [US1] Crear y ejecutar `frontend/scripts/verificar-cierre.mjs` (sección 404 y metadatos):
  - estados y `og:*` en el HTML inicial;
  - el SPA muestra «Este sendero no está en el mapa.» en las 404;
  - API detenida → 200 con los metadatos genéricos;
  - `/admin` y sus subrutas siguen dando 200 con `noindex`.

## Phase 3: User Story 2 — Accesibilidad y móvil (P1)

**Goal**: 0 incumplimientos WCAG 2.1 A/AA y 0 desbordamientos, con solo los cambios de P4.

**Independent Test**: `verificar-accesibilidad.mjs` y comparación de capturas.

- [X] T007 [P] [US2] Crear `frontend/scripts/verificar-accesibilidad.mjs`:
  - axe (`@axe-core/playwright` 4.10.2, WCAG 2.1 A/AA) a 360 y 1440 px en todas las rutas públicas, un detalle de cada tipo, la 404 y el acceso al panel;
  - desbordamiento a 320, 340, 360, 768, 1024 y 1440 px.
- [X] T008 [US2] Aplicar P4 en `frontend/src/styles/ajustes.css` (`.button` principal `#b64b24`/`#9a3d1c`, textos del bloque solidario en blanco, enlace del pie subrayado) y corregir la cabecera a 320/340 px. Ejecutar T007 hasta 0 incumplimientos
- [X] T009 [US2] Comparar las capturas de T001 con las nuevas y documentar que solo cambian los elementos de P4

## Phase 4: User Story 3 — Copias, restauración y despliegue independiente (P1)

**Goal**: restauración idéntica y despliegue reproducible solo con la documentación.

**Independent Test**: `verificar-copia.sh` y ensayo en `trail-ensayo`.

- [X] T010 [P] [US3] Crear `infra/scripts/verificar-copia.sh` (research R3) y ejecutarlo: huellas por tabla y por archivo antes y después de restaurar (data-model.md `CopiaSeguridad`)
- [X] T011 [US3] Añadir `SITE_ADDRESS` (por defecto `:80`) a `infra/caddy/Caddyfile`, crear `compose.produccion.yaml` (80/443, `ENTORNO=produccion`, `COOKIE_SECURE=true`, `PANTALLAS=no`) y documentar las variables nuevas en `.env.example`
- [X] T012 [US3] Escribir `docs/operacion.md`:
  - instalación, variables, dominio y HTTPS, R2 (y sus copias), administrador;
  - copias y restauración, actualización con migraciones, recuperación del acceso;
  - comprobaciones tras desplegar.
- [X] T013 [US3] Ensayo de despliegue: clon limpio en una carpeta temporal, proyecto `trail-ensayo` en el puerto 8090, solo con `docs/operacion.md` y la copia de T010. La copia se restaura sobre una base recién creada. Comprobar la web, el acceso al panel y un archivo restaurado. Retirar con `down -v` del proyecto `trail-ensayo` y comprobar que el entorno de desarrollo no ha cambiado

## Phase 5: User Story 4 — CSP y `/pantallas` (P2)

**Goal**: CSP sin bloqueos y `/pantallas` retirada en producción.

**Independent Test**: recorrido sin violaciones; `/pantallas` según `PANTALLAS`.

- [X] T014 [US4] Añadir la CSP por defecto (`?Content-Security-Policy`, research R4) y la regla `PANTALLAS` (404 si no es `si`) en `infra/caddy/Caddyfile`. Pasar `PANTALLAS` en `compose.yaml` (`no`) y en `compose.dev.yaml` (`si`)
- [X] T015 [US4] Ampliar `frontend/scripts/verificar-cierre.mjs`:
  - violaciones de CSP en el recorrido público, en una prueba con Wikiloc y en el panel con subida;
  - `/media` conserva su CSP propia;
  - `/pantallas` 404 con `PANTALLAS=no` y 200 con `si`.
  Adaptar `frontend/scripts/verificar-admin.mjs` a los dos modos.

## Phase 6: User Story 5 — Rendimiento (P2)

**Goal**: fuentes en WOFF2 real con el mismo aspecto.

**Independent Test**: peso, tipo de archivo y capturas.

- [X] T016 [US5] Convertir `frontend/public/fonts/*.woff2` a WOFF2 real con fontTools, cambiar a `format('woff2')` en `frontend/public/fonts/{barlow,manrope}.css` y comprobar el peso (≥ 40 % menos), el tipo, la compresión y la caché de `/fonts`. Comparar las capturas posteriores a P4 (T009) con las posteriores a la conversión: 0 diferencias de píxeles (SC-007). Actualizar `docs/PROCEDENCIA_RECURSOS.md`

## Phase 7: User Story 6 — Limpieza (P3)

**Goal**: huérfanos liberables sin riesgo, sin código muerto ni avisos.

**Independent Test**: `limpiar-archivos` en modo listado y borrado; pytest sin avisos.

- [X] T017 [P] [US6] Escribir `backend/tests/test_limpieza.py`:
  - huérfano antiguo listado y no borrado sin `--borrar`;
  - borrado solo con «BORRAR» (fila y objeto);
  - referenciado (también desde un borrador) y reciente intactos;
  - otra respuesta → código 1 sin cambios.
- [X] T018 [US6] Implementar en `backend/app/services/archivos.py` y `backend/app/cli.py` el comando `limpiar-archivos` con data-model.md `ArchivoHuerfano` (`Archivo.clave` sin referencias y `Archivo.creado_en` anterior al umbral)
- [X] T019 [US6] Eliminar el código sin uso (`frontend/src/components/Site.tsx`, `frontend/src/components/admin/Admin.tsx`, `backend/app/api/media.py`) y pasar a `httpx2==2.16.0` en `backend/pyproject.toml` (y `uv.lock`). Comprobar `tsc --noUnusedLocals`, vulture y pytest sin avisos

## Phase 8: Polish

- [ ] T020 Ejecutar ruff, pytest, vitest, `typecheck`, `build` y la regresión completa de Playwright (con `PANTALLAS=si` donde haga falta) y la de respaldo con la API detenida
- [ ] T021 Actualizar `docs/arquitectura.md`, `docs/desarrollo.md`, `docs/ROADMAP.md`, `docs/ESTADO_PROYECTO.md` (cierre del proyecto) y `docs/referencia/DISCREPANCIAS.md` (U4, U5, U6 y C4 resueltas)

## Dependencies & Execution Order

- **Antes de todo**: T001 (referencia visual).
- **Historias**: US1–US6 son independientes entre sí, con dos salvedades:
  - T015 usa el Caddyfile de T005 y T014;
  - T013 usa la copia de T010 y la documentación de T012.
- **Orden dentro de las historias**: T005 → T006; T007 → T008 → T009; T017 → T018.
- **Cierre**: Polish va al final.
- **En paralelo [P]**: T002, T007, T010 y T017 (archivos distintos). T005, T011 y T014 tocan el mismo `Caddyfile`, así que van en orden.

## Implementation Strategy

- **MVP**: US1, que da los 404 reales y los metadatos.
- **Orden recomendado después**: US2 y US3 (requisitos de lanzamiento), luego US4 y US5 y, por último, US6.
