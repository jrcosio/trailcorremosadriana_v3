# Quickstart / validación: Noticias (007)

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head   # 0007
docker compose run --rm api python -m app.cli importar-inicial                    # 2 noticias si no hay ninguna
docker compose up -d
cd frontend && ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-noticias.mjs
```

El script comprueba:

- las dos noticias en `/noticias` y en la portada, con sus detalles;
- una noticia nueva que nace como borrador (no visible y con detalle no encontrado);
- su publicación con imagen subida;
- el HTML mostrado como texto;
- el conflicto 409;
- la retirada y el borrado, con restauración al terminar.
