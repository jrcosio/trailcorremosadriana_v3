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
