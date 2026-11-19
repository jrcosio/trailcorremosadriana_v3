"""US2 · HEAD de /media devuelve las mismas cabeceras sin cuerpo."""

from tests.conftest import JPEG, subir


def test_head(cliente_admin):
    url = subir(cliente_admin, JPEG, "a.jpg").json()["url"]
    r = cliente_admin.head(url)
    assert r.status_code == 200
    assert r.content == b""
    assert r.headers["etag"] and r.headers["content-type"] == "image/jpeg"
