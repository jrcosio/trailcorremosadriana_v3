# Arquitectura

Estado a 2026-11-20 (features 001–011). Las decisiones detalladas y sus alternativas están en el
`research.md` de cada feature (`specs/NNN-*/`). Operación y despliegue: `docs/operacion.md`.

## Procesos

```text
Navegador ──► web (Caddy 2.11, :80 → publicado en WEB_PORT)
                ├── /api/*, /media/*  ──► api (FastAPI, :8000, red interna)
                │                           └── db (PostgreSQL 17, red interna, volumen pgdata)
                └── resto: frontend/dist (HTML por ruta + SPA)
```

| Servicio | Imagen | Responsabilidad | Puertos |
|---|---|---|---|
| `web` | `frontend/Dockerfile` (Node 22 build → `caddy:2.11-alpine`) | Sirve la web y hace de proxy de `/api` y `/media` (mismo origen) | `WEB_PORT` (8080) |
| `api` | `backend/Dockerfile` (`python:3.13-slim` + uv) | API, validación, permisos, contenidos | ninguno (solo red interna) |
| `db` | `postgres:17-alpine` | Persistencia relacional | ninguno (solo red interna) |

`compose.dev.yaml` publica `api` y `db` solo en `127.0.0.1` para desarrollo local, activa
`/pantallas` (`PANTALLAS=si`) y define `api-test` (pytest contra PostgreSQL real).
`compose.produccion.yaml` (features 011 y 012):

- publica 80/443 con HTTPS automático para `SITE_ADDRESS`;
- fija `COOKIE_SECURE=true`, `ENTORNO=produccion` y `PANTALLAS=no`;
- exige los secretos sin valores por defecto;
- monta `infra/caddy/redireccion-www.caddy`, que el Caddyfile importa desde
  `/etc/caddy/sitios/*.caddy`: `www.<dominio>` → dominio principal con 301.

Todas las respuestas llevan `Strict-Transport-Security`. Los orígenes del panel se normalizan a
*punycode* (`normalizar_origen`), así que un dominio con «ñ» funciona aunque la configuración lo
escriba con «ñ». Guía de despliegue y migración desde la web anterior: `docs/operacion.md`,
secciones 12 y 13.

## Repositorio

| Carpeta | Contenido |
|---|---|
| `frontend/` | SPA React 19 + TypeScript + Vite 8. Componentes y estilos reutilizados de la propuesta aprobada sin cambios visuales |
| `backend/` | FastAPI (`app/api`, `app/core`, `app/schemas`, `app/services`), Alembic (`alembic/`), semilla (`seed/`) y pruebas (`tests/`) |
| `infra/` | `caddy/Caddyfile` y scripts de operación (`scripts/`) |
| `docs/` | Documentación del proyecto y `referencia/` (documentación aprobada copiada) |
| `specs/` | Especificaciones Spec Kit por feature |
| `datos_iniciales/` | Fuentes de referencia de solo lectura (ignoradas por Git y Docker) |

Decisión: estructura en la raíz (`frontend/`, `backend/`, `infra/`) según el prompt de
desarrollo, en lugar del `proyecto/…` sugerido por la DOC 14 (no existe ese nivel aquí). Cada
Dockerfile vive junto a su componente para que el contexto de build no incluya el resto del
repositorio.

## Frontend

- Vite + React SPA. `src/main.tsx` renderiza `<Site path={location.pathname}>`. Se conserva el
  router interno de la propuesta, por `path` y con enlaces `<a>` de recarga completa.
- Se eliminó todo lo ligado a Vinext/Cloudflare Workers: `vinext`, `wrangler`, `@cloudflare/*`,
  `worker/`, route handlers, D1/drizzle, conectores Sites, shadcn/ui sin uso y Tailwind sin uso.
- **Metadatos**: el plugin `plugins/metadatos-rutas.ts` genera en el build:
  - un HTML por cada ruta pública estática (`dist/<ruta>/index.html`);
  - `plantilla.html` (plantilla de Caddy para los detalles y las rutas desconocidas; ver «404 y
    metadatos de detalle»);
  - `404.html` (noindex, con la marca `estado-pagina`);
  - `app.html` (genérico, respaldo con la API caída);
  - HTML con `noindex` para `/admin` y `/pantallas`.
- **Estilos**: `globals.css` se conserva idéntica a la propuesta. Los arreglos verificados van en
  `ajustes.css`, cada uno con su referencia:
  - A-001: cabecera a 360 px;
  - A-002: contraste AA por la decisión P4. Desde P9 (feature 012, US5), la frase del pie no
    tiene enlace; la regla que subraya los enlaces de esa línea se conserva por si vuelve a
    haber uno;
  - A-003: cabecera por debajo de 360 px;
  - A-004: fotos siempre completas por la decisión P6 (feature 012). Cada `<img>` de foto lleva
    `style={fondoFoto(src)}` (`lib/fotos.ts`, variable `--foto`). El marco no cambia; la foto se
    muestra con `contain` y el espacio sobrante se rellena con la misma foto bajo un velo verde.
  - A-005: logotipo nuevo de la cabecera por la decisión P7 (feature 012).
    - `Logo en="cabecera"` (`Site.tsx`) sirve `reused/logos/logo_cabecera-{480,720}.webp` con
      `srcset`/`sizes`. La imagen la genera `LogoImg` (`components/Logo.tsx`), compartido con el
      panel.
    - La altura del logotipo depende del tramo de la cabecera (80/70/68/58/49 px).
    - El enlace conserva el ancho de la marca anterior, así que nada más se mueve.
    - La barra lateral del panel siguió con `logo1.webp` en blanco hasta la decisión P11 (A-008).
  - A-006: logotipo también en el pie por la decisión P8 (feature 012).
    - `Logo en="pie"` sirve `reused/logos/logo_pie-{480,720}.webp`, la versión en negativo para el
      fondo verde oscuro, con `loading="lazy"`. `Brand`, con la silueta y el texto, se eliminó.
    - Ancho de 233 px, el de la marca anterior, o el de la columna si es menor; el alto sale de
      la proporción. Las demás columnas del pie no se mueven.
  - A-007: podio de las clasificaciones por la decisión P10 (feature 012).
    - `ClassificationTable` marca las filas con puesto 1–3 (`podium podium-N`) y pone el número
      en una medalla (`podium-medal`).
    - Fondo suave de oro, plata y bronce, con una franja interior de 4 px y la medalla en el mismo
      color más intenso (variable `--podio`).
    - La medalla no cambia el alto de la fila. Cuenta el puesto publicado, también con filtros.
  - A-007, ampliado por la decisión P12 (feature 012, US10): podio por sexo y por categoría.
    - La consulta pública devuelve `podium` por fila (`services/clasificaciones.py::_podio`,
      `rank()` por sexo sobre el grupo filtrado, sin la búsqueda).
    - El panel usa `rangosPodio` (`lib/classifications.ts`).
    - La medalla pasa a ser una etiqueta junto al nombre (`.podium-label`).
  - A-008: panel de administración (feature 012).
    - US7: la barra lateral se desplaza en vertical (`overflow-y: auto`,
      `overscroll-behavior: contain`). `Admin.tsx` muestra la opción de la sección abierta una vez
      por sección.
    - Con el menú de móvil abierto, el contenido usa `overflow-x: clip` para que «Ver web» no
      desborde la página.
    - US8 (decisión P11): `LogoImg` en negativo en la barra lateral (180 px, con
      «ADMINISTRACIÓN» debajo) y en el acceso (261 px). `logo1.webp` queda solo como favicon.
  - A-009: contraste AA del panel con la sesión iniciada (decisión P4; feature 012, US9).
    - Las cabeceras de las tablas de listados y el pie del panel pasan a `--muted`.
    - Lo vigila `scripts/verificar-panel-aa.mjs`.
- **Textos del panel por sección** (decisión P13; feature 012, US11): `src/lib/textosPanel.ts`
  da el nombre de la lista y del elemento de cada sección, con tilde, artículo y género. De ahí
  salen el buscador, el enlace de vuelta, el bloque del formulario, la lista vacía y el nombre
  accesible de las subidas. El nombre interno de la sección (`galeria`) solo se usa en rutas.
- **Fuentes**: WOFF2 real (Barlow Condensed y Manrope, OFL), servidas desde `/fonts`. Las tres
  variantes de Barlow Condensed incluyen la Ñ y las vocales con tilde: el título «TRAIL
  PEÑASAGRA» de la portada (decisión P13) se dibuja entero en esa fuente.
- **Respaldo**: `src/lib/data.ts` (semilla) se muestra si `/api/content` falla, junto con el aviso
  existente.

## Backend

- FastAPI 0.165, Pydantic 2, pydantic-settings, SQLAlchemy 2.1 síncrono con psycopg 3, Alembic 1.20.
- `GET /api/health` responde siempre que el proceso esté vivo. `GET /api/ready` exige base de
  datos accesible y esquema en la cabeza de Alembic; con la base caída responde en unos 3 s
  (timeout de conexión).
- Las migraciones se aplican solo con un paso explícito:
  `docker compose run --rm api alembic upgrade head`. El servicio nunca migra al arrancar.
- **Contrato de lectura**: `GET /api/content` es un adaptador de solo lectura que devuelve el
  `SiteData` publicado (o el privado con `?admin=1`). Desde la feature 010 todas las secciones
  proceden de PostgreSQL. `backend/seed/contenido_inicial.json` (validado al arrancar) solo se
  usa como respaldo de lo que falte en una base sin inicializar. No existe `PUT /api/content`
  (405): las escrituras son por recurso (`/api/admin/...`).
- Errores en formato `{"error": "..."}`, que es el que ya consume el frontend. Las respuestas de
  la API llevan `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`.
- OpenAPI en `/api/docs` solo con `ENTORNO=desarrollo`. Los contratos versionados están en
  `specs/*/contracts/`.

## Cierre para el lanzamiento (feature 011)

- **404 y metadatos de detalle**:
  - Las rutas con HTML estático no cambian. El resto se reescribe a `plantilla.html` con
    `templates`, que pide `GET /api/meta?ruta=…` mediante `httpInclude`.
  - La API responde siempre 200 (`text/plain`): el marcador `<!-- meta -->` seguido de las
    etiquetas escapadas (título, descripción, `og:*`, `twitter:*` y canónica), o `no-encontrada`.
  - Con `no-encontrada`, la plantilla llama a `httpError 404` y `handle_errors` sirve `404.html`
    con estado 404. El SPA ve la marca `estado-pagina` y muestra «Este sendero no está en el
    mapa.».
  - Si la plantilla falla (API caída), `handle_errors` sirve `app.html` con 200 y el SPA muestra
    su aviso de respaldo. En ese caso tampoco se puede distinguir una ruta inexistente.
  - Detalles con metadatos propios: noticias, álbumes, pruebas (`/carreras` y `/recorridos`) y
    `/clasificaciones/{año}` con clasificaciones publicadas.
  - Los 404 y 405 genéricos de la API salen en español.
- **Cabeceras**:
  - Caddy añade una CSP por defecto (`?Content-Security-Policy`): solo `self`, imágenes `https:`
    y `data:`, y `frame-src` de Wikiloc. `/media` conserva su CSP propia (`default-src 'none';
    sandbox`).
  - `X-Frame-Options`, `Referrer-Policy` y `nosniff` siguen igual.
- **`/pantallas`** (decisión P5): `PANTALLAS=si|no` en el servicio `web`; con `no` (producción y
  valor por defecto), `error 404`.
- **Operación**:
  - `infra/scripts/verificar-copia.sh` comprueba la restauración tabla a tabla y archivo a archivo.
  - `python -m app.cli limpiar-archivos [--horas N] [--borrar]` lista o borra (tras escribir
    «BORRAR») los archivos sin referencias `/media/<clave>` en ninguna tabla con más de N horas.
  - El almacenamiento tiene `borrar` (local y S3).
- **Pruebas**: pytest usa `httpx2` (sin avisos).

## Persistencia del panel por recursos (desde la feature 004)

`Admin.tsx` guarda siempre un `SiteData` completo con `save()`. `frontend/src/lib/persistencia.ts`
(`guardarCambios`) compara el estado anterior con el nuevo y reparte los cambios:

| Cambio | Destino |
|---|---|
| `settings.edition`, `date`, `countdown` | `PUT /api/admin/evento` |
| prueba nueva o editada | `PUT /api/admin/carreras/{id}` (con `version`) |
| prueba borrada | `DELETE /api/admin/carreras/{id}?version=N` |
| `settings.registrationsOpen`, `registrationMessage`, `solidarityRegistration` | `PUT /api/admin/inscripciones` (después de las pruebas y del evento) |
| `news[]` | `PUT/DELETE /api/admin/noticias/{id}` (007) |
| `albums[]` | `PUT/DELETE /api/admin/albumes/{id}` (008) |
| `sponsors[]` y `collaborators[]` | `PUT/DELETE /api/admin/entidades/patrocinadores/{id}` y `…/colaboradores/{id}` (009) |
| `regulation` | `PUT /api/admin/reglamento` (010; después de las inscripciones, con la versión de la edición) |
| `settings.email`, `phone`, `instagram` | `PUT /api/admin/contacto` (010; con `contactVersion`) |
| cualquier otro cambio | Se rechaza en el cliente con «Esta sección del panel todavía no guarda cambios.», sin llamar al servidor |

Después se relee `GET /api/content?admin=1`, así que el panel muestra lo que confirmó el
servidor, con sus versiones. Cada feature siguiente añade su recurso a este módulo.

## Evento y carreras (feature 004)

- **Tablas**:
  - `ediciones`: año único, `fecha_hora` timestamptz nula, contador, `es_actual` (índice único
    parcial) y `version`.
  - `carreras`: el `slug` es la URL estable.
  - `carreras_edicion`: UNIQUE por carrera y edición, con los datos de la prueba, `publicada` y
    `version`.
- **Ficha mostrada**: la web enseña la ficha *publicada* de año más alto; el panel, la de año más
  alto en cualquier estado. Cambiar la edición de una prueba crea otra ficha y la anterior queda
  como histórico.
- **Fechas**: la API acepta ISO con zona o una hora local interpretada en Europe/Madrid (`fold=0`)
  y devuelve ISO UTC `…Z` (`app/services/fechas.py`).
- **Errores**: 409 con «Otra persona ha modificado estos datos…» ante una versión obsoleta; 400
  con «Revisa el campo «…».» ante un dato no válido.
- **Importación**: `python -m app.cli importar-inicial` carga las ediciones 2026 (11/07/2026 09:00)
  y 2027 (actual, sin fecha) y las 3 pruebas con datos de 2026. Solo rellena las partes vacías;
  `--reemplazar` exige confirmación escrita.
- **`/api/content`**: `settings.edition`, `date`, `countdown` y `races` salen de PostgreSQL. Sin
  ediciones ni pruebas (base sin inicializar), se sirve la semilla.

## Reglamento y contacto (feature 010)

- **Reglamento**:
  - Columna `ediciones.reglamento` (hasta 200 000 caracteres). Comparte la versión de la edición
    con el evento y las inscripciones.
  - La web y el editor muestran el de la edición actual o, si no tiene, el de la edición más
    reciente que lo tenga (hoy, la referencia de 2026). Si ninguna edición tiene reglamento, se
    sirve el de la semilla, como en una base sin inicializar, para que `/reglamento` nunca quede
    vacío.
  - Se normalizan los saltos de línea y se recortan los espacios exteriores; el resto se guarda
    íntegro.
- **Contacto**: tabla `configuracion` de fila única (`id = 1`), con correo, teléfono, Instagram
  (`https://` en `instagram.com`) y `version`. `/contacto` deriva el usuario de Instagram del
  enlace (`lib/contacto.ts`). «Imanol» y «Plaza de Cosío» siguen fijos (DISCREPANCIAS C2).
- **Formulario de contacto**: sigue preparando un `mailto` al correo configurado, sin envío por
  servidor.
- **Importación**:
  - El reglamento de la semilla se asocia a la edición 2026 si ninguna edición tiene reglamento.
  - El contacto se importa si no hay configuración.

## Patrocinadores y colaboradores (feature 009)

- **Tabla** `entidades`: `tipo` (`patrocinador` o `colaborador`), `slug` único dentro del tipo,
  nombre, logotipo obligatorio, `web` (vacía o https sin credenciales), `orden`, `publicada` y
  `version`. El mismo identificador en las dos secciones son dos entidades distintas.
- **Endpoints**: `PUT` y `DELETE` en `/api/admin/entidades/{seccion}/{id}`, con `seccion` =
  `patrocinadores` o `colaboradores`. Borrar no borra el archivo del logotipo.
- **Orden público**: `orden` y, en caso de empate, fecha de alta. Solo se publican las visibles.
  Con web, el logo se enlaza en una pestaña nueva; sin web, es informativo.
- **Mensajes**: los errores de validación usan los nombres del formulario de la sección
  («logotipo», «web de la entidad»; `ETIQUETAS_POR_RUTA` en `app/main.py`).
- **Importación**: los 8 patrocinadores aprobados, sin web, si la tabla está vacía. Colaboradores
  vacíos (D3).

## Galería (feature 008)

- **Tablas**:
  - `albumes`: `slug`, título, año, portada obligatoria, `url_externa` (https), `publicado`,
    `orden` y `version`.
  - `fotografias`: `album_id`, imagen, `alt` y `orden`.
- **Endpoints**: `PUT` y `DELETE` en `/api/admin/albumes/{id}`. El `PUT` sustituye la lista de
  fotos en la misma transacción. Quitar fotos o borrar álbumes no borra archivos.
- **Contrato**: `albums[]` añade `photoAlts`, que por defecto es «{título} · fotografía N»
  (DISCREPANCIAS M7). Orden público: año descendente y después `orden`.
- **Visor**: el foco queda atrapado (Tab/Mayús+Tab), Escape cierra y el foco vuelve a la miniatura.
  Sin cambios visuales.
- **Importación**: los 3 álbumes históricos con sus enlaces de Google Fotos, si la tabla está vacía.

## Noticias (feature 007)

- **Tabla**: `noticias` con `slug` (URL), título, categoría, `fecha` (día, nula), imagen, extracto,
  cuerpo de texto plano, `publicada` y `version`.
- **Orden**: `fecha DESC NULLS FIRST, creado_en DESC`. Las noticias sin fecha son anuncios
  vigentes y van arriba.
- **Endpoints**: `PUT` y `DELETE` en `/api/admin/noticias/{id}`, con versión (409), mediante
  `persistencia.ts` (`recursoSimple`). Las nuevas son borradores.
- **Importación**: `importar-inicial` carga la noticia de la semilla y la de producción
  (`gracias-trail-2026`, con su imagen en `/reused/noticias/`) si la tabla está vacía.

## Clasificaciones CSV (feature 006)

- **Tablas**:
  - `clasificaciones`: `identificador` único y `carrera_edicion_id` UNIQUE con FK RESTRICT, que
    impide borrar una prueba clasificada.
  - `resultados`: `orden`, `posicion` (NULL o 1–100000), dorsal y tiempo como texto, `busqueda`
    sin tildes, e índice único `(clasificacion_id, lower(dorsal)) WHERE dorsal <> ''`.
  - `importaciones_csv`: importación temporal por sesión.
- **Lector**: `app/services/csv_clasificaciones.py` adapta el lector TS de la propuesta con los
  mismos límites, alias (incluido `meta`) y mensajes por fila.
- **Flujo del panel**: lectura, mapeo y vista previa en el cliente. Después:
  1. `POST /api/admin/clasificaciones/vista-previa` valida en el servidor y guarda la importación
     temporal; devuelve un token.
  2. `PUT /api/admin/clasificaciones/{id}` con `importToken` sustituye las filas en una
     transacción. Cualquier fallo deja la clasificación anterior.
- **Web**: `GET /api/clasificaciones/{id}/participantes?q=&categoria=&sexo=&pagina=` (páginas de
  50; solo clasificaciones publicadas). `/api/content` público solo envía metadatos y
  `participants`. `ClassificationTable` consulta al servidor con el mismo marcado.
  `/clasificaciones/{año}` fija el año.
- **Operador**: `python -m app.cli importar-clasificacion --carrera … --edicion … --titulo …
  [--publicar] [--sustituir] < archivo.csv` (UTF-8 o Windows-1252).
- **Dorsal**: obligatorio solo para clasificados (decisión P3).

## Inscripciones y Dorsal Solidario (feature 005)

- **Datos**: columnas `inscripciones_abiertas`, `mensaje_inscripciones` (1–2000 caracteres al
  escribir) y `url_dorsal_solidario` en `ediciones`. La versión es la misma de la edición
  (compartida con el evento).
- **Endpoint**: `GET` y `PUT` en `/api/admin/inscripciones`. No se pueden abrir sin un destino
  válido: URL del dorsal válida o alguna prueba cuya ficha publicada más reciente tenga enlace.
  En caso contrario, 400.
- **Destinos externos** (`url_externa_segura`): vacío o `https://` con host, sin credenciales ni
  espacios, de hasta 2200 caracteres. Se aplica a la URL del dorsal y a `races[].registration`.
- **Web**: el componente aprobado `DorsalSolidario` aplica la matriz. Con las inscripciones
  cerradas, `/inscripciones` muestra su estado cerrado en lugar del bloque.
- **Importación**: `importar-inicial` rellena estos campos en la edición actual solo si siguen en
  sus valores por defecto.

## Archivos (feature 003)

- **Subida**: `POST /api/upload` con la protección de escritura de la 002. Acepta JPEG, PNG, WebP,
  PDF y GPX.
  - El tipo se detecta por los bytes mágicos.
  - El GPX se analiza con `defusedxml`: sin DTD ni entidades, raíz `gpx`.
  - SVG, HTML y cualquier otro formato se rechazan.
  - Límite de 10 MB (`UPLOAD_MAX_BYTES`): Caddy corta a 11 MB y la API a 10 MB, ambos con 413 en
    JSON.
  - Clave aleatoria `uuid4().hex.<ext>`. Primero se guarda el objeto y después la fila en
    `archivos` (tipo, tamaño, sha256, nombre saneado, quién lo subió y cuándo). Si falla el
    almacenamiento: 503 sin fila.
- **Entrega**: `GET` y `HEAD` de `/media/{clave}` son públicos (la clave no se puede adivinar).
  Cualquier otra ruta bajo `/media/` devuelve el mismo 404 genérico.
  - Cabeceras: caché inmutable de 1 año, ETag = sha256 (con 304), `nosniff` y
    `CSP default-src 'none'; sandbox`.
  - Los GPX se descargan con nombre saneado.
  - Una clave no válida o inexistente devuelve 404 genérico.
- **Almacenamiento** (`app/storage/`): se elige con `ALMACENAMIENTO`.
  - `local`: volumen `media` en `/data/media`, con escritura atómica.
  - `s3`: `boto3` con `endpoint_url`, para Cloudflare R2 en producción.
  - Las credenciales solo existen en el servidor.
  - En desarrollo y pruebas, el servidor S3 es moto (`motoserver/moto:5.2.5`, servicio `s3-dev`);
    la imagen pública de MinIO ya no está disponible.
  - `compose.s3.yaml` arranca la API completa en modo S3, sin publicar puertos.
- **Referencias de contenido** (`app/core/referencias.py`): se aceptan valores vacíos,
  `/reused/…` (sin `..`), `/media/<clave>` o `https://` sin credenciales, de hasta 2200
  caracteres. Las features 004–010 las validan con esta regla.
- **Recursos estáticos**: `/reused/`, `/images/`, `/fonts/` y `/templates/` siguen sirviéndose
  desde `frontend/public` sin cambios.
- **Sin borrado físico**: retirar contenido no borra archivos. La limpieza de archivos sin uso
  llega en la 011.

## Seguridad del panel (feature 002)

- **Cuentas**:
  - Solo se crean con el comando de operador `python -m app.cli`: `crear-admin`,
    `restablecer-password`, `desactivar`, `activar`, `revocar-sesiones` y `listar-admins`. No hay
    registro público.
  - Contraseñas en Argon2id (`argon2-cffi`), de 12 a 128 caracteres y distintas del usuario.
  - La contraseña se introduce de forma oculta o por `--password-stdin`, nunca como argumento.
- **Sesión**:
  - Token opaco de 256 bits en la cookie `penasagra_admin`, con `HttpOnly`, `SameSite=Strict` y
    `Path=/`. El atributo `Secure` depende de `COOKIE_SECURE`, que es `true` por defecto y
    `false` solo en el Compose de desarrollo por HTTP.
  - Caduca a las 8 h exactas (`SESSION_HOURS`). En PostgreSQL solo se guarda la huella SHA-256.
  - Se revoca al cerrar sesión, desactivar la cuenta, restablecer la contraseña o mediante
    `revocar-sesiones`.
- **Escrituras**: se comprueban por este orden.
  1. **Origin** ∈ {`PUBLIC_ORIGIN`} ∪ `ORIGENES_PERMITIDOS`; si no, 403.
  2. **Sesión** válida; si no, 401.
  3. **CSRF** de doble envío vinculado a la sesión: la cookie legible `penasagra_csrf` debe ir
     también en la cabecera `X-CSRF-Token`; si no, 403.

  El panel usa `frontend/src/lib/api.ts` (`apiFetch`). `/api/session` vuelve a emitir el
  comprobante si falta.
- **Límite de acceso**:
  - Máximo de 8 fallos en 15 minutos por IP (`LOGIN_MAX_INTENTOS`, `LOGIN_VENTANA_MINUTOS`), con
    respuesta 429 y `Retry-After`.
  - Se guarda en la tabla `limites_login` (clave = huella de la IP) con `SELECT … FOR UPDATE`.
  - La IP real llega en el `X-Forwarded-For` que pone Caddy, que ignora el del cliente. Uvicorn
    usa `--proxy-headers` y confía en él (`FORWARDED_ALLOW_IPS=*`) solo porque la API no es
    accesible fuera de la red interna. Uvicorn lee esa variable del entorno, así que el
    Dockerfile no la fija. Comprobado: la clave es la huella de la IP real del cliente, no la de
    Caddy ni la de un `X-Forwarded-For` falsificado.
- **Errores**:
  - Mensaje genérico idéntico para usuario inexistente, contraseña errónea y cuenta inactiva.
  - Tiempo igualado con un hash ficticio.
  - Con la base caída: 503 genérico. Si la API no responde, Caddy devuelve 503 en JSON
    (`handle_errors`).
- **Escrituras**: todas son recursos reales con la protección completa. `PUT /api/content` y el
  501 transitorio se retiraron en la feature 010; las pruebas de protección usan
  `PUT /api/admin/contacto`.
- **Otras cabeceras**: Caddy añade `nosniff`, `Referrer-Policy` y `X-Frame-Options: SAMEORIGIN`.
  La CSP completa se define en la feature 011 (iframe de Wikiloc).
- **Sin secretos en el repositorio**: `.env` está ignorado y `.env.example` solo contiene valores
  de desarrollo.
