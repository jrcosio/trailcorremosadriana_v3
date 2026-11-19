"""Contrato transitorio `SiteData` (data-model.md de la feature 001).

Permite campos adicionales (compatibilidad con `passthrough` de la propuesta) y valida las
reglas de data-model.md: Settings.*, Item.id, Item.published, límites de colecciones y
`regulation`.
"""

import re
from datetime import datetime
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

PATRON_ID = r"^[A-Za-z0-9_-]{1,100}$"
PATRON_EDICION = r"^20\d\d$"
PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_URL = 2200


def _fecha_iso_con_zona(valor: str) -> str:
    if valor == "":
        return valor
    try:
        fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("La fecha debe estar vacía o en formato ISO 8601") from exc
    if fecha.tzinfo is None:
        raise ValueError("La fecha debe incluir zona horaria")
    return valor


def _https_sin_credenciales(valor: str) -> str:
    if valor == "":
        return valor
    partes = urlsplit(valor)
    if len(valor) > MAX_URL or partes.scheme != "https" or not partes.hostname:
        raise ValueError("Debe ser una URL https válida")
    if partes.username or partes.password:
        raise ValueError("La URL no puede contener credenciales")
    return valor


def _email(valor: str) -> str:
    if not PATRON_EMAIL.match(valor):
        raise ValueError("Correo electrónico no válido")
    return valor


class Settings(BaseModel):
    model_config = ConfigDict(extra="allow")

    edition: str = Field(pattern=PATRON_EDICION)
    date: Annotated[str, AfterValidator(_fecha_iso_con_zona)] = ""
    countdown: bool = True
    registrationsOpen: bool = False
    solidarityRegistration: Annotated[str, AfterValidator(_https_sin_credenciales)] = ""
    registrationMessage: str = Field(default="", max_length=2000)
    email: Annotated[str, AfterValidator(_email)]
    phone: str = Field(default="", max_length=40)
    instagram: Annotated[str, AfterValidator(_https_sin_credenciales)] = ""


class Item(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(pattern=PATRON_ID)
    published: bool


class SiteData(BaseModel):
    model_config = ConfigDict(extra="allow")

    settings: Settings
    races: list[Item] = Field(max_length=30)
    news: list[Item] = Field(max_length=500)
    albums: list[Item] = Field(max_length=200)
    results: list[Item] = Field(max_length=500)
    sponsors: list[Item] = Field(max_length=200)
    collaborators: list[Item] = Field(max_length=200)
    regulation: str = Field(max_length=100_000)
