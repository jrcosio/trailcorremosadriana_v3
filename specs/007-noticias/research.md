# Research: Noticias (007)

- **R1 Modelo**: tabla `noticias` con `slug` único (el id del panel y de la URL), `titulo`,
  `categoria`, `fecha` (date, nula), `imagen`, `extracto`, `cuerpo`, `publicada`, `version`,
  `creado_en` y `actualizado_en`. Migración `0007_noticias`.
- **R2 Orden**: `fecha DESC NULLS FIRST, creado_en DESC`. Las noticias sin fecha (anuncios
  vigentes) van arriba.
- **R3 Endpoints**: `PUT /api/admin/noticias/{id}` (crea o actualiza con `version`; 409) y
  `DELETE /api/admin/noticias/{id}?version=N`, con la misma pauta que las pruebas (004). El panel
  las usa a través de `persistencia.ts` (sección `news`).
- **R4 Contrato**: `news[]` = `{id, title, category, date (AAAA-MM-DD o ''), image, excerpt, body,
  published}`, más `version` en la variante privada. La pública solo incluye las publicadas.
- **R5 Importación**: `importar-inicial` crea las noticias si la tabla está vacía. Toma la de la
  semilla y la de producción `backend/seed/noticias/2026-07-13-gracias-trail-2026.json` (contenido
  público sin datos personales). La imagen se copia en
  `frontend/public/reused/noticias/gracias_2026.webp`. El orden de alta es primero «gracias» y
  después «proxima-edicion».
- **R6 Fecha**: se acepta un día `AAAA-MM-DD` o un ISO del que se toma la fecha, y vacío. El
  formulario del panel usa `type=date`.
