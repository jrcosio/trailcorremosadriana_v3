# Semilla de contenido inicial

`contenido_inicial.json` es el contenido público de referencia que sirve el adaptador
transitorio `GET /api/content` (feature 001). Las features 004–010 trasladan cada sección a
tablas de PostgreSQL y la importan desde aquí.

## Procedencia

- Generado el 2026-11-19 volcando `seed` de `lib/data.ts` de la propuesta aprobada
  (`Trail_Penasagra_Desarrollo/proyecto`, commit fuente `9e0768887bcdfac5c361a4c4256ff59d76b5c296`).
  Es idéntico a `frontend/src/lib/data.ts`, que el frontend usa como respaldo.
- Comparado con la exportación publicada `contenido/contenido-publicado.json` (revisión pública 7).

## Diferencias con la exportación publicada

La comparación campo a campo solo encontró los datos de prueba documentados en
`docs/referencia/DISCREPANCIAS.md`, que **no** se incluyen:

| Ref. | Campo | Exportación publicada | Semilla |
|---|---|---|---|
| D1 | `settings.edition` / `settings.date` | `2028` / `2027-07-10T07:00:00.000Z` | `2027` / vacío (decisión del propietario P1) |
| D2 | `races[trail-27k].image` | `/media/2f25827b-….png` (silueta subida por error) | `/reused/img/trail_inscripciones.webp` |
| D3 | `collaborators` | colaborador de prueba «boc» | vacío |
| D4 | `regulation` | termina con «PRUEBA / Pues eso esto es una prueba.» | sin ese párrafo |

No hay otras diferencias editoriales: textos, carreras, noticia, álbumes, patrocinadores y
ajustes coinciden.

## Datos que son referencia y no oficiales

- Carreras, precios y horarios: referencia de la edición 2026.
- Enlaces de inscripción y de pago solidario: vacíos hasta que el propietario los facilite.
- Webs de patrocinadores: vacías (no se infieren dominios).
