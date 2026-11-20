"""Entrada del reglamento de la edición actual (data-model.md `Edicion.reglamento`, feature 010)."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

MAX_REGLAMENTO = 200_000


def normalizar(valor: object) -> str:
    """Saltos de línea `\\n` y sin espacios exteriores; el resto no cambia (research R3)."""
    if not isinstance(valor, str):
        raise ValueError("Texto no válido")
    return valor.replace("\r\n", "\n").replace("\r", "\n").strip()


class ReglamentoEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    regulation: Annotated[str, BeforeValidator(normalizar)] = Field(
        min_length=1, max_length=MAX_REGLAMENTO
    )
    version: int = Field(ge=0)
