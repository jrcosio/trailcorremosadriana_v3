# Galería de imágenes

| Propiedad | Definición |
|---|---|
| Ruta | `/galeria` |
| Área | Web pública |
| Referencia de código | `components/Site.tsx · Gallery sin id` |

## Objetivo

Explorar álbumes por edición.

## Composición y contenido

- Encabezado de recuerdos de la carrera.
- Filtros de todas las ediciones y años disponibles.
- Tarjetas con portada, año, título y acceso al álbum.

## Datos

`albums[]` publicados. Enlaces históricos incluidos para 2026, 2025 y 2024.

## Acciones y navegación

- Filtrar por año; abrir `/galeria/:id`.

## Estados

- Años con álbumes publicados.
- No asignar las portadas reutilizadas a un año como si esa procedencia estuviera verificada.
- Si no hay álbumes, mostrar un estado vacío útil.

## Criterios específicos

- Las fotos del propietario no se sustituyen por imágenes genéricas.
- El filtro no altera la URL de los álbumes ni pierde enlaces históricos.

Aplicar también [estilo visual](../../02_ESTILO_VISUAL.md), [flujos](../../06_FLUJOS_Y_REGLAS.md) y [criterios globales](../../09_CRITERIOS_ACEPTACION.md).
