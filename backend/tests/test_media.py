"""US2 · Entrega pública de archivos: bytes, cabeceras, caché, 304 y 404."""

import hashlib

import pytest

from tests.conftest import GPX, JPEG, PDF, crear_cliente, subir


def _clave(cliente, datos, nombre="a.bin"):
    return subir(cliente, datos, nombre).json()["url"]


def test_bytes_y_cabeceras_de_imagen(cliente_admin, base_con_admin):
    url = _clave(cliente_admin, JPEG, "foto.jpg")
    with crear_cliente(base_con_admin) as anonimo:  # entrega pública, sin sesión
        anonimo.app.state.almacenamiento = cliente_admin.app.state.almacenamiento
        r = anonimo.get(url)
    assert r.status_code == 200
    assert r.content == JPEG
    h = r.headers
    assert h["content-type"] == "image/jpeg"
    assert h["cache-control"] == "public, max-age=31536000, immutable"
    assert h["etag"] == f'"{hashlib.sha256(JPEG).hexdigest()}"'
    assert h["x-content-type-options"] == "nosniff"
    assert h["content-security-policy"] == "default-src 'none'; sandbox"
    assert h["content-disposition"] == "inline"


def test_gpx_como_descarga_con_nombre_saneado(cliente_admin):
    url = _clave(cliente_admin, GPX, "Trail 27K <final>.gpx")
    r = cliente_admin.get(url)
    assert r.headers["content-type"].startswith("application/gpx+xml")
    assert r.headers["content-disposition"] == 'attachment; filename="Trail-27K-final.gpx"'


def test_pdf_inline(cliente_admin):
    r = cliente_admin.get(_clave(cliente_admin, PDF, "reglamento.pdf"))
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"] == "inline"


def test_304_con_etag(cliente_admin):
    url = _clave(cliente_admin, JPEG)
    etag = cliente_admin.get(url).headers["etag"]
    for valor in (etag, f"W/{etag}", f'"otro", {etag}'):
        r = cliente_admin.get(url, headers={"If-None-Match": valor})
        assert r.status_code == 304
        assert r.content == b""
    assert cliente_admin.get(url, headers={"If-None-Match": '"distinto"'}).status_code == 200


@pytest.mark.parametrize(
    "ruta",
    [
        "/media/0123456789abcdef0123456789abcdef.jpg",  # formato válido, inexistente
        "/media/no-valida.jpg",
        "/media/0123456789ABCDEF0123456789ABCDEF.jpg",
        "/media/0123456789abcdef0123456789abcdef.svg",
        "/media/..%2F..%2Fetc%2Fpasswd",
    ],
)
def test_404_sin_detalles(cliente_admin, ruta):
    r = cliente_admin.get(ruta)
    assert r.status_code == 404
    assert r.json() == {"error": "Archivo no encontrado."}


def test_404_si_falta_el_objeto(cliente_admin, base_con_admin):
    url = _clave(cliente_admin, JPEG)

    class Vacio:
        def leer(self, *_):
            return None

    cliente_admin.app.state.almacenamiento = Vacio()
    assert cliente_admin.get(url).status_code == 404


def test_media_no_lleva_no_store(cliente_admin):
    r = cliente_admin.get(_clave(cliente_admin, JPEG))
    assert "no-store" not in r.headers["cache-control"]
