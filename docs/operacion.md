# Operación y despliegue independiente

Guía para instalar, mantener y recuperar la web **Trail Peñasagra — Corremos por Adriana** en un
servidor propio. Probada en dos ensayos locales desde un clon limpio:

- el de la feature 011 (sección 11);
- el ensayo en modo producción con HTTPS y un dominio con «ñ» de la feature 012 (sección 14).

Nada de esta guía se ha ejecutado contra el dominio ni la producción real.

> **Lo más sencillo: `deploy.sh`** (sección 0). Instala o actualiza todo con una orden, también
> cuando sustituye a la web anterior en su misma MV. Las secciones 2–12 explican los mismos pasos a
> mano. **¿Cómo entro al panel?** Lo explica la **sección 13**.

> Todos los comandos se ejecutan en la carpeta del repositorio. En producción, añade siempre
> `-f compose.yaml -f compose.produccion.yaml`. En esta guía se hace con la función `dc`, que
> funciona igual en bash y en zsh (una variable `dc` con espacios no funciona en zsh):

```bash
dc() { docker compose -f compose.yaml -f compose.produccion.yaml "$@"; }
```

## 0. Despliegue automático con `deploy.sh`

Feature 012, US12. Ensayado en local con una web anterior simulada (ver `docs/ESTADO_PROYECTO.md`).

**Primera vez** (como root o con `sudo`):

```bash
git clone https://github.com/jrcosio/trailcorremosadriana_v3.git /srv/trail-v3
# desde tu ordenador, el .env de producción preparado para la MV:
scp .env.produccion <usuario>@<mv>:/srv/trail-v3/.env
# en la MV:
cd /srv/trail-v3 && sudo ./deploy.sh
```

**Cada actualización**: `cd /srv/trail-v3 && sudo ./deploy.sh`. El script descarga el código nuevo
y, si `deploy.sh` ha cambiado, se relanza con la versión nueva.

**Qué hace, en orden** (se puede repetir sin riesgo):

1. Comprueba Docker y Compose 2.24 o posterior, el `.env` (lo deja con permisos 600) y la
   configuración de producción.
2. Descarga el código (`git pull --ff-only`). Se detiene si hay cambios locales en archivos del
   repositorio. `--sin-descargar` se salta este paso.
3. Si ya hay una base en marcha, hace una copia (`infra/scripts/backup.sh`) en `COPIAS_DIR`.
4. Construye las imágenes, arranca la base y aplica las migraciones.
5. **Solo si la base está vacía** (sin ediciones):
   - importa los datos aprobados;
   - importa las 3 clasificaciones de 2026, que busca en `CSV_2026_DIR` o en la carpeta de la web
     anterior (`datos/2026`). Si no las encuentra, avisa: se pueden subir desde el panel.

   Con datos, no importa nada ni sobrescribe.
6. Si no hay ninguna cuenta del panel, crea `ADMIN_USUARIO` con `ADMIN_PASSWORD`. Si ya hay
   cuentas, no cambia ninguna contraseña.
7. Detecta otra web (otro proyecto de Docker) que ocupe los puertos 80/443, como la v2, y la para
   con `docker compose down`, **sin `-v`**, así que sus datos se conservan. Anota cuál era en
   `.despliegue/web-anterior`. Si los puertos los ocupa un programa que no es Docker, se detiene
   sin arrancar.
8. Arranca la web y espera hasta 180 s (`DEPLOY_ESPERA`) a que
   `https://<dominio>/api/ready` responda «disponible», con su certificado. **Si no responde y
   había parado la web anterior, la vuelve a arrancar** y termina con error: la web nueva queda
   parada con sus datos.
9. Repite las comprobaciones de la sección 6 e informa de cada una:
   - HTTP a HTTPS y `www` al dominio principal;
   - las cabeceras de seguridad;
   - 404 en `/no-existe` y en `/pantallas`;
   - el esquema en `head`;
   - el emisor del certificado.
10. Programa la copia diaria a las 04:00 en el crontab de quien lo ejecuta y conserva 14 días; el
    registro queda en `COPIAS_DIR/copias.log`. No duplica la tarea ni toca las demás. Con
    `COPIAS_PROGRAMADAS=no`, no la programa. Al final, borra las imágenes de Docker huérfanas.

Al terminar muestra la dirección de la web y del panel, el usuario y la orden exacta para volver a
la web anterior. Cada ejecución deja su registro en `COPIAS_DIR/despliegue-AAAAMMDD-HHMMSS.log`.

**Variables del `.env` que solo usa `deploy.sh`** (Compose no las pasa a los contenedores):

| Variable | Uso |
|---|---|
| `ADMIN_USUARIO`, `ADMIN_PASSWORD` | Cuenta del panel que se crea si no hay ninguna. Después se puede borrar `ADMIN_PASSWORD` del `.env` |
| `COPIAS_DIR` | Copias y registros (por defecto `/srv/copias-trail`) |
| `COPIAS_PROGRAMADAS` | `si` (por defecto) o `no` |
| `WEB_ANTERIOR_DIR`, `CSV_2026_DIR` | Solo si no detecta sola la carpeta de la web anterior o los CSV |

**Volver a la web anterior** (lo que imprime el script al final):

```bash
cd /srv/trail-v3 && docker compose -f compose.yaml -f compose.produccion.yaml down
cd <carpeta de la v2> && docker compose -p <proyecto de la v2> up -d
```

## 1. Requisitos

- Servidor Linux con Docker Engine 24 o posterior y Docker Compose v2.24 o posterior.
- 2 GB de RAM y 10 GB de disco libres (más el espacio de las fotos si se usa almacenamiento local).
- Dominio con registros DNS `A` (y `AAAA` si hay IPv6) apuntando al servidor.
- Puertos 80 y 443 abiertos (TCP; 443 también UDP para HTTP/3).
- Un bucket de Cloudflare R2 (recomendado) o espacio en disco para las fotos.

## 2. Instalación

1. **Clonar el repositorio.** `datos_iniciales/` no forma parte del repositorio ni hace falta.
2. **Crear `.env`** a partir de `.env.example` y fijar como mínimo:

   | Variable | Producción |
   |---|---|
   | `POSTGRES_DB`, `POSTGRES_USER` | Nombres a elegir |
   | `POSTGRES_PASSWORD` | Secreto aleatorio: `openssl rand -base64 32` |
   | `PUBLIC_ORIGIN` | `https://<dominio>`, en *punycode* si el dominio lleva «ñ»: `https://xn--trailpeasagra-okb.com`. La API lo normaliza igualmente, pero el *punycode* evita dudas |
   | `SITE_ADDRESS` | `<dominio>`, solo el principal, sin `https://` ni `www`: `xn--trailpeasagra-okb.com` |
   | `ALMACENAMIENTO` | `s3` (R2) o `local` |
   | `S3_*` | Solo con R2 (sección 4) |
   | `SESSION_HOURS`, `LOGIN_*`, `UPLOAD_MAX_BYTES` | Por defecto, salvo necesidad |

   `compose.produccion.yaml` fija `ENTORNO=produccion`, `COOKIE_SECURE=true` y `PANTALLAS=no`,
   y publica los puertos 80 y 443. Si falta una variable obligatoria, Compose se detiene con un
   error que la nombra. `.env` **nunca** se versiona ni se copia fuera del servidor.
3. **Comprobar la configuración** sin arrancar nada: `dc config > /dev/null`.
4. **Varias instalaciones en el mismo servidor** (por ejemplo, un ensayo): define en `.env` un
   `COMPOSE_PROJECT_NAME` distinto en cada una. Así cada instalación tiene sus propios
   contenedores y volúmenes, y los scripts de copia actúan sobre la suya. Compruébalo con
   `docker compose config --format json | grep '"name"'` antes de restaurar nada.

## 3. Dominio y HTTPS

- Caddy obtiene y renueva los certificados automáticamente para `SITE_ADDRESS` cuando el DNS ya
  apunta al servidor y los puertos 80 y 443 están abiertos.
- Los certificados se guardan en el volumen `caddy_data`: **no borres ese volumen**, porque
  forzaría a pedirlos de nuevo y hay límites de emisión.
- **`www.<dominio>`**: `compose.produccion.yaml` monta `infra/caddy/redireccion-www.caddy`, que
  pide su certificado y redirige con 301 al dominio principal, conservando la ruta, como hacía la
  web anterior. El DNS de `www` también debe apuntar a la MV.
- **HTTP**: redirige a HTTPS automáticamente. Las respuestas llevan
  `Strict-Transport-Security: max-age=31536000`, sin incluir otros subdominios.
- **Dominio con «ñ»**: Caddy acepta el nombre con «ñ» o en *punycode*. La API compara el origen
  del panel en *punycode*, que es lo que envían los navegadores.
- Las cookies del panel exigen HTTPS (`COOKIE_SECURE=true`). En producción no se puede usar el
  panel por HTTP.

## 4. Almacenamiento de fotos en Cloudflare R2

1. Crea un bucket privado (p. ej. `trail-penasagra-media`). Los archivos siempre se entregan a
   través de la API (`/media/...`); el bucket **no** necesita acceso público.
2. Crea un token de API de R2 con permiso de lectura y escritura de objetos solo para ese bucket.
3. En `.env`:
   - `ALMACENAMIENTO=s3`;
   - `S3_ENDPOINT_URL=https://<cuenta>.r2.cloudflarestorage.com`;
   - `S3_BUCKET`, `S3_REGION=auto`, `S3_ACCESS_KEY_ID` y `S3_SECRET_ACCESS_KEY`;
   - `S3_CREAR_BUCKET=false`.
4. **Copias de R2**: activa el versionado de objetos o una réplica a otro bucket. Como
   alternativa, programa un `rclone sync` diario a otro almacenamiento. `backup.sh` no copia R2.

## 5. Primera puesta en marcha (base nueva)

```bash
dc build
dc up -d db
dc run --rm api alembic upgrade head                  # esquema (paso explícito)
dc run --rm api python -m app.cli importar-inicial    # datos aprobados (solo partes vacías)
dc run --rm api python -m app.cli crear-admin <usuario>   # pide la contraseña (12–128)
dc up -d
```

- Para cargar clasificaciones desde un CSV:
  `dc run --rm -T api python -m app.cli importar-clasificacion --carrera trail-27k --edicion 2026 --titulo "…" --archivo original.csv --publicar < original.csv`.
- **Alternativa**: si se parte de una copia existente (por ejemplo, la del entorno de revisión con
  las clasificaciones de 2026 ya importadas), sigue la sección 7 en lugar de `importar-inicial`.

## 6. Comprobaciones después de desplegar

| Comprobación | Resultado esperado |
|---|---|
| `curl -s https://<dominio>/api/ready` | `{"estado":"disponible", …}` |
| `curl -sI https://<dominio>/` | 200 con `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options` y `Referrer-Policy` |
| `curl -sI http://<dominio>/` | 308 a `https://<dominio>/` |
| `curl -sI https://www.<dominio>/noticias` | 301 a `https://<dominio>/noticias` |
| `echo \| openssl s_client -connect <dominio>:443 -servername <dominio> 2>/dev/null \| openssl x509 -noout -issuer -dates` | Emisor Let's Encrypt; vigente |
| `curl -s -o /dev/null -w '%{http_code}' https://<dominio>/no-existe` | `404` |
| `curl -s -o /dev/null -w '%{http_code}' https://<dominio>/pantallas` | `404` (P5) |
| `curl -s https://<dominio>/noticias/<id>` | Título y `og:*` propios en el HTML |
| `/admin` | Acceso con la cuenta creada; cookie `penasagra_admin` con `Secure` y `HttpOnly` |
| Subir una imagen desde el panel | Se ve en la web (`/media/…`) |
| `dc run --rm api alembic current` | Revisión en la cabeza (`head`) |

## 7. Copias de seguridad y restauración

**Copia** (base de datos y, con `ALMACENAMIENTO=local`, archivos):

```bash
infra/scripts/backup.sh /ruta/copias      # trail-AAAAMMDD-HHMMSS.dump [+ media-….tgz]
```

- Programa la copia diaria con cron, por ejemplo
  `0 4 * * * cd /srv/trail && infra/scripts/backup.sh /srv/copias >> /var/log/trail-copias.log 2>&1`.
- Conserva al menos 14 días y guarda una copia fuera del servidor.

**Restauración** (sustituye la base actual; pide escribir `RESTAURAR`):

```bash
dc up -d db api                       # la API debe estar en marcha para restaurar archivos
infra/scripts/restore.sh /ruta/trail-….dump [/ruta/media-….tgz]
dc run --rm api alembic upgrade head  # por si la copia es de una versión anterior
dc up -d
```

- La restauración funciona igual sobre una base nueva (servidor nuevo) que sobre una existente.
- Restaurar los archivos **añade y sobrescribe**; no borra los archivos que no estén en la copia.
- **Verificación periódica** (en un entorno de pruebas, nunca en producción):
  `infra/scripts/verificar-copia.sh`. Hace una copia, cambia datos, restaura y compara las
  huellas de cada tabla y de cada archivo.

## 8. Actualizar a una versión nueva

Con `sudo ./deploy.sh` (sección 0) estos pasos se hacen solos. A mano:

1. Haz una copia (sección 7).
2. Descarga el código: `git pull` o la etiqueta de la versión.
3. Construye y migra:

   ```bash
   dc build
   dc run --rm api alembic upgrade head
   dc up -d
   ```

4. Repite las comprobaciones de la sección 6.

**Volver atrás**: código anterior (`git checkout <versión>`), `dc build` y restauración de la
copia del paso 1.

## 9. Recuperar el acceso al panel

| Situación | Comando |
|---|---|
| Contraseña olvidada | `dc run --rm api python -m app.cli restablecer-password <usuario>` (revoca sus sesiones) |
| Sospecha de sesión robada | `dc run --rm api python -m app.cli revocar-sesiones <usuario>` |
| Cuenta desactivada | `dc run --rm api python -m app.cli activar <usuario>` |
| Ver las cuentas | `dc run --rm api python -m app.cli listar-admins` |
| Nueva cuenta | `dc run --rm api python -m app.cli crear-admin <usuario>` |

Tras 8 intentos fallidos en 15 minutos desde la misma IP, el acceso se bloquea hasta que pasa la
ventana (`LOGIN_MAX_INTENTOS` y `LOGIN_VENTANA_MINUTOS`). No hay recuperación por correo: la web no
envía correo (constitución VI).

## 10. Mantenimiento

- **Archivos subidos sin uso**: `dc run --rm api python -m app.cli limpiar-archivos` lista los
  archivos sin referencias con más de 24 horas. Con `--borrar` los elimina después de escribir
  `BORRAR`. Haz antes una copia.
- **Registros**: `dc logs --since 24h api web`.
- **Vistas de revisión `/pantallas`**: desactivadas en producción. Para revisarlas en local,
  `PANTALLAS=si` (lo hace `compose.dev.yaml`).

## 11. Ensayo de despliegue (feature 011)

El ensayo se hizo en la máquina de desarrollo, sin servidor ni dominio real:

1. **Clon limpio** de la rama en una carpeta temporal.
2. **`.env` propio**: `COMPOSE_PROJECT_NAME=trail-ensayo`, `WEB_PORT=8090`,
   `PUBLIC_ORIGIN=http://localhost:8090` y contraseña aleatoria.
3. **Sin `compose.produccion.yaml`**, porque no hay dominio para HTTPS.
4. **Pasos 2, 5 y 7**: restauración de una copia del entorno de desarrollo sobre la base nueva.
5. **Comprobaciones**: las de la sección 6 que no dependen de HTTPS.
6. **Retirada**: `docker compose -p trail-ensayo down -v`. Solo elimina los volúmenes del ensayo;
   el entorno de desarrollo (`trail-penasagra`) no se toca.

**Resultado (2026-11-20)**:

| Comprobación | Valor |
|---|---|
| Clon limpio (sin `datos_iniciales` ni `.env`) | OK |
| De la construcción a la restauración | 19 s |
| `/api/ready` | `disponible` |
| Páginas | `/` 200, `/no-existe` 404, detalle con `og:url` del ensayo |
| Clasificaciones de 2026 | 63/205/224 |
| Acceso al panel | Con la cuenta restaurada |
| Archivos | 42 restaurados, servidos con bytes idénticos |
| Entorno de desarrollo | Intacto tras la retirada |

## 12. Migración desde la web anterior en la misma MV

> `deploy.sh` (sección 0) hace esta migración entera, con la vuelta atrás automática si la web
> nueva no responde. Esta sección queda como referencia del procedimiento manual.

La web anterior (v2) se ejecuta en la MV con su propio `docker-compose.yml`: un servicio `app` y
un `caddy` que ocupa los puertos 80/443 y tiene los certificados de `trailpeñasagra.com`. Las dos
webs no pueden usar los puertos a la vez, así que el cambio consiste en parar una y arrancar la
otra. **Las comprobaciones y la carga de datos se hacen antes de parar la v2**, para que el corte
dure solo lo que tarda Caddy en pedir los certificados (segundos).

1. **Preparar la v3** en una carpeta nueva, sin tocar la v2 (por ejemplo `/srv/trail-v3`):

   ```bash
   git clone https://github.com/jrcosio/trailcorremosadriana_v3.git /srv/trail-v3 && cd /srv/trail-v3
   cp .env.example .env    # y edítalo (sección 2), con, como mínimo:
   #   POSTGRES_PASSWORD=<secreto: openssl rand -base64 32>
   #   PUBLIC_ORIGIN=https://xn--trailpeasagra-okb.com
   #   SITE_ADDRESS=xn--trailpeasagra-okb.com
   #   ALMACENAMIENTO=local    (o s3 con los datos de R2, sección 4)
   dc() { docker compose -f compose.yaml -f compose.produccion.yaml "$@"; }
   dc config > /dev/null && dc build
   ```

2. **Base de datos y datos** (la web aún no está publicada; solo arrancan `db` y `api`):

   ```bash
   dc up -d db
   dc run --rm api alembic upgrade head
   dc run --rm api python -m app.cli importar-inicial
   V2=/ruta/a/trailcorremosadriana_v2/datos/2026     # los CSV ya están en la MV, en la carpeta de la v2
   dc run --rm -T api python -m app.cli importar-clasificacion --carrera trail-27k --edicion 2026 \
     --titulo "Clasificación Trail Peñasagra 2026" --archivo Clasificacion_27km.csv --publicar < $V2/Clasificacion_27km.csv
   dc run --rm -T api python -m app.cli importar-clasificacion --carrera speed-14k --edicion 2026 \
     --titulo "Clasificación Speed Trail 2026" --archivo Clasificacion_14km.csv --publicar < $V2/Clasificacion_14km.csv
   dc run --rm -T api python -m app.cli importar-clasificacion --carrera familiar-7k --edicion 2026 \
     --titulo "Clasificación Familiar Peñasagra 2026" --archivo Clasificacion_marcha.csv --publicar < $V2/Clasificacion_marcha.csv
   dc run --rm api python -m app.cli crear-admin <tu-usuario>   # pide la contraseña dos veces
   ```

   Resultado esperado: 63, 205 y 224 participantes. Es una instalación limpia, sin los datos de
   prueba del entorno de desarrollo.

3. **Cambio** (el corte empieza aquí):

   ```bash
   cd /ruta/a/trailcorremosadriana_v2 && docker compose down    # SIN -v: conserva la v2 para volver
   cd /srv/trail-v3 && dc up -d
   dc logs -f web    # espera a «certificate obtained successfully» para el dominio y para www
   ```

4. **Comprobaciones**: las de la sección 6 y el acceso al panel (sección 13).

5. **Vuelta atrás** si algo falla (los datos de la v3 se conservan en sus volúmenes):

   ```bash
   cd /srv/trail-v3 && dc down
   cd /ruta/a/trailcorremosadriana_v2 && docker compose up -d
   ```

6. **Después**: programa las copias (sección 7). Cuando la v3 lleve unos días estable, puedes
   borrar la carpeta y los volúmenes de la v2.

## 13. Acceso al panel de administración

- **Dirección**: `https://<dominio>/admin`; con el dominio actual,
  `https://trailpeñasagra.com/admin`. No hay enlace desde la web pública.
- **Cuenta**: no hay usuario ni contraseña por defecto. La cuenta se crea en la MV con
  `dc run --rm api python -m app.cli crear-admin <usuario>` (sección 12, paso 2). La contraseña
  se pide oculta, dos veces, y debe tener entre 12 y 128 caracteres y ser distinta del usuario.
  Para crear más cuentas, repite el comando con otro usuario.
- **Sesión**: dura 8 horas (`SESSION_HOURS`) y se cierra con «Cerrar sesión». La cookie es
  `Secure`, así que el panel solo funciona por HTTPS.
- **Contraseña olvidada, cuenta bloqueada o sesión sospechosa**: sección 9. Tras 8 intentos
  fallidos en 15 minutos desde la misma IP hay que esperar a que pase la ventana.
- **Qué se gestiona**:
  - noticias, galería, pruebas y recorridos;
  - inscripciones y Dorsal Solidario;
  - fecha y contador;
  - clasificaciones (CSV);
  - patrocinadores y colaboradores;
  - reglamento;
  - contacto.

## 14. Ensayo en modo producción con HTTPS (feature 012)

Hecho en la máquina de desarrollo, sin servidor ni dominio real:

1. **Clon limpio**.
2. **Proyecto `trail-prod-ensayo`** con `compose.yaml` + `compose.produccion.yaml`.
3. **Dominio de prueba con «ñ»**: `SITE_ADDRESS=trailpeñasagra.localhost` y
   `PUBLIC_ORIGIN=https://trailpeñasagra.localhost`. Los `.localhost` reciben un certificado de la
   CA interna de Caddy en lugar de Let's Encrypt; el resto del mecanismo es el mismo.
4. **Puertos** 80/443 de la máquina.

Resultado en `docs/ESTADO_PROYECTO.md` (pruebas de la 012).

