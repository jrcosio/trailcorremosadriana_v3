"""Entradas de clasificaciones (feature 006)."""

import uuid

from pydantic import BaseModel, ConfigDict, Field

PATRON_EDICION = r"^20\d\d$"
PATRON_ID = r"^[A-Za-z0-9_-]{1,100}$"


class VistaPreviaEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    csv: str = Field(min_length=1, max_length=1_000_000)
    mapping: dict[str, int]
    sourceFile: str = Field(min_length=5, max_length=255, pattern=r"(?i)\.csv$")
    raceId: str = Field(pattern=PATRON_ID)
    year: str = Field(pattern=PATRON_EDICION)
    id: str | None = Field(default=None, pattern=PATRON_ID)


class ClasificacionEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=200)
    year: str = Field(pattern=PATRON_EDICION)
    raceId: str = Field(pattern=PATRON_ID)
    published: bool = False
    importToken: uuid.UUID | None = None
    version: int = Field(default=0, ge=0)
