# Contrato: metadatos de página y respuestas por ruta (feature 011)

## `GET /api/meta?ruta=<ruta>` (público)

- Siempre `200`, `text/plain; charset=utf-8` y `Cache-Control: no-store`.
- **Página publicada**: el cuerpo empieza por `<!-- meta -->` y sigue con las etiquetas, todas con
  los valores escapados:
  - `<title>`;
  - `<meta name="description">`;
  - `og:type`, `og:site_name`, `og:locale`, `og:title`, `og:description`, `og:image` y `og:url`;
  - `twitter:card`, `twitter:title`, `twitter:description` y `twitter:image`;
  - `<link rel="canonical">`.
- **Página inexistente o no publicada**: el cuerpo es exactamente `no-encontrada`.
- **Rutas con metadatos propios**: `/noticias/{id}`, `/galeria/{id}`, `/carreras/{id}`,
  `/recorridos/{id}` y `/clasificaciones/{año}`.

## Respuestas por ruta (a través de Caddy)

| Ruta | Estado | HTML |
|---|---|---|
| Rutas públicas estáticas (`/`, `/carreras`, …) | 200 | El suyo, generado en el build (sin cambios) |
| Detalle publicado | 200 | Plantilla con los metadatos propios |
| Detalle inexistente o no publicado, ruta desconocida, más de 2 segmentos | 404 | `404.html` (noindex); el SPA muestra «Este sendero no está en el mapa.» |
| Detalle con la API caída | 200 | Metadatos genéricos; el SPA muestra el aviso de respaldo |
| `/admin`, `/admin/*` | 200 | Sin cambios (noindex) |
| `/pantallas`, `/pantallas/*` | 404 si `PANTALLAS≠si`; 200 si `si` | `404.html` / sin cambios |

## Errores genéricos de la API

- `404` sin detalle propio: `{"error":"No encontrado."}`.
- `405`: `{"error":"Método no permitido."}`.

## CLI `python -m app.cli limpiar-archivos [--horas N] [--borrar]`

- Lista los huérfanos (clave, tamaño y fecha) y su total.
- `--borrar` pide escribir `BORRAR`; con cualquier otra respuesta sale con código 1 sin tocar nada.
