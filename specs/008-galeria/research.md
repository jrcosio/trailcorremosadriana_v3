# Research: Galería (008)

- **R1 Modelo**: tablas `albumes` (`slug`, `titulo`, `anio`, `portada`, `url_externa`,
  `publicado`, `orden`, `version`) y `fotografias` (`album_id` con FK CASCADE, `imagen`, `alt`,
  `orden`). Migración `0008_galeria`.
- **R2 Contrato**: `albums[]` = `{id, title, year, image, url, photos: string[], photoAlts:
  string[], published}`, más `version` en la variante privada. `photos` sigue siendo una lista de
  URL, porque es lo que el panel aprobado edita. `photoAlts` es un campo nuevo y paralelo que usa
  la web pública.
- **R3 Endpoints**: `PUT` y `DELETE` en `/api/admin/albumes/{id}`. El `PUT` sustituye la lista
  de fotos en la misma transacción, con el orden del índice y el `alt` por defecto. El panel los
  usa mediante `recursoSimple` en `persistencia.ts`.
- **R4 Orden público**: `anio DESC, orden, id`. Un álbum nuevo toma `orden = max + 1`.
- **R5 Visor**: en `Site.tsx`:
  - el foco se atrapa con Tab y Mayús+Tab entre los tres botones del diálogo;
  - al cerrar, el foco vuelve a la miniatura que abrió el visor;
  - las fotos usan `alt={a.photoAlts?.[i] ?? …}`.

  Sin cambios de CSS ni de marcado visible.
- **R6 Importación**: los 3 álbumes de la semilla, sin fotos propias, si la tabla está vacía.
