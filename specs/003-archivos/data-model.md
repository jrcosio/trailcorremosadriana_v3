# Data Model: Archivos (003)

Migración Alembic `0003_archivos` (sobre `0002_administracion`).

## Archivo (`archivos`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | bigint identity | PK |
| `clave` | varchar(64) | NOT NULL, UNIQUE; patrón `^[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$` (CHECK) |
| `tipo` | varchar(64) | NOT NULL; uno de `image/jpeg`, `image/png`, `image/webp`, `application/pdf`, `application/gpx+xml` (CHECK) |
| `tamano` | integer | NOT NULL; CHECK `tamano > 0` (el máximo lo fija `UPLOAD_MAX_BYTES`) |
| `sha256` | char(64) | NOT NULL; huella SHA-256 en hexadecimal del contenido |
| `nombre_original` | varchar(255) | NULL; saneado (solo el nombre base, caracteres imprimibles, ≤ 255) |
| `subido_por` | integer | NULL; FK → `administradores.id` ON DELETE SET NULL |
| `creado_en` | timestamptz | NOT NULL, por defecto `now()` |

Los bytes viven en el almacenamiento con la clave `clave`. La base de datos no guarda contenido.

## Referencia de contenido (regla, no tabla)

Valor permitido: vacío, `/reused/…` sin `..`, `/media/<Archivo.clave>` o `https://` sin
credenciales. Máximo de 2200 caracteres.

## Configuración nueva

| Variable | Defecto (código) | Desarrollo (Compose) |
|---|---|---|
| `ALMACENAMIENTO` | `local` | `local` (`s3` con el perfil `s3`) |
| `MEDIA_DIR` | `/data/media` | volumen `media` |
| `UPLOAD_MAX_BYTES` | `10000000` | `10000000` |
| `S3_ENDPOINT_URL` | vacío | `http://s3-dev:5000` (moto) |
| `S3_BUCKET` | vacío | `trail-media` |
| `S3_REGION` | `auto` | `us-east-1` |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | vacío | valores ficticios de moto |
| `S3_CREAR_BUCKET` | `false` | `true` (solo en desarrollo) |
