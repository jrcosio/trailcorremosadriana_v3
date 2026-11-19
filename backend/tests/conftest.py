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


ORIGEN = "http://localhost:8080"
PASSWORD = "clave-de-prueba-segura"


def crear_cliente(database_url: str, ip: str = "203.0.113.10", **ajustes) -> TestClient:
    """Cliente de pruebas con Origin permitido por defecto y una IP de cliente concreta."""
    ajustes.setdefault("public_origin", ORIGEN)
    # httpx no envía cookies Secure por HTTP; las pruebas de atributos lo activan explícitamente.
    ajustes.setdefault("cookie_secure", False)
    app = create_app(Settings(database_url=database_url, **ajustes))
    return TestClient(app, base_url=ORIGEN, client=(ip, 50000), headers={"Origin": ORIGEN})


def crear_admin(database_url: str, usuario: str = "admin", password: str = PASSWORD) -> None:
    """Crea un administrador directamente con el servicio (como haría el comando de operador)."""
    from sqlalchemy.orm import Session

    from app.services import administradores

    engine = create_engine(database_url)
    with Session(engine) as db:
        administradores.crear(db, usuario, password)
    engine.dispose()


def entrar(cliente: TestClient, usuario: str = "admin", password: str = PASSWORD):
    return cliente.post("/api/login", json={"username": usuario, "password": password})


def csrf(cliente: TestClient) -> str:
    return cliente.cookies.get("penasagra_csrf") or ""


def consultar(database_url: str, sql: str, **params):
    engine = create_engine(database_url)
    with engine.begin() as conn:
        resultado = conn.execute(text(sql), params)
        filas = resultado.all() if resultado.returns_rows else []
    engine.dispose()
    return filas


@pytest.fixture
def cliente(base_migrada: str) -> Iterator[TestClient]:
    with crear_cliente(base_migrada) as c:
        yield c


@pytest.fixture
def base_con_admin(base_migrada: str) -> str:
    crear_admin(base_migrada)
    return base_migrada


@pytest.fixture
def cliente_admin(base_con_admin: str) -> Iterator[TestClient]:
    """Cliente con una sesión de administrador ya iniciada."""
    with crear_cliente(base_con_admin) as c:
        r = entrar(c)
        assert r.status_code == 200, r.text
        yield c
