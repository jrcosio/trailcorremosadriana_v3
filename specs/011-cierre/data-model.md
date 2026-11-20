# Data Model: Cierre para el lanzamiento (011)

Sin cambios de esquema ni migraciones. Las entidades de la spec son vistas sobre datos existentes:

## MetadatosPagina (derivado; respuesta de `GET /api/meta`)

| Campo | Origen | Reglas |
|---|---|---|
| `titulo` | Título de la noticia, el álbum o la prueba; «Clasificaciones {año}» | `{titulo} \| Trail Peñasagra`; escapado |
| `descripcion` | Resumen, frase del álbum o descripción de la prueba | Máximo 160 caracteres, cortada por palabra; escapada |
| `imagen` | Imagen del elemento | Absoluta (`PUBLIC_ORIGIN` + ruta) o `https://`; la general si falta |
| `canonica` | `PUBLIC_ORIGIN` + ruta pedida | Sin barra final |
| `tipo` | `article` (noticias) o `website` | — |

Solo para elementos publicados (los borradores se tratan como inexistentes).

## ArchivoHuerfano (derivado de `Archivo`)

| Campo | Regla |
|---|---|
| `Archivo.clave` | No aparece como `/media/<clave>` en ninguna fila de ninguna otra tabla |
| `Archivo.creado_en` | Anterior a ahora − `--horas` (24 por defecto) |

## CopiaSeguridad (archivos en `copias/`)

- `trail-AAAAMMDD-HHMMSS.dump`: `pg_dump` en formato *custom*.
- `media-AAAAMMDD-HHMMSS.tgz`: contenido de `/data/media`, cuando `ALMACENAMIENTO=local`.
