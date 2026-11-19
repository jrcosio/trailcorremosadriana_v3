# Clasificaciones

| Propiedad | Definición |
|---|---|
| Ruta | `/clasificaciones` |
| Área | Web pública |
| Referencia de código | `components/Results.tsx` / `ClassificationTable.tsx` |

## Objetivo y composición

Consultar la tabla oficial de cada carrera desde los datos de su CSV. Encabezado deportivo, filtros por edición y carrera, título de cada clasificación y número de participantes. El Dorsal Solidario no aparece entre las carreras ni en los resultados.

Cada tabla muestra posición, dorsal, participante y tiempo; categoría, club, sexo y estado aparecen si tienen contenido. Búsqueda por nombre, dorsal o club; filtros por categoría y sexo; paginación de 50 participantes. El podio tiene acento naranja y las filas alternan fondo blanco/verde suave. El desplazamiento horizontal queda dentro de la tabla.

## Datos y acciones

`results[]` publicados con `rows[]`, ya normalizados desde el CSV. Filtrar no recalcula el puesto general; conserva el valor oficial. Los no clasificados van al final con estado y sin puesto inventado. No se abre un PDF o enlace externo para consultar los resultados.

## Estados y aceptación

- Sin resultados oficiales: mensaje de publicación futura, sin datos de ejemplo.
- Sin coincidencias: mensaje y filtros editables.
- Los borradores y los antiguos enlaces sin datos CSV no aparecen.
- Los nombres se buscan sin distinguir mayúsculas ni acentos.
- Un nuevo CSV guardado reemplaza la tabla anterior del mismo registro.
- Tablas semánticas, cabeceras, región enfocables y controles etiquetados.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [contrato CSV](../../13_CLASIFICACIONES_CSV.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
