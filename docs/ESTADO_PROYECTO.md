# Estado del proyecto

Última actualización: 2026-11-21

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
- **US3 terminada** (decisión P7: logotipo nuevo en la cabecera, desde `datos_iniciales/new_logo.png`):
  - Cambio: la cabecera pública muestra el logotipo del propietario en lugar de la silueta y del
    texto en dos filas.
    - Archivos: `reused/logos/logo_cabecera-{480,720}.webp`, de 25 y 39 KB, recortados y en
      WebP.
    - Código: `LogoCabecera` en `Site.tsx` y `ajustes.css` A-005.
    - La altura de la cabecera no cambia; el enlace conserva el ancho de la marca anterior.
  - Fuera (supuesto de la spec): el pie y la barra lateral del panel, con fondo oscuro, siguen
    con la marca blanca; el favicon no cambia.
  - Verificación:
    - `verificar-logo.mjs` en 90 vistas (6 rutas × 15 anchos): 0 px de diferencia, 0
      desbordamientos y nitidez en densidad 2;
    - axe 0;
    - capturas: solo cambia la cabecera, más un reescalado imperceptible del icono del pie;
    - regresión correcta.
  - Publicada en GitHub a petición del propietario: `main` 22aa4f0.
- **US4 terminada** (decisión P8: «pon también el logo en el pie»):
  - Cambio: el pie muestra el logotipo nuevo en negativo (texto y montañas en blanco, naranja
    intacto), derivado del original sin redibujar.
    - Archivos: `reused/logos/logo_pie-{480,720}.webp`, de 17,6 y 27,3 KB.
    - Código: componente `Logo` (cabecera y pie) en `Site.tsx`; `Brand` eliminado;
      `ajustes.css` A-006.
    - Tamaño: 233 px de ancho, el de la marca anterior (228 a 701 px), y 74,8 px de alto.
    - Efecto: el resto de la primera columna baja 22,8 px; el pie crece 0–22,8 px según el ancho.
  - Fuera (supuesto de la spec): la barra lateral del panel conserva la marca blanca; el favicon
    no cambia.
  - Verificación:
    - `verificar-logo.mjs` en 90 vistas: cabecera con 0 px de diferencia; columnas 2.ª–4.ª del pie
      en su sitio; nada baja más de lo que crece la marca;
    - contraste: naranja 5,52:1 y blanco 16,24:1;
    - nitidez en densidad 2 y panel sin cambios;
    - axe 0; 44 capturas sin desbordamientos;
    - caso en que el logotipo no carga: el hueco se conserva;
    - regresión correcta.
  - Herramientas: `cargarTodo` y `verificar-logo` se desplazan de forma instantánea, porque
    `scroll-behavior: smooth` falseaba las medidas y las capturas del pie.
- **US5 terminada** (decisión P9: frase del pie):
  - Cambio: la línea inferior del pie dice «Hecho por la Escuela Hacker Cosío» en lugar de
    «Hecho con pasión por JR BLANCO · Hackers Cosío».
    - Va como texto, sin enlace: la frase nueva no nombra a JR BLANCO y no hay dirección de la
      Escuela.
    - El aviso de copyright y el estilo de la línea no cambian. La regla A-002 del enlace del pie
      se conserva, sin efecto.
  - Verificación:
    - `tests/pie.test.tsx` en 13 rutas: falla antes del cambio y pasa después;
    - `verificar-logo.mjs`, ampliado con la línea inferior: detecta la frase anterior y pasa con la
      nueva en 90 vistas, con el panel sin cambios;
    - axe 0;
    - 44 capturas: solo cambia esa línea, comparadas píxel a píxel con las de la US4;
    - regresión correcta.
- **US6 terminada** (decisión P10: podio destacado en las clasificaciones):
  - Cambio: las filas del 1.º, 2.º y 3.º llevan un fondo suave de oro, plata y bronce, una franja
    a la izquierda y el número dentro de una medalla del mismo color más intenso.
    - Código: `ClassificationTable.tsx` y `ajustes.css` A-007.
    - Los colores los eligió el equipo, porque el propietario los dejó a su elección.
    - El podio es el puesto publicado: con la búsqueda o los filtros, cada fila conserva el suyo.
      No se calculan podios por sexo ni por categoría (supuesto ampliable).
  - Verificación:
    - `tests/podio.test.tsx`: falla antes del cambio y pasa después;
    - `verificar-podio.mjs` contra una referencia previa: 45 filas del podio en 5 anchos, las demás
      sin cambios, filas y tablas con 0 px de diferencia, contraste mínimo de 11,6:1 en el texto y
      de 5,7:1 en las medallas, búsqueda y filtro correctos;
    - axe 0;
    - 44 capturas: solo cambian las 4 de clasificaciones;
    - regresión correcta.
- **US7 terminada** (fallo del panel: la barra lateral no se desplazaba en ventanas bajas):
  - Causa: la barra es fija y ocupa toda la altura, sin desbordamiento propio. Las últimas
    opciones y «Cerrar sesión» quedaban fuera de alcance.
  - Cambio:
    - desplazamiento vertical de la barra, sin arrastrar la página (`ajustes.css` A-008);
    - la opción de la sección abierta queda a la vista (`Admin.tsx`);
    - con altura suficiente, la barra se ve igual que antes.
  - Fallo previo encontrado al verificar: con el menú de móvil abierto, la página se desbordaba
    78 px a 360 px. Corregido con `overflow-x: clip` mientras el menú está abierto.
- **US8 terminada** (decisión P11: logotipo oficial también en el panel):
  - Logotipo en negativo en la barra lateral (180 px, con «ADMINISTRACIÓN» debajo) y en la
    pantalla de acceso (261 px).
  - Componente compartido `LogoImg` (`components/Logo.tsx`).
  - `logo1.webp` queda solo como favicon.
- **Verificación de la US7 y la US8**:
  - `verificar-panel.mjs`, con una referencia previa:
    - con la versión previa detecta los dos fallos;
    - con la nueva todo se alcanza con el teclado y con la rueda en 8 ventanas, sin
      desbordamientos;
    - barra, contenido y formulario en su sitio y logotipo correcto;
    - axe 0 en la barra lateral.
  - Cabecera y pie públicos con 0 px de diferencia.
  - Acceso, panel, axe, capturas (0 cambios en la web pública) y regresión correctos.
- **US9 terminada** (el propietario pidió corregir el contraste del panel; decisión P4):
  - Auditoría (`verificar-panel-aa.mjs`): axe con la sesión iniciada en 69 vistas. Son 22 rutas
    a 360, 1024 y 1440 px y 3 estados de guardado, con las escrituras interceptadas.
  - Antes: 222 incumplimientos, de solo 2 defectos:
    - las cabeceras de las tablas de listados, a 3,40:1;
    - el pie del panel, a 2,67:1.
  - Cambio (`ajustes.css` A-009): los dos textos pasan a `--muted` (#66716b), con 4,88:1 y
    4,63:1. Tamaños, pesos y fondos no cambian.
  - Después: 0 incumplimientos en las 69 vistas.
  - Ningún dato cambió durante la revisión (comprobado en la API).
  - Capturas: solo cambian esos textos.
  - Regresión correcta.
- **Publicación**: la US3 está en GitHub (`main` 22aa4f0). Las US4–US9 están solo en local, en
  `012-ajustes-revision` y fusionadas en `main`. Se suben cuando el propietario lo pida.
- **Siguiente acción concreta**:
  1. El propietario despliega en la MV siguiendo `docs/operacion.md` §12. El código ya está en
     GitHub (`main`, push del 2026-11-20 a petición del propietario).
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
| 2026-11-21 | Contraste AA también en el panel con la sesión iniciada: cabeceras de tabla y pie del panel en `--muted` | Propietario (P4, confirmado para el panel), 012 research R9 |
| 2026-11-21 | Logotipo oficial en negativo en la barra lateral del panel (con «ADMINISTRACIÓN») y en el acceso; favicon sin cambios | Propietario (P11), 012 research R8 |
| 2026-11-21 | Barra lateral del panel con desplazamiento vertical propio, sin arrastrar la página; opción abierta a la vista | 012 US7, research R8 |
| 2026-11-21 | Podio de las clasificaciones en oro, plata y bronce suaves (fondo, franja y medalla) por el puesto publicado; sin podios por sexo ni categoría | Propietario (P10), 012 research R7 |
| 2026-11-21 | Frase del pie «Hecho por la Escuela Hacker Cosío», sin enlace (no hay dirección aprobada) | Propietario (P9), 012 research R6 |
| 2026-11-21 | Logotipo también en el pie, en negativo (tinta oscura → blanco, naranja intacto), con el ancho de la marca anterior; el panel conserva la marca blanca | Propietario (P8), 012 research R5 |
| 2026-11-21 | Logotipo nuevo en la cabecera pública; el pie y el panel conservan la marca blanca | Propietario (P7), 012 research R4 |

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
| 2026-11-21 | 012 | US3 (P7): `verificar-logo.mjs` contra la referencia previa (6 rutas × 15 anchos, incluidos los dos lados de cada cambio de diseño, y la barra del panel con `/pantallas` en local) | 90/90: logotipo completo y sin deformar, sin texto de marca; cabecera, navegación, INSCRIPCIONES y menú con 0 px de diferencia; pie y panel iguales; variantes de 25 y 39 KB; densidad 2 con resolución suficiente |
| 2026-11-21 | 012 | US3: axe y desbordamiento; capturas antes y después (44) | 0 incumplimientos; 0 desbordamientos; solo cambia la cabecera. A 1440 px, el icono del pie (mismo `logo1.webp`) se reescala distinto (máximo 36/255 en 55 × 29 px, imperceptible) porque ya no comparte la imagen decodificada con la cabecera |
| 2026-11-21 | 012 | US3: logotipo que no carga (petición abortada, 360 y 1440 px) | Cabecera con la misma altura, INSCRIPCIONES en su sitio, enlace a la portada con su nombre accesible; favicon sin cambios (`logo1.webp`) |
| 2026-11-21 | 012 | US3: regresión (vitest, typecheck, build, rutas, cierre, fotos) | 75 passed; OK; 42/42; 7/7; 100/100 fotos sin el panel |
| 2026-11-21 | 012 | US4 (P8): `verificar-logo.mjs` contra una referencia previa nueva (`pie-antes-012.json`, 6 rutas × 15 anchos y barra del panel con `/pantallas` en local) | Cabecera con 0 px de diferencia; logotipo del pie completo, sin deformar y no más ancho que la marca anterior ni que su columna; columnas 2.ª–4.ª con la misma `x` y el mismo ancho; bajada máxima de 22,8 px (= lo que crece la marca); 0 desbordamientos; variantes de 17,6 y 27,3 KB; densidad 2 correcta; contraste naranja 5,52:1 y blanco 16,24:1; panel sin cambios |
| 2026-11-21 | 012 | US4: axe y desbordamiento; capturas (44) y revisión visual del pie a 360, 768, 1024 y 1440 px | 0 incumplimientos en 17 rutas; 0 desbordamientos; solo cambia el pie |
| 2026-11-21 | 012 | US4: logotipo del pie que no carga (petición abortada, 360 y 1440 px) | Mismo hueco (74,8 px) y párrafo en el mismo sitio; enlace a la portada con su nombre accesible |
| 2026-11-21 | 012 | US4: regresión (vitest, typecheck, build, rutas, cierre, fotos) | 75 passed; OK; 42/42; 7/7; 100/100 fotos sin el panel |
| 2026-11-21 | 012 | US5 (P9): `tests/pie.test.tsx` (13 rutas públicas, incluida una inexistente), antes y después del cambio | Antes: 13 fallos (frase anterior con enlace). Después: 13 passed |
| 2026-11-21 | 012 | US5: `verificar-logo.mjs --comparar` ampliado con la línea inferior del pie (6 rutas × 15 anchos y barra del panel con `/pantallas` en local) | Con la versión previa detecta la frase anterior. Con la nueva: frase correcta, sin enlaces, mismo estilo, sin restos; cabecera con 0 px de diferencia y pie como en la US4; panel sin cambios |
| 2026-11-21 | 012 | US5: axe y desbordamiento; 44 capturas, comparadas píxel a píxel con las de la US4 y revisión visual del pie a 360, 768 y 1440 px | 0 incumplimientos en 17 rutas; 0 desbordamientos; solo cambia la línea inferior del pie y ninguna página cambia de alto |
| 2026-11-21 | 012 | US5: regresión (vitest, typecheck, build, rutas, cierre, fotos) | 88 passed; OK; 42/42; 7/7; 100/100 fotos sin el panel |
| 2026-11-21 | 012 | US6 (P10): `tests/podio.test.tsx` (puestos 1–3, empate, vista previa y sin puestos), antes y después del cambio | Antes: 2 fallos. Después: 3 passed |
| 2026-11-21 | 012 | US6: `verificar-podio.mjs` contra una referencia previa (`podio-antes-012.json`; `/clasificaciones/2026` a 320, 360, 768, 1024 y 1440 px, 8 primeras filas de las 3 tablas) | Con la versión previa, 136 problemas. Con la nueva: 45 filas del podio con su fondo, su franja y su medalla; 75 filas sin cambios; filas y tablas con 0 px de diferencia; contraste mínimo de 11,62:1 (texto) y 5,68:1 (medallas). La búsqueda del ganador conserva el oro; el filtro «Femenino» no colorea las primeras filas |
| 2026-11-21 | 012 | US6: axe y desbordamiento; 44 capturas comparadas píxel a píxel con las de la US5; revisión visual de la tabla a 360 y 1440 px | 0 incumplimientos en 17 rutas; 0 desbordamientos; solo cambian las 4 capturas de clasificaciones, con el mismo alto |
| 2026-11-21 | 012 | US6: regresión (vitest, typecheck, build, rutas, cierre, fotos) | 91 passed; OK; 42/42; 7/7; 100/100 fotos sin el panel |
| 2026-11-21 | 012 | US7 y US8: `verificar-panel.mjs` contra una referencia previa (`panel-antes-012.json`; acceso a 7 anchos; barra lateral en 8 ventanas de 1440×900 a 360×480, con el menú de móvil abierto) | Con la versión previa, 66 problemas: opciones y «Cerrar sesión» inalcanzables, rueda que mueve la página y marca antigua. Con la nueva: 7 ventanas con desplazamiento y todo alcanzable con el teclado y con la rueda, sin mover la página; 1 sin él, como antes; «Ajustes» a la vista; sin desplazamiento horizontal; logotipo oficial con «ADMINISTRACIÓN»; barra, contenido y formulario en su sitio (bajada máxima de 28,8 px); densidad 2 correcta; axe 0 en la barra lateral |
| 2026-11-21 | 012 | US8: `verificar-logo.mjs --comparar` (con `/pantallas` en local) | Cabecera y pie públicos con 0 px de diferencia tras extraer `LogoImg`; barra del panel con el logotipo oficial |
| 2026-11-21 | 012 | US7 y US8: `verificar-acceso.mjs`, `verificar-admin.mjs`, axe (17 rutas) y 44 capturas comparadas con las de la US6 | Todo correcto; 0 incumplimientos; 0 desbordamientos; 0 capturas públicas cambian |
| 2026-11-21 | 012 | US8: logotipo que no carga (petición abortada) en el acceso y en el panel | Enlaces con su nombre accesible; «ADMINISTRACIÓN» visible |
| 2026-11-21 | 012 | US7 y US8: axe con la sesión iniciada en todo el panel (1440×560 y 360×640) | 0 en la barra lateral. En el contenido, contraste previo: cabeceras de «Últimas noticias» a 3,39:1 y pie del panel a 2,66:1 (corregido en la US9) |
| 2026-11-21 | 012 | US7 y US8: regresión (vitest, typecheck, build, rutas, cierre, fotos con el panel) | 91 passed; OK; 42/42; 7/7; 180/180 fotos con el panel |
| 2026-11-21 | 012 | US9: `verificar-panel-aa.mjs` (axe con la sesión iniciada: 22 rutas × 360/1024/1440 px y 3 estados de guardado, con las escrituras interceptadas), antes y después del cambio | Antes: 222 incumplimientos en 69 vistas (2 defectos: cabeceras de tabla a 3,40:1 y pie del panel a 2,67:1). Después: 0 en 69 vistas; 3 escrituras interceptadas; datos sin cambios en la API |
| 2026-11-21 | 012 | US9: capturas del panel antes y después (6 pantallas a 1440 y 360 px) | Solo cambian la fila de cabeceras de la tabla y el pie, sin cambios de tamaño, más 1 píxel de rasterizado del logotipo (2/255) |
| 2026-11-21 | 012 | US9: regresión (`verificar-panel`, axe público, vitest, typecheck, rutas, cierre) | OK; 0 incumplimientos en 17 rutas; 91 passed; OK; 42/42; 7/7 |
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
