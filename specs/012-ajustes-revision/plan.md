# Implementation Plan: Ajustes de la revisión del propietario

**Branch**: `012-ajustes-revision` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

US1 (decisión P6): fotos siempre completas. Sin cambios de DOM, de esquema ni de API.

- Cada `<img>` de foto recibe la variable CSS `--foto` con su propia URL, mediante el helper
  `fondoFoto`.
- `ajustes.css` (A-004) cambia esos marcos a `object-fit: contain`, centrada. El fondo del propio
  `<img>` es la misma foto bajo un velo del verde de la paleta al 82 % y solo se ve en las franjas
  sobrantes.

Detalle en [research.md](research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 + React 19; CSS
**Primary Dependencies**: Vite; Playwright y `@axe-core/playwright` (verificación)
**Storage**: N/A
**Testing**: vitest (`fondoFoto`); Playwright (`verificar-fotos.mjs`, `verificar-accesibilidad.mjs`, capturas)
**Target Platform**: navegadores actuales (`object-fit` y variables CSS)
**Project Type**: aplicación web (solo frontend en esta historia)
**Performance Goals**: sin peticiones nuevas. El relleno reutiliza la imagen ya descargada (misma URL, en caché).
**Constraints**:
- Marcos con el mismo tamaño y posición.
- CSP: los estilos se aplican por CSSOM, sin `style=` en el HTML servido.
- Accesibilidad AA.
**Scale/Scope**: 9 imágenes públicas y 2 miniaturas del panel

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Cambio visual ordenado por el propietario (P6); marcos y diseño sin mover; capturas antes y después | ✅ |
| II | Sin cambios de persistencia | ✅ |
| III | Compatible con la CSP (CSSOM); el panel no cambia de comportamiento | ✅ |
| IV | URLs y recursos intactos | ✅ |
| V | vitest, Playwright (geometría de las fotos), axe y capturas | ✅ |
| VI | Sin datos inventados | ✅ |

Re-evaluación tras el diseño: sin cambios. ✅

## Project Structure

```text
frontend/src/lib/fotos.ts (nuevo) · frontend/tests/fotos.test.ts (nuevo)
frontend/src/components/Site.tsx · frontend/src/components/admin/Admin.tsx (style={fondoFoto(src)})
frontend/src/styles/ajustes.css (A-004)
frontend/scripts/verificar-fotos.mjs (nuevo)
docs/{arquitectura,ROADMAP,ESTADO_PROYECTO}.md
```

## Complexity Tracking

Sin violaciones.
