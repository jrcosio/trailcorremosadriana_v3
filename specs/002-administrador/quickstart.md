# Quickstart / validación: Administrador (002)

Prerrequisito: el entorno de la feature 001 funcionando (`docs/desarrollo.md`). Contratos:
[`contracts/api-administracion.openapi.yaml`](contracts/api-administracion.openapi.yaml) y
[`contracts/cli-operador.md`](contracts/cli-operador.md). Modelo:
[`data-model.md`](data-model.md).

## 1. Migración y administrador local

```bash
docker compose build api web
docker compose run --rm api alembic upgrade head            # aplica 0002_administracion
docker compose up -d
docker compose run --rm api python -m app.cli crear-admin admin    # pide la contraseña dos veces
docker compose run --rm api python -m app.cli listar-admins
```

Esperado: `listar-admins` muestra `admin` activo. En la base, `hash_password` empieza por
`$argon2id$`. Repetir `crear-admin admin` falla y no modifica la cuenta.

## 2. Acceso por la web

1. Abrir <http://localhost:8080/admin>, entrar con `admin` → se muestra el resumen
   («Peñasagra 2027», conteos de noticias, álbumes, clasificaciones y entidades).
2. Recargar → sigue dentro. `docker compose restart api` y recargar → sigue dentro.
3. Usuario o contraseña incorrectos → «Usuario o contraseña incorrectos.» (mismo mensaje en ambos
   casos).
4. Cerrar sesión → vuelve el formulario de acceso.

## 3. API (con curl)

```bash
O='-H Origin:http://localhost:8080'
curl -s -c c.txt $O -H 'content-type: application/json' \
  -d '{"username":"admin","password":"<contraseña>"}' localhost:8080/api/login     # {"ok":true,...}
curl -s -b c.txt 'localhost:8080/api/content?admin=1' | head -c 80                 # 200
curl -s -b c.txt -X PUT $O localhost:8080/api/content -w ' %{http_code}\n'         # 403 (sin CSRF)
T=$(awk '$6=="penasagra_csrf"{print $7}' c.txt)
curl -s -b c.txt -X PUT $O -H "X-CSRF-Token: $T" localhost:8080/api/content -w ' %{http_code}\n'   # 501
curl -s -b c.txt -X POST -H 'Origin: https://otro.example' localhost:8080/api/logout -w ' %{http_code}\n'  # 403
curl -s -b c.txt -X POST $O -H "X-CSRF-Token: $T" localhost:8080/api/logout       # {"ok":true}
curl -s -b c.txt -o /dev/null -w '%{http_code}\n' 'localhost:8080/api/content?admin=1'   # 401
```

## 4. Límite de intentos

Enviar 8 accesos fallidos seguidos. El 9.º, incluso con la contraseña correcta, responde 429 con
`Retry-After`, y la pantalla muestra «Demasiados intentos…». Tras `docker compose restart api`
sigue bloqueado. Para desbloquear en local antes de 15 minutos:
`docker compose exec db psql -U trail -c 'DELETE FROM limites_login'`.

## 5. Revocación por operador

Con una sesión abierta en el navegador:
`docker compose run --rm api python -m app.cli revocar-sesiones admin` → la siguiente acción del
panel vuelve al acceso. `desactivar admin` → ya no se puede entrar. `activar admin` → se puede
entrar de nuevo.

## 6. Pruebas automáticas

```bash
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test
cd frontend && npm run typecheck && npm test && npm run build
node scripts/verificar-acceso.mjs      # requiere ADMIN_USUARIO y ADMIN_PASSWORD de una cuenta local
node scripts/verificar-admin.mjs       # vistas de diseño sin escritura; acceso erróneo con mensaje genérico
node scripts/verificar-rutas.mjs       # las 42 rutas de la feature 001 siguen funcionando
```
