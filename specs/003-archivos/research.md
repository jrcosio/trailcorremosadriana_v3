# Research: Archivos (003)

Fecha: 2026-11-20.

## R1. Interfaz de almacenamiento

- **Decision**: protocolo `Almacenamiento` (`app/storage/`) con `guardar(clave, datos, tipo)`,
  `leer(clave) -> bytes | None` y `existe(clave)`. Hay dos adaptadores y se elige con
  `ALMACENAMIENTO=local|s3`:
  - `Local`: escribe en `MEDIA_DIR` (volumen `media`) de forma atómica, con un archivo temporal
    seguido de `os.replace`. Las claves validadas impiden salir del directorio.
  - `S3`: `boto3` con `endpoint_url`, compatible con Cloudflare R2. Usa `put_object` y
    `get_object`; `NoSuchKey` devuelve `None`. `S3_CREAR_BUCKET=true` crea el bucket (solo en
    desarrollo).
- **Rationale**: lo pide la DOC 14 (adaptador local y S3/R2 por entorno). Los archivos ocupan como
  máximo 10 MB, así que leerlos en memoria es suficiente y simplifica ETag y 304.
- **Alternatives considered**: URLs prefirmadas o un bucket público de R2. Exponen otro origen y
  complican la CSP y la caché; se pueden valorar en la 011. Streaming por partes: innecesario con
  10 MB.

## R2. Servicio S3 de desarrollo y pruebas

- **Decision**: `motoserver/moto:5.2.5` como servicio `s3-dev` en `compose.dev.yaml` (perfil
  `test`). Las pruebas de integración del adaptador S3 hablan HTTP S3 real contra él.
- **Rationale**: la imagen `minio/minio` ya no está disponible públicamente (la descarga falló el
  2026-11-20). Moto implementa la API S3 por HTTP y basta para comprobar el adaptador.
- **Alternatives considered**: MinIO (no disponible); LocalStack (más pesado); mocks en proceso
  (no prueban el protocolo).

## R3. Detección y validación de tipo

- **Decision**: el tipo se detecta por bytes mágicos, sin mirar el nombre ni el tipo MIME
  declarado:

  | Tipo | Bytes mágicos | MIME | Extensión |
  |---|---|---|---|
  | JPEG | `FF D8 FF` | `image/jpeg` | `.jpg` |
  | PNG | `89 50 4E 47 0D 0A 1A 0A` | `image/png` | `.png` |
  | WebP | `RIFF????WEBP` | `image/webp` | `.webp` |
  | PDF | `%PDF-` | `application/pdf` | `.pdf` |

  Un GPX es un XML que se analiza con `defusedxml` (prohíbe DTD, entidades y referencias
  externas). Debe estar bien formado y su raíz local debe ser `gpx`; se entrega como
  `application/gpx+xml`.

  Cualquier otro contenido (SVG, HTML, ejecutables, texto) se rechaza con `400` y el mensaje
  «Sube imágenes JPG, PNG o WebP, documentos PDF o rutas GPX.».
- **Rationale**: FR-002 y FR-004. El prototipo aceptaba GPX solo porque contuviera `<gpx`; ahora
  el análisis es seguro.

## R4. Límite de tamaño

- **Decision**: `UPLOAD_MAX_BYTES=10000000` (10 MB, igual que el prototipo). Hay tres barreras:
  1. Caddy aplica `request_body max_size 11MB` en `/api/upload`.
  2. La API rechaza de antemano un `Content-Length` excesivo.
  3. La API lee por bloques y corta al superar el máximo.

  En todos los casos responde `413 {"error":"Máximo 10 MB por archivo."}` sin guardar nada.

## R5. Orden de escritura y fallos

- **Decision**: se valida, se guarda en el almacenamiento y después se inserta la fila en
  `archivos`. Si falla el almacenamiento, responde 503 y no se crea ninguna fila. Si falla la
  base después de guardar, el objeto queda huérfano pero ninguna fila apunta a un archivo
  inexistente (FR-011); la limpieza llega en la 011.

## R6. Entrega

- **Decision**: `GET /media/{clave}`, con la clave validada contra
  `^[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$`. Se busca la fila en `archivos` y se leen los bytes
  del almacenamiento. Si falta la fila o el objeto: 404 `{"error":"Archivo no encontrado."}`.

  Cabeceras de respuesta:

  | Cabecera | Valor |
  |---|---|
  | `Content-Type` | El registrado |
  | `Cache-Control` | `public, max-age=31536000, immutable` |
  | `ETag` | `"<sha256>"` |
  | `X-Content-Type-Options` | `nosniff` |
  | `Content-Security-Policy` | `default-src 'none'; sandbox` |
  | `Content-Disposition` | `inline` en imágenes y PDF; `attachment` con nombre `.gpx` saneado en GPX |

  Con `If-None-Match` coincidente responde 304.
- **Rationale**: FR-008 y FR-009. El prototipo hacía lo mismo con R2.

## R7. Acceso a archivos de borradores

- **Decision**: todos los archivos se entregan públicamente por una clave aleatoria de 128 bits
  que no se puede enumerar. Queda registrado en Assumptions de la spec.
- **Alternatives considered**: comprobar la publicación del contenido asociado en cada petición.
  Requiere un índice de referencias entre todos los recursos; se puede revisar en la 011 si se
  necesita.

## R8. Reglas de referencia

- **Decision**: `app/core/referencias.py` con `referencia_valida(valor)`. Acepta: vacío,
  `/reused/<ruta sin ..>`, `/media/<clave válida>` y `https://` sin credenciales, con un máximo de
  2200 caracteres. Las features 004–010 lo reutilizan en sus esquemas.

## R9. Persistencia y copias

- **Decision**:
  - Volumen Docker `media` montado en `/data/media`. El Dockerfile crea el directorio con
    propietario `app`.
  - `infra/scripts/backup.sh` añade un `tar.gz` del volumen cuando `ALMACENAMIENTO=local`, y
    `restore.sh` lo restaura si se le indica.
  - Con S3/R2, las copias son responsabilidad del bucket (versionado o replicación de R2), como
    se documentará en la 011.

## R10. Dependencias

- **Decision**: `boto3` 1.44, `python-multipart` 0.0.34 (formularios de FastAPI) y `defusedxml`
  0.7.1. En desarrollo, el servidor `motoserver/moto:5.2.5`.
