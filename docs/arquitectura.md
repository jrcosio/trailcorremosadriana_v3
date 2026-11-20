# Arquitectura

Estado a 2026-11-19 (feature 001). Las decisiones detalladas y sus alternativas están en
`specs/001-base-proyecto/research.md`.

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

`compose.dev.yaml` publica `api` y `db` solo en `127.0.0.1` para desarrollo local y define
`api-test` (pytest contra PostgreSQL real).

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
- **Metadatos**: el plugin `plugins/metadatos-rutas.ts` genera en el build un HTML por cada ruta
  pública estática (`dist/<ruta>/index.html`). Las rutas de detalle y las desconocidas usan
  `app.html` con metadatos genéricos. `/admin` y `/pantallas` usan HTML con `noindex`.
- **Estilos**: `globals.css` se conserva idéntica a la propuesta. Los arreglos verificados van en
  `ajustes.css`, cada uno con su referencia (A-001: desbordamiento de la cabecera a 360 px).
- **Respaldo**: `src/lib/data.ts` (semilla) se muestra si `/api/content` falla, junto con el aviso
  existente.

## Backend

- FastAPI 0.165, Pydantic 2, pydantic-settings, SQLAlchemy 2.1 síncrono con psycopg 3, Alembic 1.20.
- `GET /api/health` responde siempre que el proceso esté vivo. `GET /api/ready` exige base de
  datos accesible y esquema en la cabeza de Alembic; con la base caída responde en unos 3 s
  (timeout de conexión).
- Las migraciones se aplican solo con un paso explícito:
  `docker compose run --rm api alembic upgrade head`. El servicio nunca migra al arrancar.
- **Contrato transitorio**: `GET /api/content` es un adaptador de solo lectura que devuelve el
  `SiteData` publicado. Hoy procede de `backend/seed/contenido_inicial.json`, validado al arrancar.
  Las features 004–010 sustituyen cada sección por tablas de PostgreSQL manteniendo el contrato.
  No existe `PUT /api/content`: las escrituras serán por recurso (`/api/admin/...`).
- Errores en formato `{"error": "..."}`, que es el que ya consume el frontend. Las respuestas de
  la API llevan `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`.
- OpenAPI en `/api/docs` solo con `ENTORNO=desarrollo`. Los contratos versionados están en
  `specs/*/contracts/`.

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
| secciones aún no migradas | `PUT /api/content`, que responde 501 «Esta sección del panel todavía no guarda cambios.» |

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
- **Transitorio**: `PUT /api/content` y `POST /api/upload` aplican toda la protección y
  responden 501 («Esta sección del panel todavía no guarda cambios.») hasta sus features.
- **Otras cabeceras**: Caddy añade `nosniff`, `Referrer-Policy` y `X-Frame-Options: SAMEORIGIN`.
  La CSP completa se define en la feature 011 (iframe de Wikiloc).
- **Sin secretos en el repositorio**: `.env` está ignorado y `.env.example` solo contiene valores
  de desarrollo.
