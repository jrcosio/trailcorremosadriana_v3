---
description: "Tareas de implementación de la feature 003-archivos"
---

# Tasks: Archivos

**Input**: Design documents from `/specs/003-archivos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluidas (constitución V): pytest contra PostgreSQL real, adaptador S3 contra el servidor moto por HTTP y Playwright.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Añadir `boto3>=1.44,<1.45`, `python-multipart>=0.0.34,<0.1` y `defusedxml>=0.7.1,<0.8` a `backend/pyproject.toml` y regenerar `backend/uv.lock`
- [X] T002 [P] Añadir a `backend/app/core/config.py`, `.env.example`, `compose.yaml` (volumen `media` en `/data/media`) y `compose.dev.yaml` (servicio `s3-dev` con `motoserver/moto:5.2.5` y variables `S3_TEST_*` en `api-test`) las variables de data-model.md «Configuración nueva»
- [X] T003 [P] Crear `/data/media` con propietario `app` en `backend/Dockerfile` y limitar el cuerpo de `/api/upload` a 11 MB en `infra/caddy/Caddyfile`

## Phase 2: Foundational

- [X] T004 Crear `backend/app/models/archivos.py` con `Archivo` (data-model.md `Archivo.id`, `Archivo.clave`, `Archivo.tipo`, `Archivo.tamano`, `Archivo.sha256`, `Archivo.nombre_original`, `Archivo.subido_por`, `Archivo.creado_en`), registrarlo en `backend/app/models/__init__.py` y escribir `backend/alembic/versions/0003_archivos.py` con los CHECK de `Archivo.clave`, `Archivo.tipo` y `Archivo.tamano`, el UNIQUE de `Archivo.clave` y la FK de `Archivo.subido_por` (ON DELETE SET NULL)
- [X] T005 Implementar `backend/app/storage/__init__.py` (protocolo `Almacenamiento`, error `AlmacenamientoNoDisponible`, fábrica según `ALMACENAMIENTO`), `backend/app/storage/local.py` (escritura atómica) y `backend/app/storage/s3.py` (boto3 con `endpoint_url` y creación opcional del bucket), e inyectarlo en `app.state` desde `backend/app/main.py`
- [X] T006 [P] Implementar `backend/app/core/referencias.py` (`referencia_valida`) y `backend/tests/test_referencias.py`

## Phase 3: User Story 1 - Subir archivos (P1) 🎯 MVP

- [X] T007 [P] [US1] Escribir `backend/tests/test_tipos.py`: detección de JPEG, PNG, WebP, PDF y GPX por contenido; rechazo de SVG, HTML, texto, ejecutable (cabecera MZ) y GPX con DOCTYPE o entidades, con raíz distinta o mal formado; extensión correcta para un PNG nombrado `.jpg`
- [X] T008 [P] [US1] Escribir `backend/tests/test_subida.py`: subida correcta de los 5 tipos con `{url}` y fila en `archivos` (metadatos de data-model.md, `subido_por`, nombre saneado y sha256); 413 por encima del límite sin fila ni objeto; 400 sin archivo o con varios archivos o campos inesperados; 401, 403 y 403 por la protección de la 002; 503 sin fila si falla el almacenamiento
- [X] T009 [US1] Implementar `backend/app/services/archivos.py` (`detectar_tipo`, `validar_gpx` con defusedxml, `sanear_nombre`, `guardar_subida`: lectura por bloques con límite, almacenamiento antes que la fila, 503 sin fila)
- [X] T010 [US1] Sustituir el 501 de `backend/app/api/archivos.py` por la subida real (`requiere_escritura`, `UploadFile`, comprobación previa de Content-Length)

## Phase 4: User Story 2 - Entregar archivos (P1)

- [X] T011 [P] [US2] Escribir `backend/tests/test_media.py`: bytes idénticos; cabeceras (tipo, caché inmutable, ETag, nosniff, CSP sandbox, `Content-Disposition` inline o attachment con `.gpx`); 304 con `If-None-Match`; 404 por clave mal formada, inexistente o con objeto ausente, sin rutas internas en la respuesta; sin `Cache-Control: no-store`
- [X] T012 [US2] Implementar `backend/app/api/media.py` (`GET /media/{clave}`) y registrarlo en `backend/app/main.py`

## Phase 5: User Story 3 - Almacenamiento configurable (P2)

- [X] T013 [P] [US3] Escribir `backend/tests/test_almacenamiento_s3.py`: las mismas comprobaciones de subida y entrega contra el servidor moto (bucket creado), ida y vuelta byte a byte idéntica, objeto inexistente → None, errores de conexión → 503 sin fila; ninguna respuesta contiene el endpoint, el bucket ni las credenciales (SC-005); se omite solo si no hay `S3_TEST_ENDPOINT_URL`
- [X] T014 [US3] Ejecutar la suite en `api-test` con `s3-dev` y verificar en Compose la persistencia del volumen `media` tras `docker compose restart` (quickstart §3)

## Phase 6: User Story 4 - Recursos existentes (P3)

- [X] T015 [US4] Comprobar que los recursos estáticos (`/reused/`, `/images/`, `/fonts/`, `/templates/`) siguen respondiendo igual a través de Caddy y documentar en `docs/arquitectura.md` la regla de referencias de `app/core/referencias.py`

## Phase 7: Polish

- [X] T016 [P] Ampliar `infra/scripts/backup.sh` y `infra/scripts/restore.sh` con el volumen `media` y probar la copia
- [X] T017 [P] Crear `frontend/scripts/verificar-subida.mjs` (Playwright): con sesión, subir una imagen en `/admin/noticias/nuevo` y comprobar que la vista previa carga desde `/media/…`
- [X] T018 Ejecutar ruff, la suite completa (pytest con moto, vitest, typecheck, build), quickstart §1–§6 y la regresión (`verificar-rutas`, `verificar-acceso`); medir la subida de 10 MB (SC-004)
- [X] T019 Actualizar `docs/arquitectura.md`, `docs/desarrollo.md`, `docs/ROADMAP.md` y `docs/ESTADO_PROYECTO.md`

## Dependencies & Execution Order

Setup → Foundational (T004–T006) → US1 → US2 → US3 → US4 → Polish. US2 necesita archivos
subidos (US1) en sus pruebas.

---

## Phase 8: Convergence

- [X] T020 Documentar en `docs/desarrollo.md` el arranque de la API con `ALMACENAMIENTO=s3` contra `s3-dev` y verificar la subida y la entrega por Caddy en ese modo per data-model.md «Configuración nueva», US3/AC2 (partial)
- [X] T021 Registrar como trabajo trazable `HEAD /media/{clave}` (`backend/tests/test_media_head.py`), la ruta comodín `/media/{resto:path}` (404 genérico) y el `handle_errors` 413 en JSON de `infra/caddy/Caddyfile` per FR-003, FR-008 (unrequested)
