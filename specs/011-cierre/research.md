# Research: Cierre para el lanzamiento (011)

## R1 404 reales y metadatos de detalle

**Experimento** (caddy:2.11-alpine, 2026-11-20). Una plantilla con `httpInclude` hacia un
`reverse_proxy`, `httpError 404` y `file_server { status 404 }` funcionan como se esperaba.
Si el subrecurso responde 404 o falla, `httpInclude` provoca un error de plantilla o incrusta la
página de error. Por eso:

- **`GET /api/meta?ruta=…` responde siempre 200 en `text/plain`.** El cuerpo es:
  - para una página publicada: el marcador `<!-- meta -->` seguido de las etiquetas, con los
    valores escapados;
  - para una página inexistente: `no-encontrada`.
- **La plantilla** (`plantilla.html`, generada en el build a partir de `index.html`):
  - `no-encontrada` → `httpError 404`;
  - respuesta que empieza por el marcador → la incluye;
  - cualquier otra (API caída: respuesta de `handle_errors`) → metadatos genéricos.
- **Caddy**:
  - Las rutas con HTML estático siguen igual (`{path}/index.html`).
  - El resto pasa por la plantilla (`templates`).
  - `handle_errors` en rutas que no son de la API: si es 404, sirve `404.html` (noindex) con
    estado 404; si es un 5xx de la plantilla, sirve `app.html` con 200 (FR-004).
- **Rutas con metadatos propios**:
  - `/noticias/{id}`, `/galeria/{id}`, `/carreras/{id}` y `/recorridos/{id}` publicados;
  - `/clasificaciones/{año}` si hay alguna clasificación publicada de ese año.
- **Siempre 404**: más de dos segmentos; identificadores fuera de `^[A-Za-z0-9_-]{1,100}$`.
- **Valores de los metadatos**:
  - Título: «{título} | Trail Peñasagra».
  - Descripción: resumen de la noticia; «Fotografías de {álbum} ({año}).»; descripción de la
    prueba (máximo 160 caracteres, cortada por palabra).
  - Imagen: absoluta con `PUBLIC_ORIGIN` si empieza por `/`; la general de la web si no hay.
  - Canónica: `PUBLIC_ORIGIN` + ruta. `og:type` es `article` en noticias y `website` en el resto.
- **Errores genéricos de la API**: en `error_http`, los 404 y 405 sin detalle propio (frase
  estándar en inglés) se traducen a «No encontrado.» y «Método no permitido.».

*Alternativa descartada*: que la API sirva el HTML completo (ver Complexity Tracking del plan).

## R2 Accesibilidad y móvil

- **Revisión**: `@axe-core/playwright` 4.10.2 con las etiquetas `wcag2a`, `wcag2aa`, `wcag21a` y
  `wcag21aa`. Hallazgos previos: `color-contrast` (botón naranja 3,52:1; dos textos del bloque
  solidario) y `link-in-text-block` (pie).
- **Correcciones en `ajustes.css`** (decisión P4):
  - `.button` sin `secondary`/`light`: `#b64b24`, y al pasar por encima `#9a3d1c`.
  - `.donation-eyebrow` y `.donation-copy>p`: `#fff`.
  - `.footer-bottom a`: subrayado.
- **Cabecera a 320/340 px**: se ajusta en `ajustes.css` con `@media (max-width:359px)`, sin tocar
  los anchos de aceptación (≥ 360 px).
- **Verificación**: `scripts/verificar-accesibilidad.mjs` (axe a 360 y 1440 px en todas las rutas
  públicas, un detalle de cada tipo, la 404 y el acceso al panel; desbordamiento a 6 anchos) y
  capturas antes y después para confirmar que solo cambian los elementos de P4.

## R3 Copias, restauración y despliegue independiente

- **`infra/scripts/verificar-copia.sh`**:
  1. ejecuta `backup.sh`;
  2. calcula las huellas: `md5` de cada tabla ordenada por su texto y `sha256` de cada archivo de
     `media`;
  3. hace un cambio controlado: modifica `configuracion.telefono` y **borra** un archivo
     existente de `media`, que la restauración debe devolver (prueba más estricta que añadir un
     archivo nuevo, porque `restore.sh` añade y sobrescribe pero no borra);
  4. ejecuta `restore.sh` con «RESTAURAR»;
  5. vuelve a calcular las huellas y las compara.

  (Implementación final: no se crean filas ni archivos de prueba que haya que limpiar después.)
- **`restore.sh`**: se mantiene la confirmación escrita.
- **Producción**:
  - el Caddyfile usa `{$SITE_ADDRESS::80}`; con un dominio, Caddy obtiene HTTPS automáticamente;
  - `compose.produccion.yaml` publica 80/443 y fija `ENTORNO=produccion`, `COOKIE_SECURE=true`,
    `PANTALLAS=no` y `SITE_ADDRESS`.
- **Ensayo**: clon limpio de la rama en una carpeta temporal, `.env` propio
  (`COMPOSE_PROJECT_NAME=trail-ensayo`, `WEB_PORT=8090`, secretos aleatorios), pasos de
  `docs/operacion.md`, restauración de la copia, comprobaciones y `down -v` **solo** del proyecto
  `trail-ensayo`.
- **R2**: copia de objetos con el versionado o la réplica del bucket; se documenta.

## R4 CSP y `/pantallas`

- **CSP por defecto de Caddy** (`?Content-Security-Policy`, que no pisa la de `/media`):
  - `default-src 'self'`; `script-src 'self'`; `style-src 'self'`; `img-src 'self' data: https:`;
    `font-src 'self'`; `connect-src 'self'`;
  - `frame-src https://es.wikiloc.com https://www.wikiloc.com`;
  - `object-src 'none'`; `base-uri 'self'`; `form-action 'self'`; `frame-ancestors 'self'`.
  - React aplica los estilos por CSSOM, que la CSP no bloquea.
  - Verificación: recorrido con escucha de violaciones (`securitypolicyviolation` y consola).
- **`/pantallas`**: `PANTALLAS` es una variable de entorno de `web` (`no` por defecto en
  `compose.yaml`, `si` en `compose.dev.yaml`). Con `PANTALLAS ≠ si`, Caddy responde 404
  (`error 404`) en `/pantallas` y `/pantallas/*`. `robots.txt` conserva el `Disallow`.

## R5 Fuentes

- Conversión TTF → WOFF2 con `fontTools` (`ttLib.woff2 compress`), que no pierde información en
  los contornos.
- Los nombres de archivo se mantienen (`.woff2`) y `format('truetype')` pasa a `format('woff2')`.
- Licencias OFL: la conversión de formato no crea una «Modified Version» (OFL FAQ); se conservan
  las licencias.
- Verificación: mismas capturas píxel a píxel (salvo los elementos de P4) y peso antes y después.

## R6 Limpieza

- **`python -m app.cli limpiar-archivos [--horas 24] [--borrar]`**:
  - Huérfano: archivo de `archivos` con `creado_en` anterior a ahora − horas y cuya clave no
    aparece como `/media/<clave>` en el texto de ninguna fila de ninguna tabla (salvo `archivos`).
    Se recorren todas las tablas con `SELECT t::text`, así que también cuentan los borradores y
    los campos futuros.
  - Sin `--borrar`, solo lista. Con `--borrar`, pide escribir «BORRAR» y elimina el objeto del
    almacenamiento y la fila.
- **Código sin uso**: `tsc --noUnusedLocals --noUnusedParameters` (iconos sin uso en `Site.tsx`,
  `revision` en `Admin.tsx`) y `vulture` (`resto` en `media.py`).
- **Pruebas**: `httpx` → `httpx2==2.16.0` en el grupo dev (Starlette lo recomienda; versión
  publicada hace más de dos semanas).
