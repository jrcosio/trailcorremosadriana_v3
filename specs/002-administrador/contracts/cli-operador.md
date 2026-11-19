# Contrato del comando de operador (feature 002)

`python -m app.cli <subcomando> [opciones]` — en Docker:
`docker compose run --rm api python -m app.cli <subcomando> …` (añadir `-T` con `--password-stdin`).

| Subcomando | Argumentos | Efecto | Salida y código |
|---|---|---|---|
| `crear-admin` | `USUARIO [--password-stdin]` | Crea una cuenta activa. Falla si ya existe (no modifica nada) | `Administrador «x» creado.` · 0. Ya existe: mensaje con `restablecer-password` · 1 |
| `restablecer-password` | `USUARIO [--password-stdin]` | Nueva contraseña y revocación de todas sus sesiones | 0 / 1 si no existe |
| `desactivar` | `USUARIO` | `activo=false` y revocación de sesiones | 0 / 1 |
| `activar` | `USUARIO` | `activo=true` | 0 / 1 |
| `revocar-sesiones` | `USUARIO` | Revoca todas sus sesiones abiertas | `N sesiones revocadas.` · 0 / 1 |
| `listar-admins` | — | Tabla: usuario, activo, último acceso (nunca hashes) | 0 |

Contraseña:

- Interactiva: `getpass` dos veces, con confirmación obligatoria.
- Con `--password-stdin`: se lee una sola línea de la entrada estándar, sin confirmación.
- Nunca se acepta como argumento ni se imprime.
- Política: 12–128 caracteres y distinta del usuario. Si no se cumple: mensaje del motivo y
  código 2.

Usuario: se normaliza (`strip`, minúsculas) y debe cumplir `^[a-z0-9][a-z0-9._-]{2,63}$`. Si no lo
cumple, código 2.
