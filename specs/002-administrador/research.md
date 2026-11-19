# Research: Administrador (002)

Fecha: 2026-11-19. No quedan incógnitas abiertas.

## R1. Hash de contraseñas

- **Decision**: Argon2id con `argon2-cffi` 25.1 (`PasswordHasher` con los parámetros por defecto
  de la biblioteca, perfil RFC 9106 de baja memoria). Al entrar se llama a `check_needs_rehash` y
  se vuelve a calcular el hash si cambian los parámetros.
- **Rationale**: lo exigen la DOC 14 y la constitución III. La biblioteca usa Argon2id por
  defecto.
- **Alternatives considered**: bcrypt (resistencia a memoria inferior); PBKDF2 del prototipo
  (descartado por la DOC 14; no se migran sus hashes, DISCREPANCIAS M8).

## R2. Sesiones

- **Decision**: token opaco `secrets.token_urlsafe(32)` (256 bits) en la cookie
  `penasagra_admin` (`HttpOnly`, `SameSite=Strict`, `Path=/`, `Max-Age` = duración, `Secure`
  según `COOKIE_SECURE`). En PostgreSQL solo se guarda `sha256(token)` en hexadecimal.
  - Caducidad absoluta de 8 h (`SESSION_HOURS`).
  - Validación por petición: sesión no revocada, no caducada y de una cuenta activa.
  - `ultimo_uso_en` se actualiza como mucho cada 5 minutos para no escribir en cada petición.
- **Rationale**: sesiones revocables en el servidor y sin JWT, como pide la DOC 14. Guardar la
  huella evita que una fuga de la base permita suplantar sesiones.
- **Alternatives considered**: JWT (no se puede revocar sin una lista de bloqueo); sesión con
  renovación por actividad (no pedida; la DOC 14 toma 8 h como referencia).

## R3. Protección CSRF y Origin

- **Decision**: doble envío vinculado a la sesión.
  - Al entrar se emite la cookie `penasagra_csrf` (legible por JS, `SameSite=Strict`, `Path=/`,
    misma caducidad) y su huella se guarda en `sesiones.csrf_hash`.
  - Toda escritura autenticada debe enviar la cabecera `X-CSRF-Token` con el valor de esa cookie.
    El servidor compara la huella de la cabecera con la de la sesión mediante `hmac.compare_digest`.
  - `GET /api/session` vuelve a emitir la cookie (con nueva huella) si una sesión válida no la
    trae.
  - Además, toda escritura (`POST`, `PUT`, `PATCH`, `DELETE`, incluidos login y logout) exige una
    cabecera `Origin` que coincida con `PUBLIC_ORIGIN` o con un origen de `ORIGENES_PERMITIDOS`.
    Sin `Origin` se rechaza.
- **Rationale**: defensa en profundidad sobre `SameSite=Strict`, como exige la DOC 14 (CSRF más
  comprobación de origen). El frontend lee la cookie y añade la cabecera con un único helper.
- **Alternatives considered**: token sincronizado devuelto en JSON y guardado en memoria (el
  panel tendría que repartirlo a todos sus componentes); solo `SameSite` (no cumple la DOC 14).

## R4. Límite de intentos

- **Decision**: tabla `limites_login` con la clave `sha256(ip)`.
  - En cada acceso, dentro de una transacción, se bloquea la fila con `SELECT … FOR UPDATE`.
  - Si la ventana de 15 minutos ha expirado, se reinicia.
  - Si `intentos ≥ 8`, se responde 429 con `Retry-After`.
  - Un fallo incrementa el contador; un acierto borra la fila.
  - Valores configurables: `LOGIN_MAX_INTENTOS` y `LOGIN_VENTANA_MINUTOS`.
- **Rationale**: es persistente (sobrevive a reinicios) y seguro frente a peticiones concurrentes.
- **Alternatives considered**: memoria del proceso (se pierde al reiniciar, prohibido);
  limitar por usuario (permite bloquear a la organización desde fuera; la DOC 14 limita por
  origen).

## R5. IP real del cliente

- **Decision**: Caddy `reverse_proxy` reemplaza `X-Forwarded-For` con la IP del cliente, porque
  ignora la cabecera entrante de clientes no confiables. Uvicorn se arranca con `--proxy-headers`
  y `FORWARDED_ALLOW_IPS=*`, valor seguro porque en `compose.yaml` la API solo es accesible desde
  Caddy en la red interna. En `compose.dev.yaml` la API se publica solo en `127.0.0.1`.
- **Rationale**: el límite debe aplicarse al visitante, no al proxy.

## R6. Igualar tiempos y mensajes

- **Decision**: si el usuario no existe o está inactivo, se verifica la contraseña contra un hash
  ficticio calculado al arrancar. Todos los fallos responden
  `401 {"error":"Usuario o contraseña incorrectos."}`. Las contraseñas de más de 128 caracteres
  o los usuarios de más de 64 se rechazan como un fallo normal (cuentan para el límite) sin
  calcular el hash.
- **Rationale**: evita enumerar usuarios por mensaje o por tiempo (FR-009, SC-008) y que se abuse
  del coste del cálculo.

## R7. Comando de operador

- **Decision**: `python -m app.cli` con `argparse` y estos subcomandos: `crear-admin`,
  `restablecer-password`, `desactivar`, `activar`, `revocar-sesiones` y `listar-admins`.
  - La contraseña se pide con `getpass` dos veces o se lee de stdin con `--password-stdin` (una
    línea), nunca como argumento.
  - Usuario normalizado: sin espacios y en minúsculas, patrón `^[a-z0-9][a-z0-9._-]{2,63}$`.
  - Política de contraseña: 12–128 caracteres y distinta del usuario.
  - `crear-admin` falla si el usuario ya existe y no modifica nada.
- **Uso**: `docker compose run --rm api python -m app.cli crear-admin <usuario>`.
- **Rationale**: es la única vía de alta (DOC 14: «Comando de creación o recuperación… sin
  registro público»).

## R8. Secciones aún sin persistencia

- **Decision**: `PUT /api/content` y `POST /api/upload` aplican la cadena de protección completa
  (Origin → sesión → CSRF) y después responden
  `501 {"error":"Esta sección del panel todavía no guarda cambios."}`. Las features 003–010 las
  sustituyen por endpoints por recurso.
- **Rationale**: el panel muestra el error recibido y nunca simula éxito (FR-018). Que la
  protección se aplique antes del 501 permite comprobar SC-002 y SC-003 sobre todas las rutas de
  escritura existentes.

## R9. Cambios en el frontend

- **Decision**: nuevo `src/lib/api.ts` con `leerCookie(nombre)` y `apiFetch(url, init)`, que
  añade `X-CSRF-Token` en los métodos de escritura. En `Admin.tsx` solo cambian `save()`, el
  botón de cerrar sesión (si falla, muestra el error y no oculta el panel) y la subida de
  archivos. Sin cambios visuales.
- **Rationale**: es el mínimo necesario para cumplir R3 conservando las pantallas.

## R10. Pruebas

- **Decision**: pytest contra PostgreSQL real. Cubre sesión, caducidad (manipulando `expira_en`),
  revocación por logout, desactivación y comando, límite (ventana manipulada en BD), CSRF,
  Origin, persistencia (segunda instancia de la app sobre la misma base), huellas en BD (el token
  en claro no aparece) y el CLI con `--password-stdin`. Se añade Playwright de extremo a extremo
  (`frontend/scripts/verificar-acceso.mjs`) con acceso, resumen, recarga, cierre, rechazo
  posterior y bloqueo.
