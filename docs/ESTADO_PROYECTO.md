# Estado del proyecto

Última actualización: 2026-11-20

## Punto de continuidad

- **Estado**: features 001–011 terminadas y fusionadas en `main`. Repositorio publicado en
  `origin` (GitHub) el 2026-11-20 a petición del propietario: `main` y todas las ramas de feature.
- **Feature activa**: 012-ajustes-revision (rama `012-ajustes-revision`). Recoge los ajustes que
  pide el propietario tras revisar la web.
  - Primero, **P6: las fotos se ven siempre completas**. Capturas del propietario en
    `datos_iniciales/` (ignorada por Git): la foto de Adriana sale con la cabeza cortada en la
    portada y en `/solidaridad`.
- **US1 (P6) terminada**:
  - Diagnóstico: 166 de 180 apariciones de fotos se recortaban (8 marcos públicos y 2
    miniaturas del panel, a 5 anchos), con pérdidas de hasta el 55 %.
  - Solución: `lib/fotos.ts` (`fondoFoto`, variable `--foto`) y `ajustes.css` A-004. Marcos
    iguales; foto completa (`contain`); relleno con la propia foto bajo un velo verde. La cabecera
    del detalle de prueba coloca la foto a la derecha, fuera del degradado.
  - Verificación: `verificar-fotos.mjs` (180/180 completas y marcos con 0 px de diferencia;
    logotipos, visor y vista previa sin cambios); axe 0; sin desbordamientos; capturas: solo
    cambian las 6 páginas con fotos; regresión correcta.
  - Fuera de alcance (supuesto de la spec): fondos decorativos de la portada, del banner de la
    galería y del marcador del mapa.
- **US2 terminada** (despliegue en la MV de la web anterior):
  - Situación en la MV (v2): un Caddy propio ocupa 80/443 y redirige `www`.
  - Cambios: redirección `www` solo en producción (`infra/caddy/redireccion-www.caddy`), HSTS y
    orígenes en *punycode* (dominio con «ñ»).
  - Guía (`docs/operacion.md`): migración con vuelta atrás (§12) y acceso al panel (§13).
  - Ensayo de producción con HTTPS desde un clon limpio (`trail-prod-ensayo`, dominio de prueba
    con «ñ»), siguiendo la guía: correcto (ver «Pruebas»).
  - El ensayo encontró y corrigió un fallo de la guía: la variable `$DC` no funciona en zsh; ahora
    se usa la función `dc`.
- **Siguiente acción concreta**:
  1. El propietario despliega en la MV siguiendo `docs/operacion.md` §12. Antes hay que subir a
     GitHub los commits de esta feature (push, cuando lo pida).
  2. Seguir con los demás ajustes de la revisión como historias nuevas de la 012.
- **Pendiente del propietario**: despliegue y datos de lanzamiento (ver «Bloqueos»). Los push
  siguientes, solo cuando el propietario los pida.

## Features

| Estado | Features |
|---|---|
| Terminadas | 0 y 001–011 (todas) |
| Activa | 012-ajustes-revision |
| Pendientes | — (solo acciones del propietario; ver el punto de continuidad) |

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
| 2026-11-20 | Dorsal obligatorio solo para clasificados (CSV real de la 27K con una participante «Sin salida» sin dorsal) | Propietario (P3) |
| 2026-11-20 | Vista previa en el cliente y validación autoritativa en el servidor con importación temporal por sesión (30 min, un solo uso) y sustitución transaccional | 006 research R1, DISCREPANCIAS M5 |
| 2026-11-20 | Consulta pública de participantes paginada en el servidor; el contrato público no incluye filas | 006 research R3 |
| 2026-11-20 | Los CSV reales de 2026 no se versionan (datos personales); se importan con el comando de operador | 006 spec Assumptions |
| 2026-11-20 | Noticias ordenadas: sin fecha primero y después por fecha descendente; la noticia de producción se importa sin categoría inventada («Actualidad») | 007 research R2, spec Assumptions |
| 2026-11-20 | Texto alternativo por foto generado desde el título del álbum (`photoAlts`); foco atrapado en el visor | 008 research R2/R5, DISCREPANCIAS M7 |
| 2026-11-20 | Patrocinadores y colaboradores en una tabla `entidades` por tipo; secciones independientes; los 8 patrocinadores sin web | 009 research, DOC 08 |
| 2026-11-20 | Mensajes de validación con el nombre del campo en el formulario de cada sección (`ETIQUETAS_POR_RUTA`) | 009 implementación |
| 2026-11-20 | Reglamento por edición con respaldo a la edición más reciente que lo tenga; la referencia de 2026 se asocia a su edición | 010 research R1/R2 |
| 2026-11-20 | Contacto en una configuración de fila única; «Imanol» y «Plaza de Cosío» siguen fijos; el usuario de Instagram se deriva del enlace | 010 research R4/R7, DISCREPANCIAS C2 |
| 2026-11-20 | Se retira `PUT /api/content`; un cambio sin recurso se rechaza en el cliente | 010 research R6, DISCREPANCIAS M1 |

## Supuestos

- El estado del evento se deriva de la apertura, la fecha y el contador; no hay enum (M3).
- Los datos de carreras son referencia de 2026 y se presentan como tal.
- `/pantallas` se retira en producción y sigue disponible en la revisión local (decisión P5).
- Los ajustes de la cabecera por debajo de 360 px (A-003) quedan fuera de los anchos aprobados y
  solo compactan espaciados y tamaños para que no haya desbordamiento a 320/340 px.
- «Imanol» y «Plaza de Cosío» siguen fijos en la presentación (C2).

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
| 2026-11-20 | 006 | Checklists `requirements` 16/16 y `datos` 15/15; `analyze` sin hallazgos (desviación justificada: lector duplicado) | OK |
| 2026-11-20 | 006 | pytest (PostgreSQL real): lector, vista previa, transacción, fallo simulado, tokens, consulta, 5000 filas en < 1 s | **296 passed** (297 tras la convergencia) |
| 2026-11-20 | 006 | vitest y typecheck | **59 passed**; OK |
| 2026-11-20 | 006 | Migración 0006 (`upgrade`, `downgrade` y `upgrade`) e importación de los CSV reales | 63/205/224 (SC-001) |
| 2026-11-20 | 006 | `verificar-clasificaciones.mjs` (2026 reales, búsqueda sin tildes, paginación, filtro, dorsal repetido, alta, sustitución, prueba clasificada no borrable, limpieza) | 11/11 OK |
| 2026-11-20 | 006 | Capturas de `/clasificaciones/2026` a 1440 y 360 px | Estilo aprobado; sin desbordamiento |
| 2026-11-20 | 006 | Regresión: rutas 42/42, evento y carreras 16/16, inscripciones 16/16, acceso 7/7 | OK |
| 2026-11-20 | 006 | `/speckit-converge` | 1.ª pasada: T014 (limpieza de importaciones caducadas) resuelta, 297 pytest; 2.ª pasada: Converged |
| 2026-11-20 | 007 | `analyze` sin hallazgos; pytest | **310 passed** |
| 2026-11-20 | 007 | vitest y typecheck | **60 passed**; OK |
| 2026-11-20 | 007 | Migración 0007 e `importar-inicial` sobre la base existente | 2 noticias importadas en el orden esperado |
| 2026-11-20 | 007 | `verificar-noticias.mjs` (existentes, borrador, publicación con imagen, HTML como texto, 409, retirada y borrado) | 7/7 OK |
| 2026-11-20 | 007 | `/speckit-converge` (después del merge; corregido en la misma sesión) | 1.ª pasada: T009 (noticia sin imagen → paisaje de reserva) verificada 8/8; 2.ª pasada: Converged |
| 2026-11-20 | 008 | `analyze` sin hallazgos; pytest | **320 passed** |
| 2026-11-20 | 008 | vitest y typecheck | **61 passed**; OK |
| 2026-11-20 | 008 | Migración 0008 e importación de los 3 álbumes | OK |
| 2026-11-20 | 008 | `verificar-galeria.mjs` (históricos, filtro, álbum con 2 fotos, publicación con `alt`, visor con 10 Tab dentro, flechas, Escape y foco devuelto, quitar foto, borrar) | 6/6 OK |
| 2026-11-20 | 008 | Desbordamiento a 4 anchos (`/galeria`, álbum, `/`, `/noticias`) y regresión completa | 0; rutas 42/42; 16/16/11/8/7/2 |
| 2026-11-20 | 008 | `/speckit-converge` | Converged a la primera |
| 2026-11-20 | 009 | `analyze` sin hallazgos; ruff; pytest (PostgreSQL real) | **329 passed** |
| 2026-11-20 | 009 | vitest, typecheck y build | **62 passed**; OK |
| 2026-11-20 | 009 | Migración 0009 e `importar-inicial` sobre la base existente; `restart` de la API | 8 patrocinadores sin web; persisten tras el reinicio |
| 2026-11-20 | 009 | `verificar-entidades.mjs` (8 logos en orden, sin enlace, `object-fit: contain` y ≥150 px a 4 anchos sin desbordamiento; 2 colaboradores con orden, pestaña nueva, cambio de orden, retirada, patrocinadores intactos, borrado) | 10/10 OK |
| 2026-11-20 | 009 | Regresión: rutas 42/42, admin 2/2, acceso 7/7, subida 2/2, evento 16/16, inscripciones 16/16, clasificaciones 11/11, noticias 8/8, galería 6/6, respaldo con la API detenida 3/3 | OK |
| 2026-11-20 | 011 | Decisiones del propietario P4 (contraste AA) y P5 (`/pantallas` retirada en producción); `analyze`: 0 críticos/HIGH, 1 MEDIUM y 2 LOW corregidos | OK |
| 2026-11-20 | 011 | Experimento con caddy:2.11 (`httpInclude`, `httpError` y `file_server { status }`; comportamiento con 404 y con la API caída) | Base del diseño R1 |
| 2026-11-20 | 011 | pytest (PostgreSQL real y S3 con moto): `/api/meta`, errores en español, `limpiar-archivos`, `borrar` en S3; con `httpx2` | **379 passed, 0 avisos** |
| 2026-11-20 | 011 | vitest (plantilla de Caddy, marca 404, metadatos), typecheck, `tsc --noUnusedLocals` y build | **72 passed**; OK |
| 2026-11-20 | 011 | `verificar-cierre.mjs` (estados de 16 rutas, metadatos propios, SPA en 404, `/admin`, API caída, CSP en 16 páginas + 7 del panel con subida, CSP de `/media`, `/pantallas` en los dos modos) | 7/7 OK |
| 2026-11-20 | 011 | `verificar-accesibilidad.mjs` (axe WCAG 2.1 A/AA, 17 rutas a 360/1440; desbordamiento a 320/340/360/768/1024/1440) | 0 incumplimientos; 0 desbordamientos |
| 2026-11-20 | 011 | Capturas antes y después (44): P4 solo cambia botones, el bloque naranja de la portada y el subrayado del pie; fuentes WOFF2 sin diferencias de píxeles | OK |
| 2026-11-20 | 011 | `infra/scripts/verificar-copia.sh` | 16 tablas y 42 archivos idénticos tras restaurar |
| 2026-11-20 | 011 | Ensayo de despliegue independiente (clon limpio, `trail-ensayo`, 8090, restauración sobre una base nueva) | Web, panel, clasificaciones 63/205/224, metadatos y archivos correctos; retirado sin tocar desarrollo |
| 2026-11-20 | 011 | `compose.produccion.yaml config` sin variables / con variables | Falla nombrando la variable / 80, 443, `COOKIE_SECURE=true`, `PANTALLAS=no` |
| 2026-11-20 | 011 | Regresión: rutas 42/42 (`/pantallas` activas y retiradas), admin 2/2 (los dos modos), acceso 7/7, subida 2/2, evento 16/16, inscripciones 16/16, clasificaciones 11/11, noticias 8/8, galería 6/6, entidades 10/10, reglamento y contacto 7/7, respaldo 3/3 | OK |
| 2026-11-20 | 012 | US1 (P6): `verificar-fotos.mjs` contra la referencia previa (180 fotos, 5 anchos, públicas, panel y álbum temporal) | 180/180 completas; marcos idénticos; relleno donde procede; logotipos, visor y vista previa sin cambios |
| 2026-11-20 | 012 | vitest (`fondoFoto`), axe y desbordamiento, capturas y regresión (rutas, cierre, galería, noticias, subida) | 75 passed; 0 incumplimientos; 0 desbordamientos; 42/42, 7/7, 6/6, 8/8, 2/2 |
| 2026-11-20 | 012 | US2: pytest (orígenes IDN; acceso con dominio escrito con «ñ») | 389 passed |
| 2026-11-20 | 012 | US2: ensayo de producción con HTTPS desde un clon limpio siguiendo `docs/operacion.md` §12 (`trail-prod-ensayo`, `SITE_ADDRESS=trailpeñasagra.localhost`) | HTTP→HTTPS 308; `www` 301 (conserva ruta y consulta); certificados para el dominio y `www` en *punycode*; HSTS; CSP; 404 reales; `/pantallas` 404; `/api/docs` 404; clasificaciones 63/205/224 |
| 2026-11-20 | 012 | US2: panel por HTTPS en el ensayo (Chromium) | Acceso con cookies `Secure`/`HttpOnly`/`SameSite=Strict`, guardado real (restaurado), subida, cierre de sesión, 0 violaciones de CSP; la redirección `www` también en el navegador |
| 2026-11-20 | 012 | US2: regresión local tras el cambio del Caddyfile | Rutas 42/42, cierre 7/7, acceso 7/7, fotos 180/180 |
| 2026-11-20 | 011 | `/speckit-converge` | 1.ª pasada: T022 (cierre en ROADMAP y estado) y T023 (`research` R3 alineado con `verificar-copia.sh`); 2.ª pasada: Converged |
| 2026-11-20 | 010 | `analyze`: 0 críticos/HIGH; 1 MEDIUM (captura de referencia de SC-005) y 2 LOW corregidos antes de implementar | OK |
| 2026-11-20 | 010 | ruff; pytest (PostgreSQL real): reglamento de 200 000 caracteres, CRLF, respaldo, versión compartida, contacto válido/no válido, alta concurrente, importación sin pisar datos, 405 | **355 passed** (tras la convergencia) |
| 2026-11-20 | 010 | vitest (persistencia y usuario de Instagram), typecheck y build | **69 passed**; OK |
| 2026-11-20 | 010 | Migración 0010 e `importar-inicial` sobre la base existente | Reglamento 2026 y contacto importados |
| 2026-11-20 | 010 | SC-005: texto de `/reglamento`, `/contacto`, `/inscripciones` y `/` (contenido, pie y enlaces) antes y después | Idéntico |
| 2026-11-20 | 010 | `verificar-reglamento-contacto.mjs` (referencia 2026, edición en la edición actual sin tocar 2026, validación sin éxito simulado, contacto en todas las ubicaciones, `mailto`, reinicio, restauración) | 7/7 OK |
| 2026-11-20 | 010 | `/speckit-converge` | 1.ª pasada: T019 (respaldo a la semilla sin reglamento en ninguna edición, con prueba y documentado); 2.ª pasada: Converged |
| 2026-11-20 | 010 | `verificar-acceso.mjs` (paso 4: error real del servidor en `/admin/ajustes`) y regresión: rutas 42/42, admin 2/2, subida 2/2, evento 16/16, inscripciones 16/16, clasificaciones 11/11, noticias 8/8, galería 6/6, entidades 10/10, respaldo 3/3 | OK |
| 2026-11-20 | 009 | Revisión durante la verificación: el error de la web de una entidad decía «álbum externo» | Corregido (`logotipo`, `web de la entidad`) con prueba |
| 2026-11-20 | 007 | Desbordamiento a 4 anchos en `/`, `/noticias` y el detalle; captura de la portada | 0 desbordamientos; cuadrícula aprobada para varias noticias |
| 2026-11-20 | 007 | Regresión: rutas 42/42, evento y carreras 16/16, inscripciones 16/16, clasificaciones 11/11, acceso 7/7 | OK (`verificar-acceso` pasa a usar `/admin/reglamento` como sección sin persistencia; se borraron 2 borradores de prueba creados por la versión anterior del script) |

## Bloqueos

Ninguno para el desarrollo. Antes del lanzamiento, el propietario debe introducir desde el panel
(o facilitar) estos datos de producción:

- fecha y hora de 2027;
- enlaces de inscripción y de pago del Dorsal Solidario;
- webs de los patrocinadores;
- reglamento definitivo de 2027;
- GPX de los recorridos;
- autorizaciones de uso de las imágenes.

## Avisos técnicos menores

- En esta máquina el puerto 8000 del host está ocupado por otro proceso. `compose.dev.yaml` permite
  cambiarlo con `API_PORT_LOCAL` (por ejemplo, `API_PORT_LOCAL=8001`).

- `Site.tsx` (propuesta) no consume el cuerpo de una respuesta de error de `/api/content`, así que
  Chromium deja esa petición abierta. No afecta al usuario. Las verificaciones con la API caída
  esperan al aviso en lugar de a `networkidle`.

- pytest ya no muestra avisos: se usa `httpx2` desde la feature 011.

- Wikiloc responde 403 (desafío anti-bots de Cloudflare) a navegadores automatizados. En las
  pruebas el mapa insertado no carga, pero la CSP no lo bloquea; en un navegador real funciona.

- En local hay 43 archivos subidos por las verificaciones de hoy sin referencias. Pasadas 24 horas,
  `limpiar-archivos --borrar` puede eliminarlos si se desea.
