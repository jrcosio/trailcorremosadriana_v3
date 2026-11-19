"""Conexión a PostgreSQL con SQLAlchemy (síncrono, psycopg 3)."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def crear_engine(database_url: str, connect_timeout: int = 3) -> Engine:
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        connect_args={"connect_timeout": connect_timeout},
    )


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return crear_engine(settings.database_url, settings.db_connect_timeout)


def get_session() -> Iterator[Session]:
    fabrica = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with fabrica() as session:
        yield session
