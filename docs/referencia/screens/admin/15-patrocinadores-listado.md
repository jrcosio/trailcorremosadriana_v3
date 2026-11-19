# Patrocinadores · listado

| Propiedad | Definición |
|---|---|
| Ruta | `/admin/patrocinadores` |
| Área | Administración |
| Referencia de código | `components/admin/Admin.tsx · Collection` |

## Objetivo

Localizar, crear, editar o eliminar cada patrocinador.

## Composición y contenido

- Encabezado de sección y botón de añadir.
- Buscador por título/nombre y filtro de todos/publicados/borradores.
- Tabla con miniatura cuando existe, título, detalle, estado y acciones.
- Conteo de elementos y estado vacío; confirmación antes de eliminar.

## Datos

Colección privada `sponsors[]`. Conservar logos reales y gran tamaño público. No inventar webs; la imagen no debe recortarse.

## Acciones y navegación

- Añadir → `/admin/patrocinadores/nuevo`.
- Editar → `/admin/patrocinadores/:id`.
- Eliminar pide confirmación y guarda con revisión; cancelar no modifica datos.

## Estados

- Cargando, vacío, sin coincidencias, confirmación, guardando, error y conflicto.
- El borrado actual retira el registro del documento; no hay papelera.

## Criterios específicos

- No mostrar éxito hasta respuesta correcta del servidor.
- No borrar al abrir la confirmación.
- Después de eliminar, una nueva lectura pública ya no muestra el registro.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
