# Trail Peñasagra — Corremos por Adriana

Web de la carrera solidaria de montaña Trail Peñasagra (Cosío, Rionansa, Cantabria) y panel de
administración para la organización.

- **Frontend**: React + TypeScript (Vite), con las pantallas aprobadas.
- **Backend**: FastAPI + PostgreSQL (SQLAlchemy, Alembic).
- **Ejecución**: Docker Compose, con Caddy como entrada en el mismo origen.

## Empezar

Ver [docs/desarrollo.md](docs/desarrollo.md). En resumen:

```bash
docker compose build
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.cli importar-inicial
docker compose up -d        # http://localhost:8080
```

## Desplegar en el servidor

Con el `.env` de producción copiado en la carpeta del repositorio: `sudo ./deploy.sh`. Instala o
actualiza todo, y sustituye a la web anterior si la encuentra. Ver la sección 0 de
[docs/operacion.md](docs/operacion.md).

## Documentación

| Documento | Contenido |
|---|---|
| [docs/ESTADO_PROYECTO.md](docs/ESTADO_PROYECTO.md) | Estado actual, decisiones, pruebas y punto de continuidad |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Features y su estado |
| [docs/arquitectura.md](docs/arquitectura.md) | Procesos, estructura y decisiones técnicas |
| [docs/desarrollo.md](docs/desarrollo.md) | Arranque, pruebas y comandos |
| [docs/operacion.md](docs/operacion.md) | Despliegue independiente, HTTPS, R2, copias, restauración y recuperación del acceso |
| [docs/PROCEDENCIA_RECURSOS.md](docs/PROCEDENCIA_RECURSOS.md) | Origen y licencias de recursos y código reutilizados |
| [docs/referencia/](docs/referencia/README.md) | Documentación funcional aprobada y discrepancias |
| [specs/](specs/) | Especificaciones Spec Kit por feature |
| [.specify/memory/constitution.md](.specify/memory/constitution.md) | Principios del proyecto |

## Metodología

Spec-Driven Development con GitHub Spec Kit: cada feature pasa por specify → plan → tasks →
analyze → implement → converge, con pruebas contra PostgreSQL real.
