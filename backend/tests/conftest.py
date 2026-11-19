"""Infraestructura de pruebas contra PostgreSQL real.

Cada prueba que lo necesita recibe una base de datos temporal (`trail_test_<id>`) creada en el
servidor PostgreSQL de Compose y eliminada al terminar. Nunca se usa SQLite.
"""

import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from alembic import command
from app.core.config import Settings, get_settings
from app.main import create_app

RAIZ = Path(__file__).resolve().parents[1]
URL_BASE = get_settings().database_url


def _engine_admin():
    url = make_url(URL_BASE).set(database="postgres")
    return create_engine(url, isolation_level="AUTOCOMMIT")


def aplicar_migraciones(database_url: str, revision: str = "head") -> None:
    cfg = Config(str(RAIZ / "alembic.ini"))
    cfg.attributes["database_url"] = database_url
    command.upgrade(cfg, revision)


@pytest.fixture
def base_temporal() -> Iterator[str]:
    """URL de una base de datos PostgreSQL vacía y exclusiva de la prueba."""
    nombre = f"trail_test_{uuid.uuid4().hex[:12]}"
    engine = _engine_admin()
    with engine.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{nombre}"'))
    yield make_url(URL_BASE).set(database=nombre).render_as_string(hide_password=False)
    with engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{nombre}" WITH (FORCE)'))
    engine.dispose()


@pytest.fixture
def base_migrada(base_temporal: str) -> str:
    aplicar_migraciones(base_temporal)
    return base_temporal


def crear_cliente(database_url: str, **ajustes) -> TestClient:
    return TestClient(create_app(Settings(database_url=database_url, **ajustes)))


@pytest.fixture
def cliente(base_migrada: str) -> Iterator[TestClient]:
    with crear_cliente(base_migrada) as c:
        yield c
