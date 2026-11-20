"""Modelos SQLAlchemy. Importarlos aquí los registra en `Base.metadata` (Alembic)."""

from app.models.administracion import Administrador, LimiteLogin, Sesion
from app.models.archivos import Archivo
from app.models.base import Base
from app.models.clasificaciones import Clasificacion, ImportacionCsv, Resultado
from app.models.evento import Carrera, CarreraEdicion, Edicion
from app.models.galeria import Album, Fotografia
from app.models.noticias import Noticia

__all__ = [
    "Administrador",
    "Album",
    "Archivo",
    "Base",
    "Carrera",
    "Clasificacion",
    "CarreraEdicion",
    "Edicion",
    "Fotografia",
    "ImportacionCsv",
    "LimiteLogin",
    "Noticia",
    "Resultado",
    "Sesion",
]
