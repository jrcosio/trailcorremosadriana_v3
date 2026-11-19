# Research: Base del proyecto (001)

Fecha: 2026-11-19. Todas las incógnitas del contexto técnico quedan resueltas aquí.

## R1. Cómo ejecutar el frontend de la propuesta fuera de Vinext/Workers

- **Decision**: SPA con Vite 8.0.13 + React 19.2.6 + TypeScript 5.9.3, con `index.html` y
  `src/main.tsx` que renderiza `<Site path={location.pathname}/>`. Se conserva el router interno
  de `Site.tsx` (switch por `path`) y los enlaces `<a>` con recarga completa.
- **Rationale**: el análisis del código mostró que Vinext/Workers solo afecta a `vite.config.ts`,
  `worker/`, `app/api/*`, `app/media/*`, `lib/server.ts` y `cloudflare-env.d.ts`. Las pantallas son
  componentes cliente sin `next/*` (0 importaciones de `next/link`, `next/image`,
  `next/navigation`, `next/headers`). `app/[[...slug]]/page.tsx` es un catch-all de 2 líneas que
  pasa `path` a `Site`. El HTML que se servía en el servidor siempre contenía la semilla, así que
  no se pierde contenido real del SSR.
- **Alternatives considered**: Next.js 16 en Node frente a FastAPI (SSR real y `generateMetadata`,
  pero añade un runtime Node en producción y no aporta datos reales sin reescribir la carga);
  React Router (obligaría a cambiar decenas de `<a>` y el comportamiento de navegación aprobado).

## R2. Dependencias que se conservan y se eliminan

- **Decision**: conservar `react`, `react-dom`, `lucide-react` (1.31.0) y tipos. Eliminar `next`,
  `vinext`, `wrangler`, `@cloudflare/*`, `@vitejs/plugin-rsc`, `react-server-dom-webpack`,
  `drizzle-*`, `json-rpc-2.0`, `raw-body`, `zod` (solo servidor), Tailwind/PostCSS (no se importa
  en `globals.css`), los 61 componentes shadcn de `components/ui` (ningún consumidor real),
  `connector-*`, `lib/server.ts`, `lib/utils.ts`, `hooks/`, `app/chatgpt-auth.ts`, `examples/`,
  `vendor/` y los scripts Sites.
- **Rationale**: solo se mantiene lo que importan las pantallas reales; reduce superficie y
  tiempo de instalación sin cambiar el aspecto (todo el estilo está en `app/globals.css`).
- **Alternatives considered**: copiar el proyecto entero y podar después (arrastra dependencias
  de Workers y riesgo de compilación).

## R3. Metadatos por ruta sin SSR

- **Decision**: un plugin de Vite (`frontend/plugins/metadatos-rutas.ts`) genera en el build un
  HTML por ruta pública estática (`dist/<ruta>/index.html`) a partir de `dist/index.html`,
  sustituyendo `<title>`, `description`, `og:*`, `twitter:*` y `canonical`. Se generan además
  `dist/app.html` (metadatos genéricos para rutas dinámicas) y `dist/admin/index.html` y
  `dist/pantallas/index.html` con `robots noindex`. Títulos de producción conservados para `/`,
  `/recorridos`, `/galeria`, `/clasificaciones`, `/reglamento` y `/contacto`.
- **Rationale**: conserva la capacidad de producción (metadatos por página) sin servidor de
  renderizado; Caddy selecciona el archivo por ruta.
- **Alternatives considered**: `document.title` en cliente (los rastreadores y las vistas previas
  de mensajería no ejecutan scripts); prerender completo con navegador (coste y datos
  desactualizados).
- **Imagen OG**: URL absoluta construida con `PUBLIC_ORIGIN` en tiempo de build
  (`/reused/logos/corremos_por_adriana.webp`, la misma imagen que usa producción).

## R4. Servir web y API bajo el mismo origen

- **Decision**: Caddy 2.11 (imagen `caddy:2.11-alpine`) sirve `frontend/dist` y hace
  `reverse_proxy` de `/api/*` y `/media/*` al servicio `api:8000`. Resolución de archivos:
  `try_files {path} {path}/index.html /app.html`; `/admin*` → `/admin/index.html`;
  `/pantallas*` → `/pantallas/index.html`; `/` → `index.html`. En desarrollo, el servidor de
  Vite hace proxy de `/api` y `/media` a `127.0.0.1:8000`.
- **Rationale**: mismo origen para que la cookie `SameSite=Strict` y la comprobación de `Origin`
  de la feature 002 funcionen sin CORS. Producción ya usa Caddy.
- **Alternatives considered**: nginx (equivalente, pero Caddy ya es la pieza de producción y
  gestiona TLS automáticamente en el despliegue futuro); servir estáticos desde FastAPI (mezcla
  responsabilidades y complica caché).

## R5. Stack del backend y versiones

- **Decision**: Python 3.13 (`python:3.13-slim`), gestionado con `uv` 0.11 y `uv.lock`.
  Dependencias de ejecución: `fastapi` 0.165, `uvicorn[standard]` 0.54, `sqlalchemy` 2.1,
  `psycopg[binary]` 3.3, `alembic` 1.20, `pydantic` 2.14, `pydantic-settings` 2.16.
  Desarrollo: `pytest` 9.2, `httpx` 0.28, `ruff` 0.17. Las de features posteriores
  (`argon2-cffi`, `boto3`, `python-multipart`) se añaden en su feature.
- **Documentación OpenAPI**: `/api/docs` y `/api/openapi.json` solo con `ENTORNO=desarrollo`; en
  producción se desactivan y el contrato vive versionado en `specs/*/contracts/`.
- **Rationale**: versiones estables actuales con soporte de Python 3.13; SQLAlchemy síncrono con
  psycopg 3 es suficiente para el volumen del proyecto y simplifica transacciones y pruebas.
- **Alternatives considered**: SQLAlchemy async + asyncpg (más complejidad sin necesidad de
  concurrencia alta); Python 3.14 local (aún sin ruedas binarias garantizadas para todas las
  dependencias; el contenedor fija 3.13).

## R6. Migraciones como paso explícito y comprobación de disponibilidad

- **Decision**: Alembic con revisión base `0001_base` (sin tablas de dominio; crea
  `alembic_version`). Paso explícito: `docker compose run --rm api alembic upgrade head`. El
  servicio nunca migra al arrancar. `/api/ready` abre una conexión con `connect_timeout=3`,
  ejecuta `SELECT 1`, lee `alembic_version` y la compara con `ScriptDirectory.get_heads()`.
  Respuestas: `200 {"estado":"disponible"}`; `503 {"estado":"no_disponible","motivo":
  "base_de_datos_inaccesible"|"migraciones_pendientes"}`.
- **Rationale**: DOC 14 exige migraciones controladas para evitar carreras entre procesos; la
  disponibilidad debe reflejar esquema al día sin exponer detalles.
- **Alternatives considered**: migrar en el arranque del contenedor (carreras con varias
  réplicas y cambios no revisados); servicio `migrate` con `depends_on` automático (no es un paso
  explícito).

## R7. Contenido público transitorio

- **Decision**: `GET /api/content` lee `backend/seed/contenido_inicial.json` al arrancar, lo
  valida con un esquema Pydantic permisivo (`SiteData`, campos extra permitidos) y devuelve
  `{"data": <publicData>, "revision": 0}` filtrando elementos `published != true` y clasificaciones
  legadas sin filas. `?admin=1` responde 401 sin sesión. La semilla se genera a partir de la
  semilla aprobada de la propuesta (`lib/data.ts`, que ya excluye D1–D4); cualquier diferencia
  editorial legítima de la exportación publicada se revisa y se documenta en
  `backend/seed/README.md`.
- **Rationale**: mantiene el contrato que consumen `Site.tsx` y `Admin.tsx` sin cambios y lo deja
  listo para que cada feature sustituya su sección por datos de PostgreSQL.
- **Alternatives considered**: cargar la semilla en una tabla JSON (contradice M1 y el principio
  II); servir la exportación tal cual (incluye datos de prueba).

## R8. Autenticación hasta la feature 002

- **Decision**: `GET /api/session` → `200 {"authenticated": false}`; `POST /api/login` →
  `503 {"error": "El acceso de administración todavía no está disponible."}`. No se implementa
  `/api/logout` ni `/api/upload` (el panel solo los usa con sesión).
- **Rationale**: `Admin.tsx` muestra el formulario de acceso cuando la sesión es falsa y pinta el
  `error` devuelto por `/api/login`; así no se simula éxito ni se concede acceso (FR-019).
- **Alternatives considered**: no exponer `/api/session` (el panel mostraría «No se puede conectar
  con el servidor», un mensaje engañoso).

## R9. Pruebas

- **Decision**:
  - Backend: pytest dentro del contenedor (`api-test`, perfil `test` en `compose.dev.yaml`)
    contra PostgreSQL real. `conftest.py` crea bases temporales (`trail_test_<uuid>`) para probar
    esquema aplicado, esquema pendiente y base inaccesible, y las elimina al terminar.
  - Frontend: vitest 5.1 (compatible con Vite 8) + `react-dom/server` portando las partes puras
    de `scripts/check-solidarity.tsx` y `scripts/check-classifications.tsx` (las partes que
    probaban los route handlers de Workers pasan a pytest en sus features).
  - Visual: `frontend/scripts/capturas.mjs` con Playwright 1.65 (Chromium) captura 360/768/1024/
    1440 px de las rutas clave en local y en la referencia publicada, guarda `innerText` y mide
    `scrollWidth > innerWidth` para detectar desbordamiento.
- **Rationale**: el principio V exige PostgreSQL real; reutilizar las comprobaciones existentes
  garantiza que las reglas de negocio no cambian al portar.
- **Alternatives considered**: SQLite en pruebas (prohibido por DOC 14 para afirmar
  compatibilidad); testcontainers (requiere acceso al socket Docker desde el contenedor).

## R10. Configuración y secretos

- **Decision**: variables documentadas en `.env.example`; Compose usa valores de desarrollo por
  defecto (`${VAR:-valor_dev}`) para arrancar sin `.env`. Variables de esta feature:
  `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `PUBLIC_ORIGIN`,
  `WEB_PORT`, `ENTORNO`, `LOG_LEVEL`. Las de cookies, sesiones, límites y almacenamiento se añaden
  en sus features. La base de datos no publica puertos en `compose.yaml`; `compose.dev.yaml` las
  publica solo en `127.0.0.1`.
- **Rationale**: arranque sin credenciales de producción (FR-012) y base interna (FR-013). El
  despliegue de producción (feature 011) usará variables obligatorias (`${VAR:?}`) sin valores por
  defecto.

## R11. Procedencia y licencias

- **Decision**: `frontend/public/fonts/licencias/*_OFL.txt` se copian con las fuentes;
  `docs/PROCEDENCIA_RECURSOS.md` lista cada recurso copiado (origen, licencia/autoría) y el código
  reutilizado (propuesta, commit `9e07688`; producción v2, MIT).
- **Rationale**: principio IV y FR-021.
