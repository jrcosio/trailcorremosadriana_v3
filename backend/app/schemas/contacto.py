"""Entrada de la configuración de contacto (data-model.md `Configuracion`, feature 010)."""

import re
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.core.referencias import url_externa_segura
from app.schemas.evento import Texto

CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONO = re.compile(r"^\+?[0-9 ()-]+$")
HOSTS_INSTAGRAM = {"instagram.com", "www.instagram.com"}


def _correo(valor: str) -> str:
    if len(valor) > 254 or not CORREO.match(valor):
        raise ValueError("Correo no válido")
    return valor


def _telefono(valor: str) -> str:
    digitos = sum(c.isdigit() for c in valor)
    if len(valor) > 30 or not TELEFONO.match(valor) or not 6 <= digitos <= 15:
        raise ValueError("Teléfono no válido")
    return valor


def _instagram(valor: str) -> str:
    if (
        not valor
        or not url_externa_segura(valor)
        or urlsplit(valor).hostname not in HOSTS_INSTAGRAM
    ):
        raise ValueError("Enlace de Instagram no válido")
    return valor


class ContactoEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: Annotated[Texto, AfterValidator(_correo)]
    phone: Annotated[Texto, AfterValidator(_telefono)]
    instagram: Annotated[Texto, AfterValidator(_instagram)]
    version: int = Field(ge=0)
