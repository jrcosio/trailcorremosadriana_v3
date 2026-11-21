# Implementation Plan: Ajustes de la revisión del propietario

**Branch**: `012-ajustes-revision` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

US1 (decisión P6): fotos siempre completas. Sin cambios de DOM, de esquema ni de API.

- Cada `<img>` de foto recibe la variable CSS `--foto` con su propia URL, mediante el helper
  `fondoFoto`.
- `ajustes.css` (A-004) cambia esos marcos a `object-fit: contain`, centrada. El fondo del propio
  `<img>` es la misma foto bajo un velo del verde de la paleta al 82 % y solo se ve en las franjas
  sobrantes.

US2: despliegue en la MV de la web anterior (`www`, HSTS, orígenes en *punycode*, guía de
migración y de acceso al panel).

US3 (decisión P7): logotipo nuevo en la cabecera pública.

- Las variantes WebP de 480 y 720 px de ancho se generan desde el PNG del propietario, recortadas
  a su contenido transparente.
- La cabecera usa un `<img>` con `srcset`/`sizes` dentro del mismo enlace a la portada.
- `ajustes.css` (A-005) fija la altura del logotipo en cada tramo de la cabecera. Esa altura cabe
  en la cabecera y en el ancho de la marca anterior. El enlace conserva ese ancho, así que nada más
  se mueve.
- La barra lateral del panel conserva la marca blanca.

US4 (decisión P8): el logotipo también en el pie.

- Se usa una versión en negativo: la tinta oscura en blanco y el naranja conservado. Sus variantes
  WebP de 480 y 720 px se generan del mismo PNG y con el mismo recorte.
- Un componente `Logo` sirve a la cabecera y al pie; `Brand` se elimina.
- `ajustes.css` (A-006) da al logotipo del pie el ancho de la marca anterior, 233 px, o el de su
  columna si es menor. Su alto sale de la proporción.
- Las demás columnas del pie no se mueven.

US5 (decisión P9): la línea inferior del pie dice «Hecho por la Escuela Hacker Cosío» en lugar de
«Hecho con pasión por JR BLANCO · Hackers Cosío». Es texto sin enlace, con el estilo de la línea;
sin CSS nuevo.

US6 (decisión P10): podio destacado en las clasificaciones.

- Las filas con puesto 1, 2 y 3 llevan `podium podium-N` y el número va dentro de una medalla.
- `ajustes.css` (A-007) les da un fondo suave de oro, plata y bronce, con una franja y la medalla
  en el mismo color más intenso.
- Ni las filas cambian de alto ni la tabla de ancho.

US7: la barra lateral del panel se desplaza en ventanas bajas (`overflow-y: auto` y
`overscroll-behavior: contain`). La opción abierta queda a la vista y, con el menú de móvil
abierto, la página no se desborda.

US8 (decisión P11): logotipo oficial en negativo en la barra lateral, con «ADMINISTRACIÓN»
debajo, y en la pantalla de acceso. Lo sirve un componente compartido, `LogoImg`
(`components/Logo.tsx`).

US9 (decisión P4 aplicada al panel): con la sesión iniciada, las cabeceras de las tablas de
listados y el pie del panel pasan al gris de texto secundario de la paleta, `--muted`
(`ajustes.css` A-009). Una auditoría axe de todo el panel, sin escrituras reales, da 0
incumplimientos.

US10 (decisión P12): podio por sexo y por categoría.

- La consulta pública devuelve `podium` (1–3) por fila: un podio por sexo, o el de la categoría
  filtrada, sin contar la búsqueda. El panel lo calcula con `rangosPodio`.
- La tabla muestra una etiqueta junto al nombre («1.ª mujer») en lugar de la medalla, y «Pos.»
  conserva la posición general.

Detalle en [research.md](research.md) (R4, R5, R6, R7, R8, R9 y R10).

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
**US3**: `Site.tsx` (cabecera), `ajustes.css` A-005 y 2 archivos WebP nuevos en
`public/reused/logos/`. Sin cambios de API ni de datos. Verificación de la geometría de la
cabecera con Playwright, con una referencia tomada antes del cambio.
**US4**: `Site.tsx` (pie), `ajustes.css` A-006 y 2 archivos WebP nuevos
(`logo_pie-{480,720}.webp`). La geometría de la cabecera y del pie se verifica contra una
referencia nueva.
**US5**: `Site.tsx` (`Footer`). Prueba vitest nueva (`tests/pie.test.tsx`) y comprobación de la
línea inferior del pie en `verificar-logo.mjs`.
**US6**: `ClassificationTable.tsx` y `ajustes.css` A-007. Prueba vitest nueva
(`tests/podio.test.tsx`) y `scripts/verificar-podio.mjs`, con una referencia tomada antes del
cambio.
**US7 y US8**: `Admin.tsx` (barra lateral y acceso), `components/Logo.tsx` (nuevo, compartido con
`Site.tsx`) y `ajustes.css` A-008. `scripts/verificar-panel.mjs` (nuevo, con credenciales y
referencia previa).
**US9**: `ajustes.css` A-009 y `scripts/verificar-panel-aa.mjs` (nuevo, con credenciales y las
escrituras interceptadas).
**US10**:
- Backend: `services/clasificaciones.py`, con `_podio` y `podium` en la consulta pública, y
  pytest.
- Frontend: `lib/classifications.ts` (`rangosPodio`, `etiquetaPodio`),
  `ClassificationTable.tsx` y `ajustes.css` A-007.
- Pruebas y contrato: `tests/podio.test.tsx`, `scripts/verificar-podio.mjs` y el contrato de la
  006.

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Cambio visual ordenado por el propietario (P6); marcos y diseño sin mover; capturas antes y después | ✅ |
| I (US3) | Cambio de marca ordenado por el propietario (P7). La cabecera conserva su altura y la posición de la navegación y de «INSCRIPCIONES»; el título literal «TRAIL PENASAGRA» de la portada no cambia. Capturas antes y después | ✅ |
| IV (US3) | Procedencia del logotipo en `docs/PROCEDENCIA_RECURSOS.md` | ✅ |
| I (US4) | Cambio de marca ordenado por el propietario (P8). La cabecera no cambia y las columnas 2.ª–4.ª del pie conservan su posición horizontal. Solo baja el resto de la primera columna, lo que crece el logotipo. Capturas antes y después | ✅ |
| IV (US4) | Procedencia de la versión en negativo (derivada de `new_logo.png`) en `docs/PROCEDENCIA_RECURSOS.md` | ✅ |
| I (US5) | Cambio de texto ordenado por el propietario (P9); mismo estilo y nada más se mueve. Capturas antes y después | ✅ |
| VI (US5) | La frase va sin enlace: no hay dirección aprobada y no se inventan enlaces | ✅ |
| I (US6) | Cambio visual ordenado por el propietario (P10), con los colores a elección del equipo; filas y tabla con 0 px de diferencia. Capturas antes y después | ✅ |
| VI (US6) | El podio es el puesto publicado; no se calculan podios por sexo ni por categoría | ✅ |
| I (US7) | Corrige un fallo sin cambiar el diseño: con altura suficiente la barra lateral se ve igual | ✅ |
| III (US7) | «Cerrar sesión» vuelve a estar al alcance en cualquier ventana | ✅ |
| I (US8) | Cambio de marca ordenado por el propietario (P11). La barra, el contenido y el formulario no cambian en horizontal. Capturas antes y después | ✅ |
| I (US9) | Solo cambia el color de dos textos, con un tono de la paleta, por la decisión P4; capturas antes y después | ✅ |
| II (US9) | La auditoría intercepta las escrituras y no cambia ningún dato (comprobado en la API) | ✅ |
| I (US10) | Cambio visual ordenado por el propietario (P12) con la presentación que eligió; fondos y franjas iguales | ✅ |
| IV (US10) | Contrato de la consulta pública ampliado (`podium`), compatible: solo añade un campo | ✅ |
| VI (US10) | El podio sale del puesto, el sexo y la categoría publicados; no se inventa nada | ✅ |
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
# US3
frontend/public/reused/logos/logo_cabecera-{480,720}.webp (nuevos)
frontend/src/components/Site.tsx (cabecera) · frontend/src/styles/ajustes.css (A-005)
frontend/scripts/verificar-logo.mjs (nuevo)
docs/{PROCEDENCIA_RECURSOS,referencia/DISCREPANCIAS}.md
# US4
frontend/public/reused/logos/logo_pie-{480,720}.webp (nuevos)
frontend/src/components/Site.tsx (Logo en cabecera y pie) · frontend/src/styles/ajustes.css (A-006)
frontend/scripts/verificar-logo.mjs (pie, contraste y densidad del pie)
# US5
frontend/src/components/Site.tsx (Footer) · frontend/tests/pie.test.tsx (nuevo)
frontend/scripts/verificar-logo.mjs (línea inferior del pie)
# US6
frontend/src/components/ClassificationTable.tsx · frontend/src/styles/ajustes.css (A-007)
frontend/tests/podio.test.tsx (nuevo) · frontend/scripts/verificar-podio.mjs (nuevo)
# US7 y US8
frontend/src/components/Logo.tsx (nuevo) · frontend/src/components/Site.tsx (Logo)
frontend/src/components/admin/Admin.tsx (barra lateral y acceso) · frontend/src/styles/ajustes.css (A-008)
frontend/scripts/verificar-panel.mjs (nuevo) · frontend/scripts/verificar-logo.mjs (panel)
# US9
frontend/src/styles/ajustes.css (A-009) · frontend/scripts/verificar-panel-aa.mjs (nuevo)
# US10
backend/app/services/clasificaciones.py (_podio) · backend/tests/test_consulta_clasificaciones.py
frontend/src/lib/classifications.ts · frontend/src/components/ClassificationTable.tsx · frontend/src/styles/ajustes.css (A-007)
frontend/tests/podio.test.tsx · frontend/scripts/verificar-podio.mjs
specs/006-clasificaciones-csv/contracts/api-clasificaciones.openapi.yaml (podium)
```

## Complexity Tracking

Sin violaciones.
