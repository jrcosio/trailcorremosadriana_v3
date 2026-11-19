# Clasificaciones · listado

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/clasificaciones` |
| Área | Administración |
| Referencia de código | `components/admin/ClassificationManager.tsx` |

## Objetivo y composición

Gestionar una clasificación CSV por carrera y edición. Buscador por título, carrera o edición; filtro de publicación; tabla con título, archivo CSV, carrera/edición, número de participantes, estado y acciones de editar/eliminar. El Dorsal Solidario se excluye de este listado.

## Acciones

- Añadir → `/admin/clasificaciones/nuevo`.
- Editar → `/admin/clasificaciones/:id`; desde aquí se sustituye el CSV completo.
- Eliminar → confirmación; solo tras confirmar y recibir éxito del servidor se retira el registro y sus filas. No hay papelera.

## Datos y estados

Colección privada `results[]`, incluyendo borradores. Los enlaces heredados pendientes de CSV muestran «Pendiente de importar CSV» y no se representan en público. Contemplar vacío, sin coincidencias, guardando, error, sesión caducada y conflicto de revisión.

## Aceptación

No mostrar clasificación del Dorsal Solidario, no duplicar carrera/edición y no perder otras colecciones. Cancelar la confirmación no elimina datos. Las vistas de diseño no modifican producción.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [contrato CSV](../../13_CLASIFICACIONES_CSV.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
