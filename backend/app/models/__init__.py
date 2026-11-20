"""Modelos SQLAlchemy. Importarlos aquí los registra en `Base.metadata` (Alembic)."""

from app.models.administracion import Administrador, LimiteLogin, Sesion
from app.models.archivos import Archivo
from app.models.base import Base
from app.models.clasificaciones import Clasificacion, ImportacionCsv, Resultado
from app.models.evento import Carrera, CarreraEdicion, Edicion

__all__ = [
    "Administrador",
    "Archivo",
    "Base",
    "Carrera",
    "Clasificacion",
    "CarreraEdicion",
    "Edicion",
    "ImportacionCsv",
    "LimiteLogin",
    "Resultado",
    "Sesion",
]
