# Estado del proyecto

Última actualización: 2026-11-19

## Punto de continuidad

- **Última feature cerrada**: 005-inscripciones-dorsal (merge local en `main`)
- **Siguiente feature**: 006-clasificaciones-csv
- **Fase SDD**: por iniciar (`/speckit-specify`)
- **Siguiente acción concreta**: `git switch -c 006-clasificaciones-csv main` y
  `/speckit-specify`.
  - Tablas `clasificaciones` (UNIQUE `carrera_edicion_id`), `resultados` (posición > 0 o NULL;
    dorsal y tiempo como texto; UNIQUE por clasificación y `lower(dorsal)`) e
    `importaciones_csv` (temporal por sesión, con hash y caducidad).
  - Lectura y validación del CSV portadas a Python desde `frontend/src/lib/classifications.ts`
    (mismos límites; alias `meta` y `pos`).
  - Vista previa en el servidor; confirmación transaccional que sustituye las filas.
  - FK RESTRICT hacia `carreras_edicion` (borrar una prueba con clasificaciones → 409, R5 de la
    004).
  - Consulta pública paginada con búsqueda y filtros.
  - Nueva ruta `/clasificaciones/{año}`.
  - Importación de los CSV reales de 2026 de producción como publicados (decisión P2; asignación
    27km → `trail-27k`, 14km → `speed-14k`, marcha → `familiar-7k`). Los CSV están en
    `datos_iniciales/trailcorremosadriana_v2/datos/2026/` y se copiarán a
    `backend/seed/clasificaciones/2026/` con su procedencia.
- **Entorno local**: esquema `0005_inscripciones`, datos importados y cuenta local `admin`.

## Features

| Estado | Features |
|---|---|
| Terminadas | 0, 001, 002, 003, 004, 005 (inscripciones y Dorsal Solidario) |
| Activa | — |
| Pendientes | 006 a 011 (ver [ROADMAP.md](ROADMAP.md)) |

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
| 2026-11-20 | Sesión opaca de 8 h exactas sin renovación; CSRF de doble envío vinculado a la sesión; orden Origin → sesión → CSRF | 002 research R2/R3 |
| 2026-11-20 | Límite por IP (huella) persistente con `FOR UPDATE`; IP real vía Caddy y uvicorn `--proxy-headers` | 002 research R4/R5 |
| 2026-11-20 | Secciones sin persistencia: `PUT /api/content` y `POST /api/upload` → 501 tras la protección completa | 002 research R8 |
| 2026-11-20 | Caddy devuelve 503 JSON si la API no responde (estado «error de servicio» del acceso) | 002 implementación |
| 2026-11-20 | Política de contraseña: 12–128 caracteres, distinta del usuario | 002 spec FR-003 |
| 2026-11-20 | Archivos públicos por clave aleatoria (también los de borradores); sin borrado físico hasta la 011 | 003 spec Assumptions, research R7 |
| 2026-11-20 | Entrega de `/media` siempre a través de la API (también con R2); CDN directa a valorar en la 011 | 003 research R1 |
| 2026-11-20 | S3 de desarrollo y pruebas con moto (`motoserver/moto:5.2.5`): la imagen pública de MinIO ya no está disponible | 003 research R2 |
| 2026-11-20 | El panel guarda por recursos mediante `lib/persistencia.ts` (sin `PUT` del documento completo) | 004 research R1 |
| 2026-11-20 | Una prueba tiene una ficha por edición; la web muestra la publicada más reciente | 004 research R2 |
| 2026-11-20 | Edición 2026 con fecha oficial 11/07/2026 09:00 (dato de producción) importada como histórico | 004 research R6 |
| 2026-11-20 | Inscripciones por edición; abrir exige un destino válido (dorsal o prueba publicada con enlace); los destinos solo pueden ser https sin credenciales | 005 research R1–R3 |
| 2026-11-20 | Con las inscripciones cerradas, `/inscripciones` muestra su estado aprobado en lugar del bloque del dorsal (spec corregida durante la implementación) | 005 spec Assumptions |

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
| 2026-11-20 | 002 | Checklist de seguridad (32 ítems) | 1.ª revisión 27/32 → 5 huecos corregidos en la spec → 32/32 con evidencia |
| 2026-11-20 | 002 | `/speckit-analyze` | 0 críticos/HIGH; 1 MEDIUM y 5 LOW corregidos antes de implementar |
| 2026-11-20 | 002 | pytest en `api-test` (PostgreSQL real): CLI, acceso, sesión, protección, límite, revocación | **97 passed** |
| 2026-11-20 | 002 | vitest (incluye `apiFetch`) y typecheck | **44 passed**; OK |
| 2026-11-20 | 002 | `alembic upgrade head` explícito | `/api/ready`: `migraciones_pendientes` → `disponible` |
| 2026-11-20 | 002 | `crear-admin --password-stdin` en Compose | Cuenta creada; hash `$argon2id$` |
| 2026-11-20 | 002 | `verificar-acceso.mjs --bloqueo` a través de Caddy | 8/8 OK (mensaje genérico, resumen en 0,7 s, cookies, recarga, 501 sin éxito simulado, cierre + cookie anterior 401, bloqueo) |
| 2026-11-20 | 002 | Bloqueo tras reiniciar la API y con `X-Forwarded-For` falsificado | 429 (`Retry-After` 891 s); la cabecera falsificada no cambia la clave |
| 2026-11-20 | 002 | Quickstart §3: `admin=1` 200, PUT sin CSRF 403, con CSRF 501, logout con origen ajeno 403 | OK |
| 2026-11-20 | 002 | `docker compose restart` con sesión abierta | Sesión válida tras el reinicio |
| 2026-11-20 | 002 | `revocar-sesiones`, `desactivar` y `activar` sobre una sesión real | 401 tras revocar; acceso rechazado si está inactiva; 200 tras activar |
| 2026-11-20 | 002 | `verificar-acceso.mjs --api-caida` y `verificar-respaldo.mjs` | Error de servicio sin acceso; web pública con respaldo |
| 2026-11-20 | 002 | `verificar-admin.mjs` y `verificar-rutas.mjs` (regresión de la 001) | OK; 42/42 rutas |
| 2026-11-20 | 002 | Revisión visual del acceso y del resumen frente a `/pantallas/admin` | Idénticos (salvo la franja de vista de diseño) |
| 2026-11-20 | 002 | IP real: petición desde otro contenedor (172.21.0.5) a `web` con `X-Forwarded-For: 6.6.6.6` | Clave = sha256(172.21.0.5); no es la de Caddy (172.21.0.2) ni la falsificada |
| 2026-11-20 | 002 | `/speckit-converge` | 1.ª pasada: 2 tareas (T037–T038) resueltas; 2.ª pasada: Converged |
| 2026-11-20 | 003 | Checklists `requirements` 16/16 y `seguridad` 18/18 (con evidencia); `analyze`: 2 LOW corregidos | OK |
| 2026-11-20 | 003 | pytest (PostgreSQL real y S3 real con moto por HTTP) | **173 passed** |
| 2026-11-20 | 003 | `alembic upgrade head` → `0003_archivos` | OK |
| 2026-11-20 | 003 | Subida por Caddy (webp real) y entrega `/media`: cabeceras (inmutable, ETag, CSP sandbox, nosniff), HEAD, 304, bytes idénticos | OK |
| 2026-11-20 | 003 | Rechazos por Caddy: SVG 400, sin CSRF 403, 11 MB 413 (Caddy), 10,5 MB 413 (API) | OK |
| 2026-11-20 | 003 | Subida de 9,9 MB (SC-004) | 0,07 s |
| 2026-11-20 | 003 | `docker compose down` + `up`: archivo subido intacto | Bytes idénticos |
| 2026-11-20 | 003 | Recursos estáticos `/reused`, `/images`, `/fonts`, `/templates`, `robots.txt` | 200 |
| 2026-11-20 | 003 | `backup.sh` con base y archivos (`media-*.tgz`) | OK |
| 2026-11-20 | 003 | `verificar-subida.mjs` (subida desde el panel y rechazo de SVG), `verificar-acceso.mjs`, `verificar-rutas.mjs` | OK; 42/42 |
| 2026-11-20 | 003 | Modo S3 completo con `compose.s3.yaml` (Caddy → API → moto) | Objeto en el bucket, no en el volumen local; entrega con bytes idénticos |
| 2026-11-20 | 003 | `/speckit-converge` | 1.ª pasada: 2 tareas (T020–T021) resueltas; 2.ª pasada: Converged |
| 2026-11-20 | 004 | Checklists `requirements` 16/16 y `datos` 13/13 (1 hueco corregido: regla de cambio horario); `analyze`: 3 LOW corregidos | OK |
| 2026-11-20 | 004 | pytest (PostgreSQL real) | **226 passed** |
| 2026-11-20 | 004 | vitest (incluye `persistencia.ts`) y typecheck | **52 passed**; OK |
| 2026-11-20 | 004 | `alembic upgrade head` → 0004; `importar-inicial` dos veces | Datos creados; 2.ª vez «Sin cambios» |
| 2026-11-20 | 004 | Textos de 44 capturas frente a la 001 (SC-001) y `verificar-rutas` | 0 diferencias; 0 desbordamientos; 42/42 |
| 2026-11-20 | 004 | `verificar-evento-carreras.mjs` (fecha de verano e invierno, sin fecha, km, borrador → publicada → retirada → borrada, conflicto 409, restauración) | 12/12 OK |
| 2026-11-20 | 004 | Cambio de contador y `docker compose restart` (SC-003) | Persiste; restaurado |
| 2026-11-20 | 004 | Regresión: `verificar-acceso` 7/7, `verificar-subida` 2/2, `verificar-admin` 2/2 | OK |
| 2026-11-20 | 004 | Convergencia: descarga GPX en el detalle (attachment) y fecha pasada (contador a cero), restaurados | 16/16 OK en `verificar-evento-carreras.mjs` |
| 2026-11-20 | 004 | `/speckit-converge` | 1.ª pasada: 2 tareas (T018–T019) resueltas; 2.ª pasada: Converged |
| 2026-11-20 | 005 | Checklists `requirements` 16/16 y `seguridad` 10/10; `analyze` sin hallazgos | OK |
| 2026-11-20 | 005 | pytest (PostgreSQL real) | **256 passed** (tras la convergencia) |
| 2026-11-20 | 005 | vitest y typecheck | **54 passed**; OK |
| 2026-11-20 | 005 | `alembic upgrade head` → 0005; `importar-inicial` completa la base existente | Mensaje rellenado sin tocar otros datos |
| 2026-11-20 | 005 | `verificar-inscripciones.mjs`: matriz 4 estados × 3 páginas, tarjetas, panel (abrir sin destinos rechazado; cerrar conserva la URL), restauración | 12/12 en la matriz; 4/4 en el resto |
| 2026-11-20 | 005 | URL del dorsal y `docker compose restart` (SC-005) | Persiste; restaurado |
| 2026-11-20 | 005 | Regresión: `verificar-rutas` 42/42, `verificar-evento-carreras` 16/16, `verificar-acceso` 7/7 | OK |
| 2026-11-20 | 005 | `/speckit-converge` | 1.ª pasada: T010 (URL con espacios recortada) resuelta; 2.ª pasada: Converged |

## Bloqueos

Ninguno. Faltan datos de producción que debe facilitar el propietario y que no bloquean el
trabajo: fecha 2027, enlaces de inscripción y de pago solidario, webs de patrocinadores,
reglamento definitivo, GPX y autorizaciones de imagen para el lanzamiento.

## Avisos técnicos menores

- En esta máquina el puerto 8000 del host está ocupado por otro proceso. `compose.dev.yaml` permite
  cambiarlo con `API_PORT_LOCAL` (por ejemplo, `API_PORT_LOCAL=8001`).

- `Site.tsx` (propuesta) no consume el cuerpo de una respuesta de error de `/api/content`, así que
  Chromium deja esa petición abierta. No afecta al usuario. Las verificaciones con la API caída
  esperan al aviso en lugar de a `networkidle`.

- pytest avisa de que `starlette.testclient` con `httpx` está obsoleto (recomienda `httpx2`).
  No afecta a los resultados; se revisará al actualizar dependencias.
