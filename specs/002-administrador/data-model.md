# Data Model: Administrador (002)

Migración Alembic `0002_administracion` (sobre `0001_base`). Todas las fechas son `timestamptz`
en UTC.

## Administrador (`administradores`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | integer identity | PK |
| `usuario` | varchar(64) | NOT NULL, UNIQUE; normalizado (minúsculas, sin espacios); patrón `^[a-z0-9][a-z0-9._-]{2,63}$` (CHECK `usuario = lower(usuario)`) |
| `hash_password` | varchar(255) | NOT NULL; formato Argon2id (`$argon2id$…`) |
| `activo` | boolean | NOT NULL, por defecto `true` |
| `creado_en` | timestamptz | NOT NULL, por defecto `now()` |
| `actualizado_en` | timestamptz | NOT NULL, por defecto `now()` |
| `ultimo_acceso_en` | timestamptz | NULL |
| `password_cambiada_en` | timestamptz | NOT NULL, por defecto `now()` |

Política de contraseña (no se guarda, se valida): 12–128 caracteres y distinta del usuario.

Transiciones de `activo`: `true → false` (`desactivar`, revoca todas las sesiones) y
`false → true` (`activar`).

## Sesión (`sesiones`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | bigint identity | PK |
| `administrador_id` | integer | NOT NULL, FK → `administradores.id` ON DELETE CASCADE; índice |
| `token_hash` | char(64) | NOT NULL, UNIQUE; SHA-256 en hexadecimal del token opaco |
| `csrf_hash` | char(64) | NOT NULL; SHA-256 en hexadecimal del comprobante CSRF |
| `creada_en` | timestamptz | NOT NULL, por defecto `now()` |
| `expira_en` | timestamptz | NOT NULL; `creada_en + SESSION_HOURS`; índice |
| `revocada_en` | timestamptz | NULL; no nulo = revocada |
| `ultimo_uso_en` | timestamptz | NOT NULL, por defecto `now()` |

Una sesión es válida si `revocada_en IS NULL`, `expira_en > now()` y la cuenta está activa.

Estados: `activa → revocada` (logout, `revocar-sesiones`, `desactivar` o `restablecer-password`)
y `activa → caducada` (por tiempo). No hay vuelta atrás.

Limpieza: en cada acceso correcto se borran las sesiones caducadas o revocadas hace más de 7 días.

## Límite de acceso (`limites_login`)

| Campo | Tipo | Restricciones |
|---|---|---|
| `clave` | char(64) | PK; SHA-256 en hexadecimal de la IP del cliente |
| `intentos` | integer | NOT NULL, CHECK `intentos >= 0` |
| `inicio` | timestamptz | NOT NULL; primer fallo de la ventana actual |

Regla: bloqueado si `intentos >= LOGIN_MAX_INTENTOS` y `now() < inicio + LOGIN_VENTANA_MINUTOS`.
Si la ventana expiró, la fila se reinicia. Un acceso correcto borra la fila.

## Configuración nueva

| Variable | Valor por defecto (código) | Desarrollo (`compose.yaml`) |
|---|---|---|
| `SESSION_HOURS` | `8` | `8` |
| `COOKIE_SECURE` | `true` | `false` (HTTP local) |
| `ORIGENES_PERMITIDOS` | vacío | vacío (en `compose.dev.yaml`: `http://localhost:5173`) |
| `LOGIN_MAX_INTENTOS` | `8` | `8` |
| `LOGIN_VENTANA_MINUTOS` | `15` | `15` |
| `FORWARDED_ALLOW_IPS` (uvicorn) | `127.0.0.1` | `*` (API solo accesible desde Caddy) |
