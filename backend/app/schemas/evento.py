"""Entradas de evento y pruebas (validación de FR-006 y data-model.md de la feature 004)."""

import re
from decimal import Decimal, InvalidOperation
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field

from app.core.referencias import referencia_valida, url_externa_segura
from app.services.fechas import FechaNoValida, a_instante

PATRON_EDICION = r"^20\d\d$"
PATRON_GPX = re.compile(r"^/media/[0-9a-f]{32}\.gpx$")


def _fecha(valor: str) -> str:
    try:
        a_instante(valor)
    except FechaNoValida as exc:
        raise ValueError(str(exc)) from exc
    return valor


def _referencia(valor: str) -> str:
    if not referencia_valida(valor):
        raise ValueError("Referencia no válida")
    return valor


def _destino_externo(valor: str) -> str:
    if not url_externa_segura(valor):
        raise ValueError("Enlace externo no válido")
    return valor


def _gpx(valor: str) -> str:
    if valor and not (
        PATRON_GPX.match(valor) or (valor.startswith("https://") and referencia_valida(valor))
    ):
        raise ValueError("GPX no válido")
    return valor


def _km(valor: object) -> Decimal:
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Distancia no válida") from exc
    if (
        not numero.is_finite()
        or numero < 0
        or numero > Decimal("9999.99")
        or numero != round(numero, 2)
    ):
        raise ValueError("Distancia no válida")
    return numero


def _entero_no_negativo(valor: object) -> int:
    texto = str(valor).strip()
    if not texto.isdigit() or int(texto) > 100_000:
        raise ValueError("Número no válido")
    return int(texto)


def _texto(valor: object) -> str:
    return "" if valor is None else str(valor).strip()


Texto = Annotated[str, BeforeValidator(_texto)]


class EventoEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    edition: Annotated[str, BeforeValidator(_texto)] = Field(pattern=PATRON_EDICION)
    date: Annotated[Texto, AfterValidator(_fecha)] = ""
    countdown: bool = True
    version: int = Field(default=0, ge=0)


class CarreraEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: Texto = Field(min_length=1, max_length=150)
    label: Texto = Field(default="", max_length=60)
    color: Texto = Field(default="", pattern=r"^(#[0-9A-Fa-f]{6})?$")
    edition: Texto = Field(pattern=PATRON_EDICION)
    km: Annotated[Decimal, BeforeValidator(_km)]
    elevation: Annotated[int, BeforeValidator(_entero_no_negativo)]
    price: Texto = Field(min_length=1, max_length=40)
    start: Texto = Field(default="", pattern=r"^(([01]\d|2[0-3]):[0-5]\d)?$")
    terrain: Texto = Field(default="", max_length=150)
    description: Texto = Field(default="", max_length=5000)
    aid: Texto = Field(default="", max_length=1000)
    image: Annotated[Texto, AfterValidator(_referencia)] = Field(min_length=1)
    route: Annotated[Texto, AfterValidator(_referencia)] = ""
    wikiloc: Texto = Field(default="", pattern=r"^\d{0,20}$")
    gpx: Annotated[Texto, AfterValidator(_gpx)] = ""
    registration: Annotated[Texto, AfterValidator(_destino_externo)] = ""
    published: bool = False
    version: int = Field(default=0, ge=0)


class InscripcionesEntrada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    registrationsOpen: bool
    registrationMessage: Texto = Field(min_length=1, max_length=2000)
    solidarityRegistration: Annotated[Texto, AfterValidator(_destino_externo)] = ""
    version: int = Field(default=0, ge=0)
