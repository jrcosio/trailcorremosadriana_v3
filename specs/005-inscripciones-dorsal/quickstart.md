# Quickstart / validación: Inscripciones y Dorsal Solidario (005)

```bash
docker compose build api web && docker compose run --rm api alembic upgrade head        # 0005
docker compose run --rm api python -m app.cli importar-inicial   # completa los campos de inscripción
docker compose up -d
cd frontend && ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-inscripciones.mjs   # matriz 4×3 + panel; restaura
```

Esperado:

- Matriz 12/12.
- Apertura sin destinos rechazada.
- Enlaces peligrosos rechazados.
- Al cerrar, los enlaces se conservan.
- Tras `docker compose restart`, el estado se mantiene.
- Al terminar, el entorno queda cerrado y sin enlaces.
