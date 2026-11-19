# Implementation Plan: Administrador

**Branch**: `002-administrador` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-administrador/spec.md`

## Summary

Cuentas de administración propias con contraseñas Argon2id, gestionadas solo mediante un comando
de operador. La sesión es opaca, de servidor y revocable, con una caducidad absoluta de 8 h, y se
transmite en una cookie HttpOnly con `SameSite=Strict`.

Las escrituras se protegen con tres comprobaciones en este orden:

1. Origin permitido.
2. Sesión válida.
3. CSRF de doble envío vinculado a la sesión.

El límite de 8 intentos cada 15 minutos por IP es persistente. El panel se reconecta con cambios
mínimos (`apiFetch`) y sin cambios visuales. Las decisiones están en [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13 · TypeScript 5.9 (sin cambios de versión respecto a 001)

**Primary Dependencies**: se añade `argon2-cffi` 25.1. Se mantienen FastAPI, SQLAlchemy, Alembic,
psycopg y React.

**Storage**: PostgreSQL 17, con las tablas `administradores`, `sesiones` y `limites_login`
(migración `0002_administracion`).

**Testing**: pytest contra PostgreSQL real · vitest · Playwright (`verificar-acceso.mjs`)

**Target Platform**: contenedores Linux (Compose) · navegadores modernos

**Project Type**: aplicación web (SPA + API + proxy)

**Performance Goals**: el acceso responde en menos de 1 s (Argon2id con parámetros por defecto,
unos 50–100 ms). La validación de sesión es una consulta indexada por petición.

**Constraints**:

- Ningún secreto en claro en BD, registros o respuestas.
- Mismo origen.
- Sin cambios visuales.
- Cookies `Secure` en producción.

**Scale/Scope**: una o pocas cuentas y pocas sesiones simultáneas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento | Estado |
|---|---|---|
| I. Preservación visual | La pantalla de acceso y el resumen no cambian. Solo cambia la lógica de `fetch` de escritura en `Admin.tsx` | ✅ |
| II. Persistencia real | Sesiones y límites en PostgreSQL. Sobreviven a reinicios (SC-004, SC-006) | ✅ |
| III. Seguridad del administrador | Argon2id, sesiones opacas revocables (solo huella), cookie HttpOnly/SameSite/Secure, límite persistente, CSRF + Origin, permisos en FastAPI, sin secretos en Git y demostración sin escritura | ✅ |
| IV. Compatibilidad de datos y URLs | Se mantienen `/api/login`, `/api/session`, `/api/logout`, `/api/content` y `/api/upload` que consume el panel | ✅ |
| V. Funcionalidades verificables | pytest con PostgreSQL real y Playwright de extremo a extremo por Caddy | ✅ |
| VI. Alcance controlado | Sin registro público, sin roles ni correo. Las secciones sin feature responden 501 sin simular éxito | ✅ |

Re-evaluación tras el diseño: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/002-administrador/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/{api-administracion.openapi.yaml, cli-operador.md}
├── checklists/{requirements.md, seguridad.md}
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml / uv.lock                    # + argon2-cffi
├── alembic/env.py                              # target_metadata = Base.metadata
├── alembic/versions/0002_administracion.py
├── app/models/{__init__,base,administracion}.py
├── app/core/config.py                          # + SESSION_HOURS, COOKIE_SECURE, ORIGENES_PERMITIDOS, LOGIN_*
├── app/core/seguridad.py                       # hash/verify Argon2id, tokens, huellas, política
├── app/services/{administradores,sesiones,limites}.py
├── app/api/deps.py                             # requiere_origen, sesion_actual, requiere_admin, requiere_escritura
├── app/api/sesion.py                           # /api/login, /api/session, /api/logout
├── app/api/contenido.py                        # ?admin=1 con sesión; PUT → 501
├── app/api/archivos.py                         # POST /api/upload → 501 (feature 003 lo sustituye)
├── app/cli.py                                  # python -m app.cli …
└── tests/{test_cli,test_login,test_sesion,test_proteccion,test_limites,test_revocacion}.py (+ conftest)

frontend/
├── src/lib/api.ts                              # leerCookie, apiFetch (X-CSRF-Token)
├── src/components/admin/Admin.tsx              # save/logout/upload → apiFetch
├── tests/api.test.ts
└── scripts/{verificar-acceso.mjs, verificar-admin.mjs (actualizado)}

compose.yaml / compose.dev.yaml / .env.example  # nuevas variables
backend/Dockerfile                              # uvicorn --proxy-headers (FORWARDED_ALLOW_IPS por entorno)
```

**Structure Decision**: se mantiene la estructura de la feature 001 y se añade `app/models/`, el
primer modelo SQLAlchemy del proyecto.

## Design Notes

- **Orden de las dependencias en escrituras**: `requiere_origen` (403) → `requiere_admin` (401)
  → `requiere_csrf` (403). El login solo exige origen. El logout exige origen y, si hay sesión
  válida, CSRF; sin sesión, borra las cookies y devuelve 200.
- **Normalización del Origin**: esquema y host en minúsculas y sin barra final. Se compara con el
  conjunto `{PUBLIC_ORIGIN} ∪ ORIGENES_PERMITIDOS`.
- **Errores de base de datos en el login** (`OperationalError`): 503 con un mensaje genérico.
- **Validación del cuerpo**: los errores de esquema (422 de FastAPI) se transforman en
  `400 {"error":"Datos no válidos."}` para todas las rutas.
- **Cookies en el logout**: se borran con `Max-Age=0` y los mismos atributos con que se crearon.
- **Pruebas**: el reloj se controla manipulando fechas en la base (`expira_en`, `inicio`); no se
  simula el tiempo del proceso.

## Complexity Tracking

Sin violaciones.
