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

## Phase 3: Polish

- [X] T007 Regresión: vitest, `typecheck`, `build`, `verificar-rutas`, `verificar-cierre` y `verificar-galeria`. Actualizar `docs/arquitectura.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Dependencies & Execution Order

- **Orden**: T001 (referencia antes del cambio) → T002 → T003 → T004 → T005 → T006 → T007.
- **En paralelo [P]**: T002 junto a T001 (archivos distintos).

## Implementation Strategy

- **Alcance**: esta entrega cubre la US1 completa. Los próximos ajustes del propietario se
  añadirán como historias nuevas (US2, US3…) de esta misma feature.
