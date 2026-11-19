"""Regla común de referencias (FR-014 de la feature 003)."""

import pytest

from app.core.referencias import referencia_valida

CLAVE = "0123456789abcdef0123456789abcdef"


@pytest.mark.parametrize(
    "valor",
    [
        "",
        "/reused/img/trail_inscripciones.webp",
        "/reused/logos/patrocinadores/banner_andros.png",
        f"/media/{CLAVE}.webp",
        f"/media/{CLAVE}.gpx",
        "https://es.wikiloc.com/rutas-carrera-por-montana/trail-sierra-penasagra-260167031",
    ],
)
def test_aceptadas(valor):
    assert referencia_valida(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "http://example.com/x.jpg",
        "javascript:alert(1)",
        "https://usuario:clave@example.com/x",
        "/reused/../backend/.env",
        "/reused/img/<script>.png",
        f"/media/{CLAVE}.svg",
        "/media/../../etc/passwd",
        f"/media/{CLAVE.upper()}.png",
        "/images/adriana-silueta.png",
        "data:image/png;base64,AAAA",
        "https://" + "a" * 2200 + ".com",
        "//example.com/x.png",
    ],
)
def test_rechazadas(valor):
    assert not referencia_valida(valor)
