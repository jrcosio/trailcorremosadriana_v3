"""Regla común de referencias de contenido a recursos (data-model.md de la feature 003)."""

import re
from urllib.parse import urlsplit

MAX_REFERENCIA = 2200
PATRON_MEDIA = re.compile(r"^/media/[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$")
PATRON_REUSED = re.compile(r"^/reused/[A-Za-z0-9_./-]+$")


def url_externa_segura(valor: str) -> bool:
    """Destino de pago o inscripción: vacío o https con host, sin credenciales (005 FR-002)."""
    if valor == "":
        return True
    if len(valor) > MAX_REFERENCIA or any(c.isspace() for c in valor):
        return False
    partes = urlsplit(valor)
    return (
        partes.scheme == "https"
        and bool(partes.hostname)
        and not partes.username
        and not partes.password
    )


def referencia_valida(valor: str) -> bool:
    """Vacía, `/reused/…`, archivo `/media/<clave>` o `https://` sin credenciales."""
    if valor == "":
        return True
    if len(valor) > MAX_REFERENCIA:
        return False
    if valor.startswith("/reused/"):
        return bool(PATRON_REUSED.match(valor)) and ".." not in valor.split("/")
    if valor.startswith("/media/"):
        return bool(PATRON_MEDIA.match(valor))
    partes = urlsplit(valor)
    return (
        partes.scheme == "https"
        and bool(partes.hostname)
        and not partes.username
        and not partes.password
    )
