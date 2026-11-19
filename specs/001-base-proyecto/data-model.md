# Data Model: Base del proyecto (001)

Esta feature no crea tablas de dominio. Las tablas relacionadas llegan con sus features
(ver `docs/ROADMAP.md` y el modelo objetivo de `docs/referencia/14_BACKEND_FASTAPI_POSTGRESQL.md`).

## Esquema PostgreSQL

| Objeto | Origen | Contenido |
|---|---|---|
| `alembic_version` | Alembic | `version_num` de la última revisión aplicada |

Revisión inicial: `0001_base` (sin cambios de dominio). La disponibilidad compara
`alembic_version.version_num` con la cabeza del directorio de migraciones.

## Contenido público transitorio (`SiteData`)

Contrato de solo lectura servido por `GET /api/content` y consumido por `Site.tsx` y `Admin.tsx`
(ver `contracts/api-base.openapi.yaml`). Procede de `backend/seed/contenido_inicial.json`.
Los campos extra se permiten (compatibilidad con `passthrough` de la propuesta).

### Settings

| Campo | Tipo | Regla | Valor inicial |
|---|---|---|---|
| `edition` | string | `^20\d\d$` | `"2027"` |
| `date` | string | vacío o fecha ISO con zona | `""` (sin fecha, decisión P1) |
| `countdown` | bool | — | `true` |
| `registrationsOpen` | bool | — | `false` |
| `solidarityRegistration` | string | vacío o `https://` sin credenciales | `""` |
| `registrationMessage` | string | ≤ 2000 | mensaje de preparación de la próxima edición |
| `email` | string | email | `asociacionpenasagra@gmail.com` |
| `phone` | string | ≤ 40 | `+34619364819` |
| `instagram` | string | URL https | `https://www.instagram.com/asociacion_penasagra/` |

### Item (elemento de cualquier colección)

| Campo | Tipo | Regla |
|---|---|---|
| `id` | string | `^[\w-]{1,100}$`, único dentro de su colección |
| `published` | bool | obligatorio; solo `true` aparece en la vista pública |

Se permiten campos adicionales propios de cada colección.

### Colecciones (listas de `Item`)

| Colección | Campos principales | Contenido inicial |
|---|---|---|
| `races` | `title, label, km, elevation, price, image, color, description, terrain, start, route, wikiloc, gpx, registration, edition, aid` | `trail-27k`, `speed-14k`, `familiar-7k` (referencia 2026, imagen real de cada carrera) |
| `news` | `title, category, date, image, excerpt, body` | `proxima-edicion` |
| `albums` | `title, year, image, url, photos[]` | `edicion-2026`, `edicion-2025`, `edicion-2024` (Google Photos) |
| `results` | `title, year, raceId, race, sourceFile, importedAt, rows[]` | vacío (CSV 2026 en la feature 006) |
| `sponsors` | `name, image, url, order` | 8 patrocinadores, `url` vacía |
| `collaborators` | `name, image, url, order` | vacío |
| `regulation` | string ≤ 100 000 | resumen 2026 sin el párrafo de prueba |

### Reglas de la vista pública (`publicData`)

- Se excluyen los elementos con `published !== true` en todas las colecciones.
- Se excluyen las clasificaciones legadas sin `rows` y las de carreras solidarias
  (`visibleClassifications` de la propuesta).
- La respuesta nunca incluye hashes, sesiones ni borradores.

## Configuración del entorno

| Variable | Uso | Valor de desarrollo |
|---|---|---|
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Base de datos del servicio `db` | `trail` / `trail` / `trail_dev` |
| `DATABASE_URL` | Conexión de la API | `postgresql+psycopg://trail:trail_dev@db:5432/trail` |
| `PUBLIC_ORIGIN` | Origen público (metadatos OG; Origin en 002) | `http://localhost:8080` |
| `WEB_PORT` | Puerto publicado por la entrada web | `8080` |
| `ENTORNO` | `desarrollo` o `produccion` | `desarrollo` |
| `LOG_LEVEL` | Nivel de registro de la API | `info` |
