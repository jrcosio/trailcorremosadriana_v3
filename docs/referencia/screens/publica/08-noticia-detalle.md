# Detalle de noticia

| Propiedad | Definición |
|---|---|
| Ruta | `/noticias/:id` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · News con id` |

## Objetivo

Leer el contenido completo de un anuncio.

## Composición y contenido

- Encabezado con categoría, título y fecha o identificación de la organización.
- Volver a noticias, imagen y cuerpo con párrafos.
- El contenido actual es texto plano separado por líneas; no hay editor HTML enriquecido.

## Datos

Noticia publicada identificada por `id`; ejemplo incluido: `/noticias/proxima-edicion`.

## Acciones y navegación

- Volver al listado; navegar a otras secciones desde la cabecera/pie.

## Estados

- ID inexistente o borrador: página no encontrada sin revelar contenido.
- Imagen no configurada: se utiliza la referencia de paisaje existente.

## Criterios específicos

- Conservar párrafos y no ejecutar HTML introducido como texto.
- Revisar metadatos por noticia y estado HTTP en la evolución del router.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
