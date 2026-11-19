# Quickstart / validación: Base del proyecto (001)

Guía para comprobar de extremo a extremo que la feature funciona. Los contratos están en
[`contracts/`](contracts/) y el modelo en [`data-model.md`](data-model.md).

## Requisitos

- Docker con Compose v2+.
- Para desarrollo y pruebas del frontend fuera de contenedores: Node ≥ 22.13 y npm.
- No se necesita `datos_iniciales/` ni credenciales de producción.

## 1. Arranque con un único flujo

```bash
cp .env.example .env                       # opcional: Compose tiene valores de desarrollo
docker compose build
docker compose up -d db
docker compose run --rm api alembic upgrade head   # paso explícito de esquema
docker compose up -d
```

Esperado: `docker compose ps` muestra `db` y `api` *healthy* y `web` en marcha; solo se publica
el puerto `WEB_PORT` (8080 por defecto).

## 2. Salud y disponibilidad

```bash
curl -s localhost:8080/api/health          # {"estado":"viva"}
curl -s localhost:8080/api/ready           # {"estado":"disponible"}
```

Esquema pendiente (base nueva sin migrar): `/api/ready` → `503`,
`{"estado":"no_disponible","motivo":"migraciones_pendientes"}`.

Base detenida:

```bash
docker compose stop db
curl -s -w ' %{http_code}\n' localhost:8080/api/ready    # 503 base_de_datos_inaccesible (< 5 s)
curl -s localhost:8080/api/health                         # sigue {"estado":"viva"}
docker compose start db
```

## 3. Persistencia

```bash
docker compose restart
sleep 20 && curl -s localhost:8080/api/ready   # disponible sin repetir alembic
```

## 4. Contenido público transitorio

```bash
curl -s localhost:8080/api/content | python3 -m json.tool | head
curl -s -o /dev/null -w '%{http_code}\n' 'localhost:8080/api/content?admin=1'   # 401
curl -s localhost:8080/api/session                                              # {"authenticated":false}
```

Comprobar en la respuesta: `edition` `2027`, `date` vacío, ningún colaborador, imagen de
`trail-27k` = `/reused/img/trail_inscripciones.webp`, reglamento sin «PRUEBA».

## 5. Web pública y metadatos

- Abrir `http://localhost:8080/` y cada ruta de FR-001; recargar cada una.
- `curl -s localhost:8080/reglamento | grep -o '<title>[^<]*'` → `Reglamento | Trail Peñasagra`.
- `curl -s localhost:8080/robots.txt` → `Disallow: /admin`, `/api/`, `/pantallas`.
- `/admin`: formulario de acceso; al enviar, mensaje «El acceso de administración todavía no está
  disponible.» y sin acceso.
- `/pantallas/admin/noticias/nuevo`: guardar muestra «Esta es una vista de diseño…» y no hay
  petición de escritura.

## 6. Pruebas automáticas

```bash
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm api-test   # pytest + PostgreSQL real
cd frontend && npm ci && npm run typecheck && npm test && npm run build
```

## 7. Revisión visual

```bash
cd frontend
npx playwright install chromium
node scripts/capturas.mjs http://localhost:8080 capturas/local
node scripts/capturas.mjs https://trail-penasagra-nueva-web.jrblanco.chatgpt.site capturas/referencia
```

Esperado: `capturas/*/informe.json` sin rutas con desbordamiento horizontal; las capturas a
360/768/1024/1440 px coinciden con la referencia salvo los datos de prueba excluidos (D1–D4).

## 8. Independencia de `datos_iniciales`

```bash
git ls-files | grep -c datos_iniciales      # 0
D=$(mktemp -d) && git clone -q . "$D" && (cd "$D" && docker compose build)   # construye sin la carpeta
```
