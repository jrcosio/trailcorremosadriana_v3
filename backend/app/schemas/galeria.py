"""Entrada de álbumes (data-model.md de la feature 008)."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.schemas.evento import Texto, _destino_externo, _referencia


def _fotos(valores: list[str]) -> list[str]:
    for valor in valores:
        _referencia(valor)
        if not valor:
            raise ValueError("Fotografía vacía")
    return valores


class AlbumEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: Texto = Field(min_length=1, max_length=150)
    year: Texto = Field(pattern=r"^20\d\d$")
    image: Annotated[Texto, AfterValidator(_referencia)] = Field(min_length=1)
    url: Annotated[Texto, AfterValidator(_destino_externo)] = ""
    photos: Annotated[list[str], AfterValidator(_fotos)] = Field(
        default_factory=list, max_length=500
    )
    published: bool = False
    version: int = Field(default=0, ge=0)
