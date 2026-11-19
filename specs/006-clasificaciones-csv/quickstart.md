# Quickstart / validación: Clasificaciones CSV (006)

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head          # 0006
D=datos_iniciales/trailcorremosadriana_v2/datos/2026
docker compose run --rm -T api python -m app.cli importar-clasificacion --carrera trail-27k --edicion 2026 \
  --titulo "Clasificación Trail Peñasagra 2026" --archivo Clasificacion_27km.csv --publicar < $D/Clasificacion_27km.csv
docker compose run --rm -T api python -m app.cli importar-clasificacion --carrera speed-14k --edicion 2026 \
  --titulo "Clasificación Speed Trail 2026" --archivo Clasificacion_14km.csv --publicar < $D/Clasificacion_14km.csv
docker compose run --rm -T api python -m app.cli importar-clasificacion --carrera familiar-7k --edicion 2026 \
  --titulo "Clasificación Familiar Peñasagra 2026" --archivo Clasificacion_marcha.csv --publicar < $D/Clasificacion_marcha.csv
docker compose up -d
```

Esperado: 63, 205 y 224 participantes. `/clasificaciones/2026` muestra las tres.

```bash
cd frontend && ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-clasificaciones.mjs
```

Comprueba:

- búsqueda sin tildes, filtros y paginación;
- importación desde el panel: plantilla → error de dorsal repetido → corrección;
- sustitución;
- borrado;
- que no se puede borrar una prueba con clasificación;
- restauración de los datos al terminar.
