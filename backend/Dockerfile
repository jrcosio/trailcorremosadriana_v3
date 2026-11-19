# syntax=docker/dockerfile:1
# API de Trail Peñasagra — FastAPI sobre Python 3.13 gestionado con uv.

FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Imagen de pruebas: incluye dependencias de desarrollo y los tests.
FROM base AS test
RUN uv sync --locked --no-install-project
COPY . .
CMD ["pytest"]

# Imagen de ejecución: sin dependencias de desarrollo ni tests, usuario sin privilegios.
FROM base AS runtime
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir -p /data/media && chown app /data/media
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY seed ./seed
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
