# Implementation Plan: Base del proyecto

**Branch**: `001-base-proyecto` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-base-proyecto/spec.md`

## Summary

Levantar la base ejecutable del proyecto fuera de `datos_iniciales`:

- **frontend**: SPA Vite + React que reutiliza las pantallas de la propuesta sin cambios visuales,
  con HTML por ruta para los metadatos.
- **backend**: FastAPI con salud, disponibilidad (base de datos + Alembic) y el adaptador de solo
  lectura `GET /api/content` alimentado por una semilla curada.
- **datos**: PostgreSQL 17 con migraciones Alembic aplicadas como paso explícito.
- **infra**: Caddy en el mismo origen y Docker Compose con red interna.

Las decisiones técnicas están razonadas en [research.md](research.md).

## Technical Context

**Language/Version**: TypeScript 5.9.3 (React 19.2.6, Vite 8.0.13) · Python 3.13

**Primary Dependencies**: react, react-dom, lucide-react 1.31.0 · fastapi 0.165, uvicorn 0.54,
sqlalchemy 2.1, psycopg 3.3, alembic 1.20, pydantic 2.14, pydantic-settings 2.16 · Caddy 2.11

**Storage**: PostgreSQL 17 (volumen `pgdata`); en esta feature solo `alembic_version`

**Testing**: pytest 9.2 + httpx contra PostgreSQL real en contenedor · vitest 5.1 · Playwright
1.65 (capturas y desbordamiento)

**Target Platform**: contenedores Linux (Docker Compose) · navegadores modernos de escritorio y
móvil

**Project Type**: aplicación web (frontend SPA + API + proxy)

**Performance Goals**: disponibilidad `< 5 s` con la base caída (timeout de conexión 3 s);
recuperación tras reinicio `< 60 s`

**Constraints**: mismo origen; base sin puertos publicados por defecto; sin credenciales de
producción; build sin `datos_iniciales`; sin cambios visuales

**Scale/Scope**: 16 pantallas públicas y de revisión, 24 vistas de panel; un único organizador

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento en esta feature | Estado |
|---|---|---|
| I. Preservación visual | Se copian componentes, CSS y recursos sin cambios visuales; revisión a 360/768/1024/1440 px frente a la referencia publicada | ✅ |
| II. Persistencia real | PostgreSQL con volumen y Alembic. El contenido transitorio es de solo lectura (sin escrituras que perder) y se migra a tablas en 004–010 (M1) | ✅ |
| III. Seguridad del administrador | `/api/login` nunca concede acceso (503); `?admin=1` → 401; vistas de diseño sin escritura; sin secretos en Git | ✅ |
| IV. Compatibilidad de datos y URLs | Se conservan todas las rutas del mapa y el alias `/recorridos`; `/api/content` mantiene su contrato; procedencia en `docs/PROCEDENCIA_RECURSOS.md` | ✅ |
| V. Funcionalidades verificables | pytest contra PostgreSQL real, vitest con las comprobaciones existentes, capturas y quickstart ejecutado | ✅ |
| VI. Alcance controlado | Semilla aprobada sin datos de prueba; edición 2027 sin fecha; nada inventado | ✅ |

Re-evaluación tras el diseño (Fase 1): sin violaciones; no hay entradas en *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/001-base-proyecto/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api-base.openapi.yaml
│   └── rutas-web.md
├── checklists/requirements.md
└── tasks.md            # /speckit-tasks
```

### Source Code (repository root)

```text
frontend/
├── package.json · package-lock.json · tsconfig.json · vite.config.ts
├── Dockerfile · .dockerignore        # build Node 22 → imagen caddy:2.11-alpine con dist/
├── index.html
├── plugins/metadatos-rutas.ts        # HTML por ruta (título, descripción, OG, canonical, noindex)
├── src/
│   ├── main.tsx
│   ├── seo/rutas.ts                  # tabla de metadatos (contracts/rutas-web.md)
│   ├── styles/globals.css            # copia de app/globals.css
│   ├── components/{Site,Results,ClassificationTable,DorsalSolidario}.tsx
│   ├── components/admin/{Admin,ClassificationManager,ClassificationImport}.tsx
│   └── lib/{data,classifications,registration}.ts
├── public/{reused,images,fonts,templates}/ · robots.txt
├── tests/{solidario.test.tsx,clasificaciones.test.tsx,metadatos.test.ts}
└── scripts/capturas.mjs

backend/
├── pyproject.toml · uv.lock · Dockerfile · .dockerignore · alembic.ini
├── alembic/{env.py,script.py.mako,versions/0001_base.py}
├── app/
│   ├── main.py                       # FastAPI, routers, cabeceras
│   ├── core/{config.py,db.py}        # pydantic-settings, engine SQLAlchemy
│   ├── api/{salud.py,contenido.py,sesion.py}
│   ├── schemas/contenido.py          # SiteData (Pydantic, extra=allow)
│   └── services/{contenido.py,esquema.py}
├── seed/{contenido_inicial.json,README.md}
└── tests/{conftest.py,test_salud.py,test_ready.py,test_contenido.py,test_sesion.py}

infra/
├── caddy/Caddyfile
└── scripts/{backup.sh,restore.sh}    # esqueleto documentado; se prueba en 011

compose.yaml · compose.dev.yaml · .env.example
docs/{arquitectura.md,PROCEDENCIA_RECURSOS.md,desarrollo.md}
```

**Structure Decision**: web application en la raíz con `frontend/`, `backend/` e `infra/`, como
fija el prompt de desarrollo. DOC 14 proponía anidarlo en `proyecto/`, pero aquí no existe ese
nivel. Cada Dockerfile vive junto a su componente para que el contexto de build no incluya el
resto del repositorio. `infra/` contiene el proxy y la operación. La decisión se documenta en
`docs/arquitectura.md`.

## Design Notes

- **Copia del frontend**:
  - Se copian los archivos tal cual. Solo se cambian las importaciones de entorno: se elimina
    `'use client'` (inocuo) y se ajusta el alias `@/` → `src/`.
  - No se toca JSX ni CSS. `globals.css` mantiene `@import url('/fonts/barlow.css')` y
    `@import url('/fonts/manrope.css')`.
- **`main.tsx`**: `createRoot(document.getElementById('root')).render(<Site path={location.pathname}/>)`.
  La ruta sin barra final se normaliza (`/carreras/` → `/carreras`).
- **Semilla**:
  - `contenido_inicial.json` se genera evaluando `seed` de `lib/data.ts` y se compara con
    `contenido/contenido-publicado.json`.
  - Las diferencias editoriales que no sean D1–D4 se revisan y documentan en
    `backend/seed/README.md`.
- **Disponibilidad**:
  - El engine de SQLAlchemy usa `pool_pre_ping=True` y `connect_args={"connect_timeout": 3}`.
  - `/api/ready` captura `OperationalError` y devuelve un motivo genérico, sin traza.
- **Compose**:
  - `api` depende de `db` en estado *healthy*.
  - Healthcheck de `api`: `python -c` contra `/api/health`.
  - `web` depende de `api` en estado *started*.
  - Volúmenes: `pgdata` y `caddy_data`. Red `interna`.
- **compose.dev.yaml**:
  - Publica `api` en `127.0.0.1:8000` y `db` en `127.0.0.1:5432`.
  - Define `api-test` (target `test` del Dockerfile, perfil `test`) que ejecuta `pytest`.
- **Cabeceras** (en Caddy):
  - Todas las respuestas: `X-Content-Type-Options: nosniff`,
    `Referrer-Policy: strict-origin-when-cross-origin` y `X-Frame-Options: SAMEORIGIN`.
  - `/assets/*`: caché inmutable de 1 año.
  - HTML: `no-cache`.
  - La CSP completa se aborda en 011 por el iframe de Wikiloc.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
