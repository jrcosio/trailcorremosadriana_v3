"""Entrada de noticias (data-model.md de la feature 007)."""

from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.schemas.evento import Texto, _referencia


def _fecha_dia(valor: str) -> str:
    """'' o día AAAA-MM-DD (de un ISO completo se toma la fecha)."""
    if valor == "":
        return valor
    try:
        return date.fromisoformat(valor[:10]).isoformat()
    except ValueError as exc:
        raise ValueError("Fecha no válida") from exc


class NoticiaEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: Texto = Field(min_length=1, max_length=200)
    category: Texto = Field(default="", max_length=60)
    date: Annotated[Texto, AfterValidator(_fecha_dia)] = ""
    image: Annotated[Texto, AfterValidator(_referencia)] = ""
    excerpt: Texto = Field(default="", max_length=500)
    body: str = Field(min_length=1, max_length=50_000)
    published: bool = False
    version: int = Field(default=0, ge=0)
