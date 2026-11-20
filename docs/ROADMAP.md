# Roadmap

Cada feature sigue el ciclo SDD de Spec Kit y cierra BD + API + admin + pública cuando
corresponde. Estado: ⏳ pendiente · 🔄 activa · ✅ terminada.

| # | Feature | Depende de | Estado | Rama / spec |
|---|---|---|---|---|
| 0 | Preparación: fuentes protegidas, referencia, constitución, roadmap | — | ✅ | `main` |
| 1 | Base del proyecto: frontend reutilizado, FastAPI, PostgreSQL, Alembic, Compose, salud | 0 | ✅ | `001-base-proyecto` |
| 2 | Administrador: usuario inicial seguro, login, sesión, logout, permisos, intentos, CSRF | 1 | ✅ | `002-administrador` |
| 3 | Archivos: almacenamiento local/S3, subida, validación, entrega de imágenes y GPX | 2 | ✅ | `003-archivos` |
| 4 | Evento y carreras: ediciones, fecha Europe/Madrid, contador, recorridos | 2, 3 | ✅ | `004-evento-carreras` |
| 5 | Inscripciones y Dorsal Solidario: apertura/cierre, enlaces por carrera y pago solidario | 4 | ✅ | `005-inscripciones-dorsal` |
| 6 | Clasificaciones CSV: importación, mapeo, vista previa, transacción, consulta pública | 4 | ✅ | `006-clasificaciones-csv` |
| 7 | Noticias: borradores, publicación, imágenes, detalle | 3 | ✅ | `007-noticias` |
| 8 | Galería: álbumes, fotografías, orden, enlaces históricos | 3 | ✅ | `008-galeria` |
| 9 | Patrocinadores y colaboradores | 3 | ✅ | `009-patrocinadores-colaboradores` |
| 10 | Reglamento y contacto | 4 | ✅ | `010-reglamento-contacto` |
| 11 | Cierre: accesibilidad, móvil, rendimiento, 404/metadatos, copias, despliegue independiente | 1–10 | 🔄 activa (implementación) | `011-cierre` |

## Progreso de la feature activa (011-cierre)

Especificación, plan y tareas: `specs/011-cierre/` (21 tareas). Decisiones del propietario P4
(contraste AA) y P5 (`/pantallas` retirada en producción) en `docs/referencia/DISCREPANCIAS.md`.

| Historia | Contenido | Estado |
|---|---|---|
| US1 (P1) | 404 reales y metadatos de detalle en el HTML inicial | ✅ T001–T006: `/api/meta`, `plantilla.html`/`404.html`, Caddy; `verificar-cierre` 5/5; rutas 42/42 |
| US2 (P1) | Accesibilidad AA (P4) y cabecera a 320/340 px | ✅ T007–T009: axe 0 incumplimientos (17 rutas, 360/1440), 0 desbordamientos a 6 anchos; capturas: solo cambian los elementos de P4 |
| US3 (P1) | Copia y restauración verificadas, ensayo de despliegue independiente, `docs/operacion.md` | 🔄 siguiente: T010–T013 |
| US4 (P2) | CSP y `/pantallas` retirada en producción | ⏳ T014–T015 |
| US5 (P2) | Fuentes en WOFF2 real (−40 %) | ⏳ T016 |
| US6 (P3) | Limpieza de archivos huérfanos, código sin uso, `httpx2` | ⏳ T017–T019 |
| Cierre | Regresión completa, documentación, convergencia, merge | ⏳ T020–T021 |

## Fuera de alcance (salvo nueva instrucción)

Pasarela de pago o inscripción propia, envío de correo desde servidor, cronometraje en directo,
varias cuentas de administrador con roles, publicación en producción y cambio de dominio.
