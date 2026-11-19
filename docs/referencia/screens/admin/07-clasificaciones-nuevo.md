# Clasificaciones · crear

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/clasificaciones/nuevo` |
| Área | Administración |
| Referencia de código | `components/admin/ClassificationManager.tsx` / `ClassificationImport.tsx` |

## Objetivo

Crear una clasificación a partir del CSV de una carrera y una edición.

## Composición y contenido

- Formulario con título, edición y selector de carrera.
- Zona para seleccionar un CSV y enlace de descarga de la plantilla.
- Asignación de columnas detectadas, con corrección manual y campos obligatorios.
- Vista previa de las cinco primeras filas y botón «Usar estos resultados».
- Nombre del archivo y número de participantes preparados.
- Panel de publicación, estado borrador/publicado y botón «Guardar cambios».

El Dorsal Solidario no figura en el selector. El formulario no ofrece carga de PDF ni enlace externo de resultados.

## Datos y guardado

Colección `results[]`: ID estable, título, edición, `raceId`, nombre de carrera, `sourceFile`, `importedAt`, filas normalizadas y visibilidad. Se guarda como máximo un registro por carrera y edición. El servidor valida filas, dorsales únicos y carrera. La importación no se publica hasta guardar.

## Acciones y estados

- Seleccionar CSV → detectar separador/columnas → revisar vista previa → confirmar → guardar.
- Una importación pendiente bloquea el guardado hasta confirmarla o cancelarla.
- CSV vacío, cabeceras incompletas, fila incorrecta, dorsales repetidos y límites excedidos muestran error.
- Cancelar la importación conserva los participantes que ya había.
- Volver al listado mantiene las rutas independientes; un ID inexistente ofrece volver.
- Sesión caducada, fallo de servidor y conflicto de revisión conservan los estados de error del panel.
- La vista `/pantallas/admin…` permite revisar el diseño e importar un ejemplo sin persistencia.

## Criterios específicos

- No inventar posiciones, participantes ni tiempos.
- No duplicar el registro al guardar ni crear un segundo CSV para la misma carrera/edición.
- La clasificación comienza en borrador y requiere confirmar un CSV válido.
- Un publicado aparece como tabla en `/clasificaciones`; un borrador permanece privado.
- No perder el resto del contenido al guardar esta colección.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [contrato CSV](../../13_CLASIFICACIONES_CSV.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
