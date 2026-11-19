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


@pytest.mark.parametrize(
    ("valor", "valido"),
    [
        ("", True),
        ("https://www.gedsports.com/inscription/trail-sierra-de-penasagra--27-km", True),
        ("https://example.com/dorsal?modalidad=solidario", True),
        ("http://example.com/pago", False),
        ("javascript:alert(1)", False),
        ("https://usuario:clave@example.com/pago", False),
        ("https://", False),
        ("https:///sin-host", False),
        (" https://example.com", False),
        ("https://example.com/a b", False),
        ("/reused/img/x.webp", False),
        ("https://example.com/" + "a" * 2200, False),
    ],
)
def test_url_externa_segura(valor, valido):
    from app.core.referencias import url_externa_segura

    assert url_externa_segura(valor) is valido
