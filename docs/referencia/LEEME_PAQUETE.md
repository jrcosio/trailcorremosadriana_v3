# Trail Peñasagra · paquete de desarrollo

Entrega del 19 de noviembre de 2026. Incluye el código de la propuesta revisada, sus recursos originales, una copia del contenido publicado y especificaciones para continuar con Claude Code o Codex.

Actualización: clasificaciones mediante un CSV por carrera y edición, con vista previa y tabla de participantes. El Dorsal Solidario no tiene clasificación. Consulta [el contrato CSV](docs/13_CLASIFICACIONES_CSV.md).

Arquitectura aprobada para el siguiente agente: **FastAPI + PostgreSQL + SQLAlchemy/Alembic + R2/S3 + Docker Compose**. Su especificación y plan están en [14_BACKEND_FASTAPI_POSTGRESQL.md](docs/14_BACKEND_FASTAPI_POSTGRESQL.md). Esta actualización es documental; el código conserva el backend actual de la propuesta.

## Empieza aquí

1. Abre esta carpeta completa con Claude Code o Codex, no solo `proyecto/`.
2. Usa el prompt de [PROMPT_PARA_CLAUDE_O_CODEX.md](PROMPT_PARA_CLAUDE_O_CODEX.md).
3. Lee [el alcance](docs/01_PRODUCTO_Y_ALCANCE.md), [el estilo](docs/02_ESTILO_VISUAL.md), [las pantallas](docs/03_MAPA_PANTALLAS.md) y [el estado real](docs/08_ESTADO_Y_PENDIENTES.md).
4. Sigue [la puesta en marcha](docs/07_PUESTA_EN_MARCHA.md).

## Qué contiene

| Carpeta o archivo | Uso |
|---|---|
| `proyecto/` | Aplicación React/TypeScript con Vinext/Vite, Worker, API, D1, R2 y migraciones |
| `docs/screens/publica/` | Una ficha Markdown por pantalla pública, incluidos sus detalles |
| `docs/screens/admin/` | Una ficha por acceso, listado, creación, edición y configuración del administrador |
| `docs/` | Producto, estilo, arquitectura, datos, flujos, instalación, pendientes y aceptación |
| `contenido/contenido-publicado.json` | Copia del contenido público recuperado del despliegue |
| `PROCEDENCIA.json` | Commit de origen y diferencias controladas de esta exportación |
| `INVENTARIO_RECURSOS.csv` | Rutas, dimensiones y usos de los recursos locales |
| `MANIFIESTO_SHA256.json` | Huellas de los archivos incluidos |
| `AGENTS.md` / `CLAUDE.md` | Instrucciones de continuidad para agentes |

## Referencias

- Propuesta visual: https://trail-penasagra-nueva-web.jrblanco.chatgpt.site
- Índice de pantallas: https://trail-penasagra-nueva-web.jrblanco.chatgpt.site/pantallas
- Sitio original: https://xn--trailpeasagra-okb.com/

El administrador de la aplicación utiliza sus propias credenciales. El alojamiento de la propuesta puede mostrar un paso previo de acceso con ChatGPT; el desarrollo local no lo necesita.

La copia conserva las decisiones aprobadas: título «TRAIL PENASAGRA», silueta de Adriana, texto de la causa ampliado, ausencia del rótulo sobre el contador, botón «INSCRIPCIONES», patrocinadores grandes y acceso al pago del dorsal solidario condicionado a configuración y apertura.

No se incluyen contraseñas del despliegue, sesiones, tokens, `.git`, dependencias instaladas ni una copia de la base de datos privada. Sí se incluyen las imágenes locales y el contenido publicado. El identificador del alojamiento se ha retirado del manifiesto de la copia para trabajar como proyecto independiente.
