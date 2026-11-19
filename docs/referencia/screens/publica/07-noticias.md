# Noticias

| Propiedad | Definición |
|---|---|
| Ruta | `/noticias` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · News, NewsCards` |

## Objetivo

Consultar anuncios y avisos publicados de la organización.

## Composición y contenido

- Encabezado editorial e introducción.
- Tarjetas de portada, categoría, título y resumen; fecha cuando existe.
- Una sola noticia usa composición destacada horizontal en escritorio y vertical en móvil.

## Datos

`news[]` filtrado por `published`.

## Acciones y navegación

- Abrir `/noticias/:id` desde una tarjeta o «Leer noticia».

## Estados

- Sin noticias: mensaje de próximas novedades.
- Una noticia sin fecha no muestra una fecha inventada.
- Las noticias en borrador permanecen fuera del listado.

## Criterios específicos

- Conservar texto claro y fotografía real.
- Adaptar la tarjeta única y el mosaico a móvil.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
