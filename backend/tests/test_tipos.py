"""US1 · Detección de tipo por contenido y validación segura de GPX."""

import pytest

from app.services.archivos import detectar_tipo, sanear_nombre
from tests.conftest import GPX, JPEG, PDF, PNG, WEBP


@pytest.mark.parametrize(
    ("datos", "tipo"),
    [
        (JPEG, "image/jpeg"),
        (PNG, "image/png"),
        (WEBP, "image/webp"),
        (PDF, "application/pdf"),
        (GPX, "application/gpx+xml"),
        (b"\xef\xbb\xbf" + GPX, "application/gpx+xml"),  # BOM UTF-8 antes de la declaración
        (b"  \n<gpx/>", "application/gpx+xml"),  # espacios sin declaración XML
        (GPX.replace(b'<?xml version="1.0" encoding="UTF-8"?>\n', b""), "application/gpx+xml"),
    ],
)
def test_detecta_tipos_admitidos(datos, tipo):
    assert detectar_tipo(datos) == tipo


SVG = (
    b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
)
HTML = b"<!doctype html><html><body><script>alert(1)</script></body></html>"
XXE = b'<?xml version="1.0"?><!DOCTYPE gpx [<!ENTITY x SYSTEM "file:///etc/passwd">]><gpx>&x;</gpx>'
BOMBA = (
    b'<?xml version="1.0"?><!DOCTYPE gpx [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;&a;">]>'
    b"<gpx>&b;</gpx>"
)


@pytest.mark.parametrize(
    "datos",
    [
        SVG,
        HTML,
        b"texto plano renombrado a .jpg",
        b"MZ\x90\x00\x03\x00\x00\x00",  # ejecutable de Windows
        b"\x7fELF\x02\x01\x01",  # ejecutable ELF
        XXE,
        BOMBA,
        b'<?xml version="1.0"?><kml><Document/></kml>',  # XML con otra raíz
        b"<gpx><trk>",  # mal formado
        b"",
        b"GIF89a\x01\x00",  # GIF no admitido
    ],
)
def test_rechaza(datos):
    assert detectar_tipo(datos) is None


@pytest.mark.parametrize(
    ("nombre", "esperado"),
    [
        ("foto.jpg", "foto.jpg"),
        ("../../etc/passwd", "passwd"),
        ("C:\\Users\\x\\ruta.gpx", "ruta.gpx"),
        ("con\x00control\x1f.png", "concontrol.png"),
        ("   ", None),
        ("", None),
        ("a" * 400 + ".pdf", "a" * 251 + ".pdf"),
    ],
)
def test_sanea_nombre(nombre, esperado):
    assert sanear_nombre(nombre) == esperado
