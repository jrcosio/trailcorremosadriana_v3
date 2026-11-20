# Quickstart / validación: Reglamento y contacto (010)

```bash
docker compose build api web && docker compose up -d && \
  docker compose run --rm api alembic upgrade head && \
  docker compose run --rm api python -m app.cli importar-inicial
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test pytest -q
cd frontend && npm run typecheck && npx vitest run && npm run build
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-reglamento-contacto.mjs
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-acceso.mjs
```

Resultados esperados:

- **Datos importados**: `/reglamento` muestra el resumen de 2026 sin «PRUEBA» y `/contacto`, el
  pie y `/inscripciones` muestran los mismos datos que antes. `/contacto` sigue mostrando
  `@asociacion_penasagra`.
- **Reglamento**:
  - Editar en `/admin/reglamento` → `/reglamento` muestra el apartado nuevo.
  - Persiste tras `docker compose restart api`.
  - Al terminar se restaura el original: el reglamento propio de 2027 se vacía directamente en la
    base para volver a mostrar la referencia de 2026.
- **Contacto**:
  - Cambiar correo, teléfono e Instagram → se actualizan todas las ubicaciones y el `mailto` del
    formulario.
  - Valores no válidos → mensaje con el nombre del campo, sin «Cambios guardados».
  - Al terminar se restauran los originales.
- **Documento completo**: `PUT /api/content` → 405.
