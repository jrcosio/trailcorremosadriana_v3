# CLAUDE.md

Este repositorio contiene la web pública y el panel de administración de «Trail Peñasagra —
Corremos por Adriana», una carrera solidaria de montaña en Cosío (Rionansa, Cantabria). Todo está
en español: la documentación, el código, los identificadores, los mensajes y los commits.

## Antes de empezar

1. Lee el **punto de continuidad** de `docs/ESTADO_PROYECTO.md`: estado, feature activa, últimas
   publicaciones y siguiente acción.
2. La feature activa de Spec Kit está en `.specify/feature.json`, no en el nombre de la rama.
3. `.specify/memory/constitution.md` prevalece sobre cualquier otra práctica. Las decisiones del
   propietario (P1, P2…) están en `docs/referencia/DISCREPANCIAS.md`.

Orden de autoridad: propietario > decisiones aprobadas (`docs/referencia/`) > código de la
propuesta > código de producción.

## Reglas que no se negocian

- **Git**:
  - rama por feature (`NNN-nombre`), commits locales y merge `--no-ff` a `main`;
  - **push solo cuando el propietario lo pida**;
  - nunca despliegues, cambios de dominio ni acciones en producción.
- **Secretos**: nunca se versionan `.env` reales, contraseñas ni credenciales.
- **`.env.produccion`**: está en la raíz, fuera de Git y con permisos 600. Es el `.env` de la MV.
  - No lo renombres a `.env` aquí: Compose lo leería y rompería el Docker local.
  - No muestres su contenido en el chat.
- **`datos_iniciales/`**: referencia de solo lectura, ignorada por Git y por Docker.
  - Contiene las fuentes, los CSV con datos personales y la web anterior (v2).
  - El proyecto funciona sin ella. No copies sus `.git`, `.env`, sesiones ni bases.
- **Datos reales**: no inventes participantes, tiempos, fechas oficiales, patrocinadores,
  colaboradores ni enlaces de inscripción o pago.
- **Lo que se publica**:
  - los borradores nunca salen en la API pública;
  - las vistas de demostración (`/pantallas/admin`) no guardan nada;
  - el contacto usa `mailto` mientras no se apruebe otro servicio.
- **Diseño**: se conservan las URLs y las pantallas aprobadas. Un cambio visual sustancial exige
  una instrucción nueva del propietario.
- **Operaciones destructivas**: no descartes cambios del usuario ni ejecutes `down -v`,
  `reset --hard` o borrados en la base local sin que lo pida.
- **Autonomía**: no preguntes «¿continúo?» entre fases. Pregunta solo por una decisión de
  producto que cambie el comportamiento y no se pueda deducir, o por un bloqueo que requiera al
  propietario.
- **Terminado = comprobado**: no declares terminado lo que no has ejecutado. Un checklist se marca
  solo con evidencia.

## Flujo de trabajo (Spec Kit)

Cada feature pasa por `/speckit-specify` → `clarify` (si procede) → `plan` → `checklist` (si
aporta) → `tasks` → `analyze` → `implement` → pruebas → `converge`.

- **Ajustes nuevos del propietario**: se añaden como historias (US13, US14…) de la feature 012
  en `specs/012-ajustes-revision/`:
  - `spec.md`: escenarios, FR y SC;
  - `research.md`: la decisión técnica (R#);
  - `plan.md`, con el Constitution Check;
  - `tasks.md`: las tareas (T#);
  - `quickstart.md` y una nota en `checklists/requirements.md`.
- **Decisiones del propietario**:
  - cada una se registra como P# en `docs/referencia/DISCREPANCIAS.md`;
  - si cambia algo aprobado, se anota en `docs/referencia/`;
  - si toca un principio, se enmienda también la constitución, con versión semántica.
- **Seguimiento**: `docs/ROADMAP.md` y el punto de continuidad de `docs/ESTADO_PROYECTO.md` se
  actualizan en cada fase y al terminar cada historia, con las pruebas ejecutadas y sus
  resultados.
- **Commits**: `feat(012): … (US12)`, `fix(012): … (US11, decisión P13)` o `docs(012): …`.

## Comandos

Desarrollo (la web queda en <http://localhost:8080>; detalle en `docs/desarrollo.md`):

```bash
docker compose build
docker compose up -d db
docker compose run --rm api alembic upgrade head                 # nunca se migra al arrancar
docker compose run --rm api python -m app.cli importar-inicial   # solo rellena lo vacío
docker compose up -d
docker compose -f compose.yaml -f compose.dev.yaml up -d   # + /pantallas, API y BD en 127.0.0.1
docker compose run --rm api python -m app.cli --help       # crear-admin, listar-admins, importar-clasificacion…
```

Pruebas y lint:

```bash
# Backend: pytest contra PostgreSQL real (bases temporales trail_test_*) y S3 simulado (moto)
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm api-test pytest tests/test_csv.py -k longitud
cd backend && uvx ruff@0.17.6 check . && uvx ruff@0.17.6 format --check .

# Frontend (vitest en frontend/tests)
cd frontend && npm run typecheck && npm test && npm run build
cd frontend && npx vitest run tests/ortografia.test.tsx
```

Las verificaciones en navegador usan Playwright. Se ejecutan desde `frontend/`, con Compose en
marcha y contra `http://localhost:8080` por defecto:

```bash
node scripts/verificar-rutas.mjs
node scripts/verificar-accesibilidad.mjs            # axe WCAG A/AA y desbordamiento
node scripts/capturas.mjs http://localhost:8080 capturas/<nombre>
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-<area>.mjs
```

Cada feature e historia tiene su `verificar-*.mjs`, que deja los datos como estaban. Antes de un
cambio visual, guarda capturas o medidas de referencia del estado anterior.

## Arquitectura

```text
Navegador → web (Caddy) ─┬─ /api/*, /media/* → api (FastAPI :8000) → db (PostgreSQL 17)
                         └─ resto → frontend/dist (un HTML por ruta + SPA)
```

- **Servicios**: todo se sirve desde el mismo origen; `api` y `db` solo están en la red interna.
- **Producción**: `compose.produccion.yaml` añade HTTPS automático, `www` → 301, `PANTALLAS=no` y
  secretos obligatorios.
- **Frontend** (`frontend/src`): React 19 + Vite 8, con el alias `@` → `src`.
  - `components/Site.tsx`: toda la web pública, con un router propio por `path` (enlaces `<a>`
    que recargan la página).
  - `components/admin/Admin.tsx`: el panel. Guarda un `SiteData` completo, y `guardarCambios` (en
    `lib/persistencia.ts`) lo reparte en llamadas por recurso a `/api/admin/...`. Cada sección
    editable nueva necesita su recurso ahí.
  - `lib/`:
    - `classifications.ts`: los CSV de clasificaciones;
    - `textosPanel.ts`: los textos de cada sección, con su género;
    - `fotos.ts`: `fondoFoto`;
    - `data.ts`: la semilla de respaldo si la API cae.
  - `plugins/metadatos-rutas.ts`: genera en el build los HTML por ruta, `plantilla.html`,
    `404.html` y `app.html`.
  - Estilos:
    - `styles/globals.css` es la propuesta aprobada y **no se toca**;
    - cada arreglo va en `styles/ajustes.css`, con su referencia (A-001…A-009) y su decisión.
- **Backend** (`backend/app`):
  - `api/`: las rutas. Las `admin_*` exigen sesión, CSRF y Origin;
  - `services/`: la lógica;
  - `models/`: SQLAlchemy;
  - `schemas/`: Pydantic;
  - `core/`: configuración, BD y seguridad;
  - `storage/`: almacenamiento local o S3;
  - `cli.py`: las órdenes de operador.

  Las migraciones están en `backend/alembic/versions/` (`NNNN_nombre.py`).
  `seed/contenido_inicial.json` tiene los datos aprobados.
- **Contratos**: el frontend lee de `GET /api/content` (con `?admin=1`, el panel); no existe
  `PUT /api/content`. Los contratos de cada feature están en `specs/*/contracts/`.
- **Infra**:
  - `infra/caddy/`: Caddyfile, CSP y redirección de `www`;
  - `infra/scripts/`: `backup.sh`, `restore.sh` y `verificar-copia.sh`;
  - `deploy.sh`: instala o actualiza la MV (`docs/operacion.md` §0).

Más detalle en `docs/arquitectura.md`. La operación y el despliegue están en `docs/operacion.md`.

## Convenciones

- **Ortografía**: español correcto en todo lo visible, con tildes, «ñ», signos de apertura
  (¿ ¡) y comillas «». La portada dice «TRAIL PEÑASAGRA» (decisión P13);
  `frontend/tests/ortografia.test.tsx` lo comprueba.
- **Errores de la API**: `{"error": "…"}`, en español y con el nombre del campo que ve el
  usuario.
- **Concurrencia**: los recursos editables llevan `version`. Ante un conflicto se responde 409,
  sin sobrescribir.
- **Fechas del evento**: en Europe/Madrid, guardadas con zona. La API devuelve ISO UTC.
- **Importaciones**: idempotentes. Solo sustituyen contenido con una acción explícita
  (`--reemplazar`, `--sustituir`).
- **CSP**: no permite scripts ni estilos en línea. Los estilos dinámicos van por CSSOM (la prop
  `style` de React), nunca como `<style>` ni atributo `style` en el HTML estático.
- **Comentarios**: en español. Explican el porqué y citan la historia o decisión de origen, por
  ejemplo `Feature 012 · US11 (decisión P13)`.
- **Revisión visual** (constitución I):
  - anchos de 360, 768, 1024 y 1440 px, más 320 si afecta a la cabecera;
  - sin desbordamiento horizontal y con axe a 0 incumplimientos AA (decisión P4);
  - capturas antes y después en las que solo cambie lo previsto.

## Trampas conocidas

- **Acceso bloqueado**: tras 8 accesos fallidos al panel en local, se desbloquea con
  `docker compose exec db psql -U trail -c 'DELETE FROM limites_login'`.
- **Scripts con condiciones**:
  - `verificar-respaldo.mjs` se ejecuta con la API parada (`docker compose stop api`);
  - `verificar-reglamento-contacto.mjs` reinicia la API;
  - `verificar-cierre.mjs` cambia `PANTALLAS` y la deja como estaba.
- **Desplazamiento en Playwright**: con `behavior: 'instant'` (`cargarTodo` en
  `scripts/comun.mjs`). `scroll-behavior: smooth` falsea las medidas y las capturas.
- **Varios `-f` de Compose**: usa una función, `dc() { docker compose -f … "$@"; }`. Una
  variable `$DC` no funciona en zsh, que no la parte en palabras.
- **bash 3.2**: `deploy.sh` y `infra/scripts/*.sh` deben funcionar con él:
  - `${VAR}` entre llaves si le sigue un carácter no ASCII (`${USUARIO}»`);
  - `${@+"$@"}` con `set -u`;
  - sin `xargs -r`.

  Se comprueban con `uv run --with shellcheck-py shellcheck deploy.sh`.
- **Ensayos de despliegue**: van en un clon aparte, con otro `COMPOSE_PROJECT_NAME`, y se retiran
  con `down -v` solo de ese proyecto. El Docker local (`trail-penasagra`, puerto 8080) no se toca.
  Los dominios `.localhost` usan la CA interna de Caddy (`curl -k`).
- **Dominio real**: `trailpeñasagra.com`, en *punycode* `xn--trailpeasagra-okb.com`.
- **Migraciones pendientes**: `/api/ready` responde `migraciones_pendientes` hasta ejecutar
  `alembic upgrade head`.
