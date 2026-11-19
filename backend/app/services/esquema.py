"""Estado del esquema: compara la revisión aplicada con la cabeza de Alembic."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

RAIZ = Path(__file__).resolve().parents[2]


class EstadoEsquema(StrEnum):
    DISPONIBLE = "disponible"
    MIGRACIONES_PENDIENTES = "migraciones_pendientes"
    BASE_INACCESIBLE = "base_de_datos_inaccesible"


@lru_cache
def revisiones_cabeza() -> frozenset[str]:
    cfg = Config(str(RAIZ / "alembic.ini"))
    return frozenset(ScriptDirectory.from_config(cfg).get_heads())


def estado_esquema(engine: Engine) -> EstadoEsquema:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            actuales = frozenset(MigrationContext.configure(conn).get_current_heads())
    except SQLAlchemyError:
        return EstadoEsquema.BASE_INACCESIBLE
    if actuales != revisiones_cabeza():
        return EstadoEsquema.MIGRACIONES_PENDIENTES
    return EstadoEsquema.DISPONIBLE
