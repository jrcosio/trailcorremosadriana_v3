# Quickstart / validación: Cierre (011)

```bash
docker compose build && docker compose up -d
docker compose -f compose.yaml -f compose.dev.yaml --profile test run --rm --build api-test pytest -q
cd frontend && npm run typecheck && npx vitest run && npm run build
```

1. **404 y metadatos**: `node scripts/verificar-cierre.mjs`.
   - `curl -o /dev/null -w '%{http_code}'` → `/no-existe` 404, `/noticias/inventada` 404,
     `/noticias/gracias-trail-2026` 200 con `og:title` propio en el HTML, `/clasificaciones/2026`
     200 y `/clasificaciones/2019` 404.
   - Con la API detenida, `/noticias/gracias-trail-2026` → 200 con los metadatos genéricos.
2. **Accesibilidad y móvil**: `node scripts/verificar-accesibilidad.mjs` → 0 incumplimientos y
   0 desbordamientos a 6 anchos. Capturas antes y después: solo cambian los elementos de P4.
3. **CSP y `/pantallas`**:
   - Recorrido sin violaciones de CSP.
   - `/pantallas` → 404 con `compose.yaml`; 200 con `PANTALLAS=si`.
4. **Fuentes**: tamaño total de `public/fonts/*.woff2` antes y después (≥ 40 % menos);
   `file` → «Web Open Font Format (Version 2)».
5. **Copias**: `infra/scripts/verificar-copia.sh` → todas las huellas coinciden.
6. **Ensayo de despliegue**: clon limpio y `docs/operacion.md` en `trail-ensayo` (puerto 8090) →
   web, panel y archivos restaurados; después `docker compose -p trail-ensayo down -v`.
7. **Limpieza**: `docker compose run --rm api python -m app.cli limpiar-archivos`. Lista los
   huérfanos; `--borrar` solo actúa con «BORRAR».
8. **Regresión**: todos los `verificar-*.mjs` (con `PANTALLAS=si` para `verificar-admin`).
