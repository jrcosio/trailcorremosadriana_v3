"""Entrada de patrocinadores y colaboradores (data-model.md de la feature 009)."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field

from app.schemas.evento import Texto, _destino_externo, _entero_no_negativo, _referencia


def _orden(valor: object) -> int:
    return 0 if valor in (None, "") else _entero_no_negativo(valor)


class EntidadEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Texto = Field(min_length=1, max_length=150)
    image: Annotated[Texto, AfterValidator(_referencia)] = Field(min_length=1)
    url: Annotated[Texto, AfterValidator(_destino_externo)] = ""
    order: Annotated[int, BeforeValidator(_orden)] = 0
    published: bool = False
    version: int = Field(default=0, ge=0)
