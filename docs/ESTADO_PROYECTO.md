# Estado del proyecto

Última actualización: 2026-11-19

## Punto de continuidad

- **Última feature cerrada**: 001-base-proyecto (merge local en `main`)
- **Siguiente feature**: 002-administrador
- **Fase SDD**: por iniciar (`/speckit-specify`)
- **Feature activa en Spec Kit**: `.specify/feature.json` apunta todavía a `specs/001-base-proyecto`.
  `/speckit-specify` de la 002 lo actualizará. Hay que comprobarlo después con
  `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`.
- **Siguiente acción concreta**: `git switch -c 002-administrador main` y `/speckit-specify` del
  administrador (cuentas propias Argon2id, CLI de alta/recuperación, login, sesión revocable,
  logout, límite persistente de intentos, CSRF + Origin, protección de escrituras y reconexión
  del acceso y resumen de `Admin.tsx`).
- **Entorno local**: `docker compose up -d` (web en http://localhost:8080). Esquema en
  `0001_base`.

## Features

| Estado | Features |
|---|---|
| Terminadas | 0 (preparación), 001 (base del proyecto) |
| Activa | — |
| Pendientes | 002 a 011 (ver [ROADMAP.md](ROADMAP.md)) |

## Decisiones tomadas

| Fecha | Decisión | Origen |
|---|---|---|
| 2026-11-19 | Próxima edición: 2027 sin fecha | Propietario (P1 en DISCREPANCIAS) |
| 2026-11-19 | Importar los CSV reales de 2026 como clasificaciones publicadas (feature 006) | Propietario (P2) |
| 2026-11-19 | Estructura `frontend/`, `backend/` e `infra/` en la raíz; Dockerfile junto a cada componente | Prompt + `docs/arquitectura.md` |
| 2026-11-19 | Frontend Vite + React SPA con el router interno de la propuesta; sin Vinext/Workers | 001 research R1/R2 |
| 2026-11-19 | Metadatos por ruta generados en el build (HTML por ruta) y servidos por Caddy | 001 research R3 |
| 2026-11-19 | Mismo origen: Caddy sirve la web y hace de proxy de `/api` y `/media` | 001 research R4 |
| 2026-11-19 | Migraciones solo como paso explícito; `/api/ready` informa de las pendientes | 001 research R6 |
| 2026-11-19 | `GET /api/content` como adaptador de solo lectura desde la semilla; sin `PUT /api/content` | DOC 14 + DISCREPANCIAS M1 |
| 2026-11-19 | La semilla es la de la propuesta: la única diferencia con la exportación son D1–D4 | `backend/seed/README.md` |
| 2026-11-19 | `globals.css` se conserva intacta; los arreglos van en `ajustes.css` (A-001: cabecera a 360 px) | 001 revision-visual |
| 2026-11-19 | Fotos, logotipos y silueta sin licencia genérica: uso limitado a la web de la carrera | DOC 11 |

## Supuestos

- El estado del evento se deriva de la apertura, la fecha y el contador; no hay enum (M3).
- Los datos de carreras son referencia de 2026 y se presentan como tal.
- `/pantallas` se mantiene como vista de revisión sin escritura hasta la feature 011.
- A 320 y 340 px la cabecera todavía desborda (357 px). Está por debajo del mínimo de aceptación
  (360 px) y se revisará en la 011.

## Pruebas ejecutadas

| Fecha | Feature | Prueba | Resultado |
|---|---|---|---|
| 2026-11-19 | 0 | `git check-ignore` sobre `datos_iniciales/` | Ignorada (`/datos_iniciales/`) |
| 2026-11-19 | 001 | pytest en `api-test` contra PostgreSQL 17 real (bases temporales) | **29 passed** |
| 2026-11-19 | 001 | vitest (comprobaciones portadas de solidario y clasificaciones, metadatos) | **38 passed** |
| 2026-11-19 | 001 | `tsc --noEmit` y `vite build` | OK; 14 HTML con metadatos |
| 2026-11-19 | 001 | Quickstart §1: build, `alembic upgrade head` explícito, `up -d` | db y api *healthy*; solo se publica 8080 |
| 2026-11-19 | 001 | Quickstart §2: `/api/ready` antes de migrar | 503 `migraciones_pendientes` |
| 2026-11-19 | 001 | Quickstart §2: base detenida | 503 `base_de_datos_inaccesible` en 1,08 s; `/api/health` 200 |
| 2026-11-19 | 001 | Quickstart §3: `restart` y `down` + `up` (mismo volumen) | Disponible en ≈1 s sin repetir Alembic |
| 2026-11-19 | 001 | `docker inspect` de `db` con `compose.yaml` | Sin `PortBindings` (FR-013) |
| 2026-11-19 | 001 | Quickstart §4–§5 vía Caddy: contenido, 401 admin, sesión, login 503, 11 títulos, `noindex`, `robots.txt`, cabeceras | OK |
| 2026-11-19 | 001 | `verificar-rutas.mjs` (Playwright): 42 rutas al abrir y al recargar | 42/42 OK |
| 2026-11-19 | 001 | `verificar-admin.mjs`: `/admin` sin acceso ni cookies; vista de diseño sin escrituras | OK |
| 2026-11-19 | 001 | `verificar-respaldo.mjs` con la API detenida | Contenido de referencia y aviso en 3/3 rutas |
| 2026-11-19 | 001 | Capturas a 360/768/1024/1440 (44 por sitio) frente a la referencia publicada | 0/44 desbordamientos (referencia: 11/44); diferencias solo D1–D4 |
| 2026-11-19 | 001 | Clon limpio sin `datos_iniciales`, build sin caché | Construido en 17 s; disponible en 25 s; imágenes sin `datos_iniciales` ni `.env` |
| 2026-11-19 | 001 | `infra/scripts/backup.sh` | Copia `pg_dump` creada (restauración completa en la 011) |
| 2026-11-19 | 001 | `/speckit-analyze` | 0 críticos; 1 HIGH y 7 MEDIUM/LOW corregidos antes de implementar |
| 2026-11-19 | 001 | `/speckit-converge` | 1.ª pasada: 4 tareas (T054–T057) implementadas; 2.ª pasada: Converged |

## Bloqueos

Ninguno. Faltan datos de producción que debe facilitar el propietario y que no bloquean el
trabajo: fecha 2027, enlaces de inscripción y de pago solidario, webs de patrocinadores,
reglamento definitivo, GPX y autorizaciones de imagen para el lanzamiento.

## Avisos técnicos menores

- pytest avisa de que `starlette.testclient` con `httpx` está obsoleto (recomienda `httpx2`).
  No afecta a los resultados; se revisará al actualizar dependencias.
