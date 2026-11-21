---
description: "Tareas de implementación de la feature 012-ajustes-revision"
---

# Tasks: Ajustes de la revisión del propietario

**Input**: documentos de diseño de `specs/012-ajustes-revision/`

**Tests**: incluidos (constitución V): vitest, Playwright con la geometría de las fotos, axe y capturas.

## Phase 1: Setup

- [X] T001 Crear `frontend/scripts/verificar-fotos.mjs` (research R2). Con `--referencia <json>`, guarda el tamaño y la posición de cada marco de foto; con `--comparar <json>`, comprueba `contain`, foto dentro del área visible, relleno y marcos iguales. Ejecutarlo antes del cambio para guardar `frontend/capturas/marcos-antes-012.json` y tomar capturas en `frontend/capturas/antes-012`

## Phase 2: User Story 1 — Las fotos se ven siempre completas (P1) 🎯 MVP

**Goal**: 0 fotos recortadas, con los marcos en su sitio y el relleno de la propia foto oscurecida.

**Independent Test**: `verificar-fotos.mjs --comparar` a 320/360/768/1024/1440 y en el panel; revisión visual de la foto de Adriana.

- [X] T002 [P] [US1] Escribir `frontend/tests/fotos.test.ts`: `fondoFoto` devuelve `--foto` con la URL entre comillas, escapa `"`, `\` y saltos de línea, y devuelve un objeto vacío sin URL
- [X] T003 [US1] Crear `frontend/src/lib/fotos.ts` con `fondoFoto(src)` (research R1)
- [X] T004 [US1] Añadir `style={fondoFoto(…)}` a las 9 imágenes de foto de `frontend/src/components/Site.tsx` y a las 2 miniaturas de `frontend/src/components/admin/Admin.tsx`
- [X] T005 [US1] Añadir A-004 a `frontend/src/styles/ajustes.css`: `contain` y centrado en los 11 selectores, con el fondo de relleno de research R1
- [X] T006 [US1] Reconstruir `web` y ejecutar `verificar-fotos.mjs --comparar` (públicas y panel), `verificar-accesibilidad.mjs` y las capturas en `frontend/capturas/despues-012`. Revisar visualmente la foto de Adriana en `/` y `/solidaridad` y una tarjeta de prueba. Comprobar en `verificar-fotos.mjs` que los logotipos, el visor y la vista previa de subida no cambian (FR-005), y que una foto que no carga deja el marco en `#172e28`

## Phase 3: User Story 2 — Desplegar en la MV de la web anterior (P1)

**Goal**: producción con HTTPS, `www`, HSTS y panel con dominio con «ñ»; guía de migración y de
acceso.

**Independent Test**: ensayo de producción con HTTPS (research R3).

- [X] T008 [US2] Normalizar a *punycode* en `normalizar_origen` (`backend/app/core/config.py`) y usar el origen normalizado en `backend/app/api/meta.py`, con pruebas en `backend/tests/test_origen_idn.py`
- [X] T009 [US2] Añadir `import /etc/caddy/sitios/*.caddy` y HSTS a `infra/caddy/Caddyfile`. Crear `infra/caddy/redireccion-www.caddy`. Montarlo y pasar `PUBLIC_ORIGIN` a `web` en `compose.produccion.yaml`
- [X] T010 [US2] Ampliar `docs/operacion.md`:
  - `SITE_ADDRESS` y `PUBLIC_ORIGIN` en *punycode*;
  - migración desde la v2 en la misma MV (parada, arranque, datos con los CSV de la v2,
    comprobaciones y vuelta atrás);
  - «Acceso al panel».
- [X] T011 [US2] Ensayo de producción con HTTPS desde un clon limpio (research R3):
  - HTTP→HTTPS, `www`→dominio y HSTS;
  - certificado;
  - acceso al panel con cookie `Secure` y un guardado real;
  - página con metadatos y CSP.

  Retirarlo y comprobar que el entorno de desarrollo sigue intacto.

## Phase 3b: User Story 3 — Logotipo nuevo en la cabecera (P1)

**Goal**: el logotipo del propietario sustituye a la silueta y al texto en dos filas de la
cabecera pública, sin mover nada más y nítido en cualquier pantalla.

**Independent Test**: `verificar-logo.mjs --comparar` a 320–1440 px y en los anchos de cambio de
diseño; capturas y axe.

- [X] T013 [US3] Crear `frontend/scripts/verificar-logo.mjs` (research R4) y ejecutar `--referencia capturas/cabecera-antes-012.json` antes del cambio
- [X] T014 [P] [US3] Generar `frontend/public/reused/logos/logo_cabecera-480.webp` y `logo_cabecera-720.webp` desde `datos_iniciales/new_logo.png` (recorte al contenido, Lanczos, WebP con calidad 90), y registrar su procedencia en `docs/PROCEDENCIA_RECURSOS.md`
- [X] T015 [US3] Sustituir en `frontend/src/components/Site.tsx` la marca de la cabecera por el `<img>` del logotipo (`srcset`/`sizes`, `width`/`height`, `alt`), conservando el enlace y su `aria-label`. El pie conserva `Brand white`
- [X] T016 [US3] Añadir A-005 a `frontend/src/styles/ajustes.css`: altura del logotipo por tramo (80/70/68/58/49 px), `width: auto` y `filter: none`; el enlace conserva el ancho de la marca anterior en cada tramo (research R4, ajuste de la implementación)
- [X] T017 [US3] Reconstruir `web` y ejecutar `verificar-logo.mjs --comparar`, `verificar-accesibilidad.mjs` y las capturas en `frontend/capturas/despues-logo-012`. Revisión visual a 320, 360, 768, 1024 y 1440 px
- [X] T018 [US3] Registrar la decisión P7 en `docs/referencia/DISCREPANCIAS.md` y actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`. Regresión: vitest, `typecheck`, `build`, `verificar-rutas`, `verificar-cierre` y `verificar-fotos --comparar`

## Phase 3c: User Story 4 — Logotipo nuevo también en el pie (P1)

**Goal**: el pie muestra el logotipo en negativo en lugar de la silueta y el texto. La cabecera no
cambia y las demás columnas del pie siguen en su sitio.

**Independent Test**: `verificar-logo.mjs --comparar capturas/pie-antes-012.json` a 320–1440 px y
en los anchos de cambio de diseño; capturas y axe.

- [X] T019 [US4] Ampliar `frontend/scripts/verificar-logo.mjs` (research R5) con:
  - la huella de la marca del pie, las columnas y el contenido de la primera columna;
  - las comprobaciones del pie;
  - el contraste;
  - la densidad del pie.

  Ejecutar `--referencia capturas/pie-antes-012.json` antes del cambio, con `/pantallas`
  disponible.
- [X] T020 [P] [US4] Generar `frontend/public/reused/logos/logo_pie-480.webp` y
  `logo_pie-720.webp` (versión en negativo, research R5) desde `datos_iniciales/new_logo.png`, y
  registrar su procedencia en `docs/PROCEDENCIA_RECURSOS.md`
- [X] T021 [US4] En `frontend/src/components/Site.tsx`:
  - unificar `LogoCabecera` en un componente `Logo` con la variante de cabecera y la de pie (pie
    con `loading="lazy"` y `sizes="233px"`);
  - usarlo en `Footer`;
  - eliminar `Brand`.
- [X] T022 [US4] Añadir A-006 a `frontend/src/styles/ajustes.css`: logotipo del pie de 233 px de
  ancho como máximo (100 % de la columna si es menor), con `height: auto` y `filter: none`
- [X] T023 [US4] Reconstruir `web` y ejecutar:
  - `verificar-logo.mjs --comparar capturas/pie-antes-012.json`;
  - `verificar-accesibilidad.mjs`;
  - las capturas en `frontend/capturas/despues-pie-012`, con revisión visual del pie a 320, 360,
    768, 1024 y 1440 px.

  Comprobar también el caso en que el logotipo no carga.
- [X] T024 [US4] Registrar la decisión P8 en `docs/referencia/DISCREPANCIAS.md` y actualizar
  `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`. Regresión: vitest,
  `typecheck`, `build`, `verificar-rutas`, `verificar-cierre` y `verificar-fotos --comparar`

## Phase 4: Polish

- [X] T007 Regresión: vitest, `typecheck`, `build`, `verificar-rutas`, `verificar-cierre` y `verificar-galeria`. Actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`
- [X] T012 Regresión tras la US2 (pytest, `verificar-rutas`, `verificar-cierre` con la configuración local) y actualización de `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Dependencies & Execution Order

- **Orden**: T001 (referencia antes del cambio) → T002 → T003 → T004 → T005 → T006 → T007.
- **En paralelo [P]**: T002 junto a T001 (archivos distintos).
- **US3**: T013 (referencia antes del cambio) → T014 [P] → T015 → T016 → T017 → T018.
- **US4**: T019 (referencia antes del cambio) → T020 [P] → T021 → T022 → T023 → T024.

## Implementation Strategy

- **Alcance**: esta entrega cubre la US1 completa. Los próximos ajustes del propietario se
  añadirán como historias nuevas (US2, US3…) de esta misma feature.
