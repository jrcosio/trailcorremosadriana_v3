# Operación y despliegue independiente

Guía para instalar, mantener y recuperar la web **Trail Peñasagra — Corremos por Adriana** en un
servidor propio. Probada en un ensayo local desde un clon limpio (feature 011, «Ensayo de
despliegue» al final). Nada de esta guía se ha ejecutado contra el dominio ni la producción real.

> Todos los comandos se ejecutan en la carpeta del repositorio. En producción, añade siempre
> `-f compose.yaml -f compose.produccion.yaml` (en esta guía, `$DC`).

```bash
DC="docker compose -f compose.yaml -f compose.produccion.yaml"
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
   | `PUBLIC_ORIGIN` | `https://<dominio>`, exactamente como lo escribe el visitante |
   | `SITE_ADDRESS` | `<dominio>`, sin `https://` (p. ej. `xn--trailpeasagra-okb.com`) |
   | `ALMACENAMIENTO` | `s3` (R2) o `local` |
   | `S3_*` | Solo con R2 (sección 4) |
   | `SESSION_HOURS`, `LOGIN_*`, `UPLOAD_MAX_BYTES` | Por defecto, salvo necesidad |

   `compose.produccion.yaml` fija `ENTORNO=produccion`, `COOKIE_SECURE=true` y `PANTALLAS=no`,
   y publica los puertos 80 y 443. Si falta una variable obligatoria, Compose se detiene con un
   error que la nombra. `.env` **nunca** se versiona ni se copia fuera del servidor.
3. **Comprobar la configuración** sin arrancar nada: `$DC config > /dev/null`.

## 3. Dominio y HTTPS

- Caddy obtiene y renueva los certificados automáticamente para `SITE_ADDRESS` cuando el DNS ya
  apunta al servidor y los puertos 80 y 443 están abiertos.
- Los certificados se guardan en el volumen `caddy_data`: **no borres ese volumen**, porque
  forzaría a pedirlos de nuevo y hay límites de emisión.
- Para servir también `www.<dominio>`, añade la variante a `SITE_ADDRESS` separada por coma
  (`dominio, www.dominio`).
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
$DC build
$DC up -d db
$DC run --rm api alembic upgrade head                  # esquema (paso explícito)
$DC run --rm api python -m app.cli importar-inicial    # datos aprobados (solo partes vacías)
$DC run --rm api python -m app.cli crear-admin <usuario>   # pide la contraseña (12–128)
$DC up -d
```

- Para cargar clasificaciones desde un CSV:
  `$DC run --rm -T api python -m app.cli importar-clasificacion --carrera trail-27k --edicion 2026 --titulo "…" --archivo original.csv --publicar < original.csv`.
- **Alternativa**: si se parte de una copia existente (por ejemplo, la del entorno de revisión con
  las clasificaciones de 2026 ya importadas), sigue la sección 7 en lugar de `importar-inicial`.

## 6. Comprobaciones después de desplegar

| Comprobación | Resultado esperado |
|---|---|
| `curl -s https://<dominio>/api/ready` | `{"estado":"disponible", …}` |
| `curl -sI https://<dominio>/` | 200 con `Content-Security-Policy`, `X-Content-Type-Options` y `Referrer-Policy` |
| `curl -s -o /dev/null -w '%{http_code}' https://<dominio>/no-existe` | `404` |
| `curl -s -o /dev/null -w '%{http_code}' https://<dominio>/pantallas` | `404` (P5) |
| `curl -s https://<dominio>/noticias/<id>` | Título y `og:*` propios en el HTML |
| `/admin` | Acceso con la cuenta creada; cookie `penasagra_admin` con `Secure` y `HttpOnly` |
| Subir una imagen desde el panel | Se ve en la web (`/media/…`) |
| `$DC run --rm api alembic current` | Revisión en la cabeza (`head`) |

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
$DC up -d db api                       # la API debe estar en marcha para restaurar archivos
infra/scripts/restore.sh /ruta/trail-….dump [/ruta/media-….tgz]
$DC run --rm api alembic upgrade head  # por si la copia es de una versión anterior
$DC up -d
```

- La restauración funciona igual sobre una base nueva (servidor nuevo) que sobre una existente.
- Restaurar los archivos **añade y sobrescribe**; no borra los archivos que no estén en la copia.
- **Verificación periódica** (en un entorno de pruebas, nunca en producción):
  `infra/scripts/verificar-copia.sh`. Hace una copia, cambia datos, restaura y compara las
  huellas de cada tabla y de cada archivo.

## 8. Actualizar a una versión nueva

1. Haz una copia (sección 7).
2. Descarga el código: `git pull` o la etiqueta de la versión.
3. Construye y migra:

   ```bash
   $DC build
   $DC run --rm api alembic upgrade head
   $DC up -d
   ```

4. Repite las comprobaciones de la sección 6.

**Volver atrás**: código anterior (`git checkout <versión>`), `$DC build` y restauración de la
copia del paso 1.

## 9. Recuperar el acceso al panel

| Situación | Comando |
|---|---|
| Contraseña olvidada | `$DC run --rm api python -m app.cli restablecer-password <usuario>` (revoca sus sesiones) |
| Sospecha de sesión robada | `$DC run --rm api python -m app.cli revocar-sesiones <usuario>` |
| Cuenta desactivada | `$DC run --rm api python -m app.cli activar <usuario>` |
| Ver las cuentas | `$DC run --rm api python -m app.cli listar-admins` |
| Nueva cuenta | `$DC run --rm api python -m app.cli crear-admin <usuario>` |

Tras 8 intentos fallidos en 15 minutos desde la misma IP, el acceso se bloquea hasta que pasa la
ventana (`LOGIN_MAX_INTENTOS` y `LOGIN_VENTANA_MINUTOS`). No hay recuperación por correo: la web no
envía correo (constitución VI).

## 10. Mantenimiento

- **Archivos subidos sin uso**: `$DC run --rm api python -m app.cli limpiar-archivos` lista los
  archivos sin referencias con más de 24 horas. Con `--borrar` los elimina después de escribir
  `BORRAR`. Haz antes una copia.
- **Registros**: `$DC logs --since 24h api web`.
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

Resultado y detalle en `docs/ESTADO_PROYECTO.md` (pruebas de la 011).
