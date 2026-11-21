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

## Phase 3d: User Story 5 — Nueva frase de autoría en el pie (P1)

**Goal**: la línea inferior del pie dice «Hecho por la Escuela Hacker Cosío», sin enlace, con el
mismo estilo y sin mover nada más.

**Independent Test**: `npx vitest run tests/pie.test.tsx`; `verificar-logo.mjs --comparar
capturas/pie-antes-012.json`; capturas y axe.

- [X] T025 [P] [US5] Escribir `frontend/tests/pie.test.tsx`. Renderiza `Site` en las rutas
  públicas y en una inexistente, y comprueba: el aviso de copyright, la frase nueva, ningún enlace
  en la línea inferior y ningún resto de la frase anterior. Ejecutarlo antes del cambio: debe
  fallar.
- [X] T026 [P] [US5] Ampliar `frontend/scripts/verificar-logo.mjs` con la línea inferior del pie
  (research R6): las dos líneas, sin enlaces, con el mismo color y tamaño, y sin restos. Ejecutarlo
  contra la versión previa: debe detectar la frase anterior.
- [X] T027 [US5] Cambiar la frase en `Footer` (`frontend/src/components/Site.tsx`). Anotar en el
  comentario de A-002 (`frontend/src/styles/ajustes.css`) que la regla del enlace del pie ya no se
  aplica.
- [X] T028 [US5] Reconstruir `web` y ejecutar:
  - vitest;
  - `verificar-logo.mjs --comparar capturas/pie-antes-012.json`, con `/pantallas` en local;
  - `verificar-accesibilidad.mjs`;
  - las capturas en `frontend/capturas/despues-pie-texto-012`, con revisión visual del pie y
    comparación con las de la US4.
- [X] T029 [US5] Registrar la decisión P9 en `docs/referencia/DISCREPANCIAS.md` y actualizar
  `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`. Regresión: `typecheck`,
  `build`, `verificar-rutas`, `verificar-cierre` y `verificar-fotos --comparar`

## Phase 3e: User Story 6 — Podio destacado en las clasificaciones (P1)

**Goal**: los tres primeros de cada clasificación se distinguen con oro, plata y bronce suaves
(fondo, franja y medalla) sin cambiar el resto de la tabla.

**Independent Test**: `npx vitest run tests/podio.test.tsx`; `verificar-podio.mjs --comparar
capturas/podio-antes-012.json`; capturas y axe.

- [X] T030 [US6] Crear `frontend/scripts/verificar-podio.mjs` (research R7) y ejecutar
  `--referencia capturas/podio-antes-012.json` antes del cambio. Comprobar que `--comparar` falla
  con la versión previa.
- [X] T031 [P] [US6] Escribir `frontend/tests/podio.test.tsx`:
  - clase y medalla solo en los puestos 1–3, también con empates;
  - la vista previa del panel, igual;
  - sin puestos, ninguna fila marcada.

  Debe fallar antes del cambio.
- [X] T032 [US6] En `frontend/src/components/ClassificationTable.tsx`, poner `podium podium-N` en
  la fila y el número dentro de `<span class="podium-medal">` en los puestos 1–3
- [X] T033 [US6] Añadir A-007 a `frontend/src/styles/ajustes.css`: fondos de oro, plata y bronce,
  la franja con `box-shadow` interior y la medalla sin cambiar el alto de la fila
- [X] T034 [US6] Reconstruir `web` y ejecutar:
  - vitest;
  - `verificar-podio.mjs --comparar capturas/podio-antes-012.json`;
  - `verificar-accesibilidad.mjs`;
  - las capturas en `frontend/capturas/despues-podio-012`, con revisión visual de la tabla a 360 y
    1440 px y comparación con las de la US5.
- [X] T035 [US6] Registrar la decisión P10 en `docs/referencia/DISCREPANCIAS.md` y actualizar
  `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`. Regresión: `typecheck`,
  `build`, `verificar-rutas`, `verificar-cierre` y `verificar-fotos --comparar`

## Phase 3f: User Story 7 y User Story 8 — Panel: barra lateral con desplazamiento y logotipo oficial (P1)

**Goal**: en cualquier ventana se alcanzan todas las opciones de la barra lateral y «Cerrar
sesión». El panel muestra el logotipo oficial en la barra lateral y en el acceso.

**Independent Test**: `verificar-panel.mjs --comparar capturas/panel-antes-012.json` (con
credenciales); capturas y axe.

- [X] T036 [US7] [US8] Crear `frontend/scripts/verificar-panel.mjs` (research R8) y ejecutar
  `--referencia capturas/panel-antes-012.json` antes del cambio. Comprobar que `--comparar`
  detecta los dos fallos con la versión previa
- [X] T037 [US8] Crear `frontend/src/components/Logo.tsx` (`LogoImg`, con los sitios cabecera,
  pie, panel y acceso) y usarlo en `Logo` de `frontend/src/components/Site.tsx`, con el mismo
  marcado
- [X] T038 [US7] [US8] En `frontend/src/components/admin/Admin.tsx`:
  - barra lateral con `LogoImg` y «ADMINISTRACIÓN»;
  - acceso con `LogoImg`;
  - referencia a la barra y efecto que muestra la opción abierta una vez por sección.
- [X] T039 [US7] [US8] Añadir A-008 a `frontend/src/styles/ajustes.css`:
  - desplazamiento vertical sin arrastrar la página;
  - `overflow-x: clip` con el menú de móvil abierto;
  - logotipo de 180 px en la barra lateral y de 261 px en el acceso.
- [X] T040 [US7] [US8] Reconstruir `web` y ejecutar:
  - `verificar-panel.mjs --comparar`;
  - `verificar-logo.mjs --comparar capturas/pie-antes-012.json`, con `/pantallas`, para la
    cabecera y el pie sin cambios y la barra del panel con el logotipo;
  - `verificar-admin.mjs` y `verificar-acceso.mjs`;
  - `verificar-accesibilidad.mjs`;
  - las capturas en `frontend/capturas/despues-panel-012`, comparadas con las de la US6.

  Revisión visual de la barra lateral y del acceso, y caso en que el logotipo no carga.
- [X] T041 [US7] [US8] Registrar la decisión P11 en `docs/referencia/DISCREPANCIAS.md` y
  actualizar `docs/PROCEDENCIA_RECURSOS.md`, `docs/arquitectura.md`, `docs/ROADMAP.md` y
  `docs/ESTADO_PROYECTO.md`, con el hallazgo de contraste del contenido del panel. Regresión:
  vitest, `typecheck`, `build`, `verificar-rutas`, `verificar-cierre` y `verificar-fotos
  --comparar` con el panel

## Phase 3g: User Story 9 — Contraste AA en todo el panel (P1)

**Goal**: 0 incumplimientos AA en el panel con la sesión iniciada, cambiando solo el color de los
textos que fallan.

**Independent Test**: `verificar-panel-aa.mjs`, con credenciales.

- [X] T042 [US9] Crear `frontend/scripts/verificar-panel-aa.mjs` (research R9):
  - axe en todas las secciones, un elemento existente y el alta de cada colección, a 360, 1024 y
    1440 px;
  - estados de guardado con las escrituras interceptadas;
  - las dos variantes de la etiqueta de estado;
  - fallos agrupados.

  Ejecutarlo antes del cambio para obtener la lista de defectos.
- [X] T043 [US9] Hacer capturas del panel antes del cambio: 6 pantallas a 1440 y 360 px
- [X] T044 [US9] Añadir A-009 a `frontend/src/styles/ajustes.css`: `--muted` en `.admin-table th`
  y en `.admin-footer`
- [X] T045 [US9] Reconstruir `web` y ejecutar `verificar-panel-aa.mjs`. Comprobar en la API que
  ningún dato ha cambiado. Comparar las capturas: solo cambian los textos corregidos. Regresión:
  `verificar-panel.mjs`, `verificar-accesibilidad.mjs`, vitest, `typecheck`, `verificar-rutas` y
  `verificar-cierre`
- [X] T046 [US9] Actualizar `docs/referencia/DISCREPANCIAS.md` (P4), `docs/arquitectura.md`,
  `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Phase 3h: User Story 10 — Podio masculino, femenino y por categoría (P1)

**Goal**: sin filtros se destacan los 3 primeros chicos y las 3 primeras chicas de cada prueba;
con el filtro de sexo o de categoría, su podio. Cada fila del podio lleva una etiqueta junto al
nombre.

**Independent Test**: pytest de la consulta; `npx vitest run tests/podio.test.tsx`;
`verificar-podio.mjs --comparar capturas/podio-sexo-antes-012.json`.

- [X] T047 [P] [US10] Añadir a `backend/tests/test_consulta_clasificaciones.py` las pruebas del
  podio: por sexo, filtro de sexo, categoría, búsqueda, empate, sin sexo y sin puesto. Deben
  fallar antes del cambio.
- [X] T048 [P] [US10] Reescribir `frontend/tests/podio.test.tsx`: `rangosPodio`,
  `etiquetaPodio` y el render en modo cliente. Debe fallar antes del cambio.
- [X] T049 [US10] Reescribir `frontend/scripts/verificar-podio.mjs` con un oráculo que lee todas
  las páginas de la API, filtros y búsqueda. Tomar la referencia
  `capturas/podio-sexo-antes-012.json` y comprobar que `--comparar` falla con la versión previa.
- [X] T050 [US10] En `backend/app/services/clasificaciones.py`: `_podio` (`rank()` por sexo sobre
  el grupo filtrado) y `podium` en cada fila de `consultar`. Añadir `podium` al contrato
  `specs/006-clasificaciones-csv/contracts/api-clasificaciones.openapi.yaml`.
- [X] T051 [US10] En el frontend:
  - `rangosPodio`, `etiquetaPodio` y `podium` en `frontend/src/lib/classifications.ts`;
  - `ClassificationTable.tsx`: `podium` del servidor o `rangosPodio`, «Pos.» con la posición
    general y la etiqueta junto al nombre;
  - A-007 en `ajustes.css`: `.podium-label` en lugar de `.podium-medal`.
- [X] T052 [US10] Reconstruir `api` y `web` y ejecutar:
  - pytest completo, vitest, `typecheck` y `build`;
  - `verificar-podio.mjs --comparar`;
  - `verificar-clasificaciones`, `verificar-accesibilidad` y `verificar-panel-aa`;
  - capturas en `frontend/capturas/despues-podio-sexo-012`, comparadas con las de la US9;
  - `verificar-rutas`, `verificar-cierre` y `verificar-fotos`.

  Revisión visual a 360 y 1440 px, sin filtros y con «Femenino».
- [X] T053 [US10] Registrar la decisión P12 en `docs/referencia/DISCREPANCIAS.md` y actualizar
  `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Phase 4: Polish

- [X] T007 Regresión: vitest, `typecheck`, `build`, `verificar-rutas`, `verificar-cierre` y `verificar-galeria`. Actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`
- [X] T012 Regresión tras la US2 (pytest, `verificar-rutas`, `verificar-cierre` con la configuración local) y actualización de `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Dependencies & Execution Order

- **Orden**: T001 (referencia antes del cambio) → T002 → T003 → T004 → T005 → T006 → T007.
- **En paralelo [P]**: T002 junto a T001 (archivos distintos).
- **US3**: T013 (referencia antes del cambio) → T014 [P] → T015 → T016 → T017 → T018.
- **US4**: T019 (referencia antes del cambio) → T020 [P] → T021 → T022 → T023 → T024.
- **US5**: T025 [P] y T026 [P] (comprobaciones que fallan antes del cambio) → T027 → T028 → T029.
- **US6**: T030 (referencia antes del cambio) → T031 [P] → T032 → T033 → T034 → T035.
- **US7 y US8**: T036 (referencia antes del cambio) → T037 → T038 → T039 → T040 → T041.
- **US9**: T042 y T043 (auditoría y capturas antes del cambio) → T044 → T045 → T046.
- **US10**: T047 [P], T048 [P] y T049 (pruebas y referencia que fallan antes del cambio) → T050 →
  T051 → T052 → T053.

## Implementation Strategy

- **Alcance**: hasta ahora, las US1–US10 completas. Los próximos ajustes del propietario se
  añadirán como historias nuevas (US11…) de esta misma feature.
