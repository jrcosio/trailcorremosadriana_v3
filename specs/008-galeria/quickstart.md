# Quickstart / validación: Galería (008)

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head   # 0008
docker compose run --rm api python -m app.cli importar-inicial                    # 3 álbumes históricos
docker compose up -d
cd frontend && ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-galeria.mjs
```

El script comprueba:

- los 3 enlaces históricos y el filtro por año;
- un álbum nuevo con 2 fotos, como borrador y luego publicado;
- el visor (foco atrapado, flechas, Escape y vuelta del foco a la miniatura);
- quitar una foto;
- borrar el álbum y restaurar los datos.
