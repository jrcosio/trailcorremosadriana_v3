# Implementation Plan: Cierre para el lanzamiento

**Branch**: `011-cierre` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

## Summary

Seis bloques sin funcionalidades nuevas de contenido:

1. **404 reales y metadatos de detalle**: plantillas de Caddy que consultan `GET /api/meta`.
2. **Accesibilidad AA y móvil**: decisión P4 y cabecera a 320/340 px.
3. **Copias, restauración y despliegue**: copia y restauración verificadas, ensayo de despliegue
   independiente y `docs/operacion.md`.
4. **Seguridad**: CSP y retirada de `/pantallas` en producción (decisión P5).
5. **Rendimiento**: fuentes en WOFF2 real.
6. **Limpieza**: comando de archivos huérfanos, código sin uso y `httpx2`.

Detalle en [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript 5.9 + React 19 (frontend), Caddy 2.11
**Primary Dependencies**: FastAPI, SQLAlchemy 2, Alembic; Vite; `@axe-core/playwright` 4.10.2
(dev); fontTools (herramienta puntual de conversión, no dependencia); `httpx2` 2.16.0 (dev)
**Storage**: PostgreSQL 17; almacenamiento local o S3/R2
**Testing**: pytest contra PostgreSQL real; vitest; Playwright (+ axe); scripts de shell de copia
**Target Platform**: Docker Compose (Caddy + API + PostgreSQL)
**Project Type**: aplicación web
**Performance Goals**: fuentes −40 % de peso o más; detalle con metadatos en una sola consulta
adicional a la API
**Constraints**:
- Sin cambios visuales fuera de P4.
- Sin desplegar.
- La CSP propia de `/media` se respeta.
**Scale/Scope**: sin migraciones nuevas; 1 endpoint público nuevo (`/api/meta`); 1 comando de
operador

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I | Cambios visuales solo los de P4 (instrucción del propietario); comparación de capturas | ✅ |
| II | Sin cambios de persistencia; la restauración se verifica tabla a tabla | ✅ |
| III | CSP; `/pantallas` retirada en producción; el borrado de archivos exige confirmación escrita; sin secretos en el ensayo | ✅ |
| IV | URLs conservadas; los 404 solo afectan a lo inexistente; licencias OFL de las fuentes conservadas | ✅ |
| V | pytest, axe, Playwright, scripts de copia y ensayo real en clon limpio | ✅ |
| VI | Sin despliegue ni cambio de dominio; sin datos inventados en los metadatos | ✅ |

Re-evaluación tras el diseño: sin cambios. ✅

## Project Structure

```text
infra/caddy/Caddyfile                       # plantillas, 404, CSP, PANTALLAS, SITE_ADDRESS
infra/scripts/{backup,restore,verificar-copia}.sh
compose.yaml · compose.dev.yaml · compose.produccion.yaml (nuevo) · .env.example
frontend/plugins/metadatos-rutas.ts         # plantilla.html y 404.html
frontend/src/styles/ajustes.css             # P4 y cabecera 320/340
frontend/public/fonts/*.woff2 · *.css       # WOFF2 real
frontend/scripts/{verificar-accesibilidad,verificar-cierre}.mjs
backend/app/api/meta.py · app/services/meta.py · app/main.py (404/405 en español)
backend/app/cli.py (limpiar-archivos) · app/services/archivos.py (huérfanos)
backend/tests/{test_meta,test_limpieza}.py · pyproject.toml (httpx2)
docs/operacion.md (nuevo) · docs/{arquitectura,desarrollo,ROADMAP,ESTADO_PROYECTO}.md
```

## Complexity Tracking

| Elemento | Por qué | Alternativa descartada |
|---|---|---|
| Plantillas de Caddy con `httpInclude` | Estado 404 real y metadatos en el HTML inicial sin que la API tenga que conocer los nombres con hash del build | API que sirve el HTML completo: exige copiar el build a la imagen de la API o leerlo de Caddy, y acopla las dos imágenes |
