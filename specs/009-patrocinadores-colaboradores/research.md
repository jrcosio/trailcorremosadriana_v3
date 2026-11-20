# Research: Patrocinadores y colaboradores (009)

- **R1 Modelo**: tabla única `entidades` con `tipo` CHECK (`patrocinador`, `colaborador`), `slug`
  único por tipo, `nombre`, `logo`, `web`, `orden`, `publicada`, `version` y `creado_en`
  (DOC 14: «same model, separate sections»). Migración `0009_entidades`.
- **R2 Endpoints**: `PUT` y `DELETE` en `/api/admin/entidades/{seccion}/{id}`, con
  `seccion ∈ {patrocinadores, colaboradores}`. La sección de la ruta fija el tipo: una entidad no
  puede cambiar de sección. En el panel se usa `recursoSimple` para `sponsors` y `collaborators`.
- **R3 Contrato**: `{id, name, image, url, order, published}`, más `version` en la variante
  privada. Orden: `orden, creado_en, id`.
- **R4 Importación**: los 8 patrocinadores de la semilla, si la tabla está vacía.
