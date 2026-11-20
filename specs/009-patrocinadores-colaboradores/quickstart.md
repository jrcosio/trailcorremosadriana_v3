# Quickstart / validación: Patrocinadores y colaboradores (009)

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head && \
  docker compose run --rm api python -m app.cli importar-inicial && docker compose up -d
cd frontend && ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-entidades.mjs
```

El script comprueba:

- los 8 patrocinadores, grandes, sin enlaces y en orden;
- un colaborador con web en pestaña nueva y su cambio de orden;
- que los patrocinadores no cambian (independencia);
- la retirada y el borrado, con restauración al terminar.
