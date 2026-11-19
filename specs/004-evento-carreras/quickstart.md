# Quickstart / validación: Evento y carreras (004)

Prerrequisitos: features 001–003 en marcha, con la cuenta `admin`. Contrato:
[`contracts/`](contracts/). Modelo: [`data-model.md`](data-model.md).

## 1. Migración e importación

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head   # 0004_evento_carreras
docker compose run --rm api python -m app.cli importar-inicial    # crea las ediciones 2026/2027 y las 3 pruebas
docker compose run --rm api python -m app.cli importar-inicial    # 2.ª vez: «sin cambios»
docker compose up -d
```

## 2. Web pública sin cambios

`node frontend/scripts/verificar-rutas.mjs` → 42/42. Las capturas y los textos coinciden con la
feature 001 (`capturas.mjs`).

## 3. Panel

| Prueba | Pantalla | Comprobación |
|---|---|---|
| Fecha | `/admin/evento` | Guardar 10/07/2027 09:00 → la portada muestra «10 de julio de 2027» con contador. Reabrir el panel → 09:00. Vaciar la fecha → «Fecha por confirmar». |
| Horario de invierno | `/admin/evento` | Guardar 2027-01-15 09:00 → reabrir muestra 09:00 (SC-002). Restaurar sin fecha. |
| Editar | `/admin/recorridos/trail-27k` | Cambiar km a 28 → `/carreras/trail-27k` muestra 28K. Restaurar a 27. |
| Crear | `/admin/recorridos/nuevo` | Guardar → borrador, no aparece en `/carreras`. Publicar → aparece. Borrar → desaparece. |
| Conflicto | Dos navegadores | Guardar en ambos sobre la misma versión → el segundo recibe 409. |

## 4. Persistencia

`docker compose restart` → la fecha y los cambios de prueba siguen ahí.

## 5. Pruebas

```bash
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test
cd frontend && npm test && npm run typecheck && npm run build
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-evento-carreras.mjs
```
