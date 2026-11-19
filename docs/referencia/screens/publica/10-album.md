# Detalle de álbum

| Propiedad | Definición |
|---|---|
| Ruta | `/galeria/:id` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Gallery con id` |

## Objetivo

Ver fotos propias y conservar el acceso al álbum externo original.

## Composición y contenido

- Encabezado con título y edición y enlace de vuelta.
- Con fotos propias: cuadrícula de imágenes ampliables.
- Sin fotos propias: portada y botón explícito al álbum de Google Fotos.
- Si coexisten ambas fuentes, ofrecer también el álbum original.

## Datos

`albums[]`: `photos`, `image`, `year`, `url`, `title`. Ejemplo: `/galeria/edicion-2026`.

## Acciones y navegación

- Ampliar foto; anterior/siguiente; cerrar con botón o Escape.
- Abrir el álbum externo cuando existe.

## Estados

- Sin fotos propias no se finge una importación.
- ID no publicado/inexistente no muestra fotos de un borrador.
- Gestionar imagen rota o conexión fallida sin bloquear el resto.

## Criterios específicos

- Revisar teclado y confinamiento/restauración de foco del visor antes de cerrar accesibilidad.
- Conservar transparencia y proporción de archivos pertinentes.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
