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
| 10 | Reglamento y contacto | 4 | ⏳ siguiente | `010-reglamento-contacto` |
| 11 | Cierre: accesibilidad, móvil, rendimiento, 404/metadatos, copias, despliegue independiente | 1–10 | ⏳ | `011-cierre` |

## Fuera de alcance (salvo nueva instrucción)

Pasarela de pago o inscripción propia, envío de correo desde servidor, cronometraje en directo,
varias cuentas de administrador con roles, publicación en producción y cambio de dominio.
