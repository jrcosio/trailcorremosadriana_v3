"""US1 · Subida autenticada: tipos, límites, metadatos, protección y fallos de almacenamiento."""

import hashlib
import re

import pytest

from app.storage import AlmacenamientoNoDisponible
from tests.conftest import (
    GPX,
    JPEG,
    ORIGEN,
    PDF,
    PNG,
    WEBP,
    consultar,
    crear_cliente,
    csrf,
    entrar,
    subir,
)

PATRON_URL = re.compile(r"^/media/[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$")


@pytest.mark.parametrize(
    ("datos", "nombre", "ext", "tipo"),
    [
        (JPEG, "foto.jpg", "jpg", "image/jpeg"),
        (PNG, "logo.png", "png", "image/png"),
        (WEBP, "foto.webp", "webp", "image/webp"),
        (PDF, "reglamento.pdf", "pdf", "application/pdf"),
        (GPX, "trail-27k.gpx", "gpx", "application/gpx+xml"),
        (PNG, "en-realidad-png.jpg", "png", "image/png"),  # se respeta el contenido real
    ],
)
def test_subida_correcta_registra_metadatos(
    cliente_admin, base_con_admin, datos, nombre, ext, tipo
):
    r = subir(cliente_admin, datos, nombre)
    assert r.status_code == 200, r.text
    url = r.json()["url"]
    assert PATRON_URL.match(url) and url.endswith("." + ext)
    clave = url.removeprefix("/media/")
    [(t, tam, sha, nom, autor)] = consultar(
        base_con_admin,
        "SELECT a.tipo, a.tamano, a.sha256, a.nombre_original, d.usuario "
        "FROM archivos a JOIN administradores d ON d.id = a.subido_por WHERE a.clave = :c",
        c=clave,
    )
    assert (t, tam, sha, nom, autor) == (
        tipo,
        len(datos),
        hashlib.sha256(datos).hexdigest(),
        nombre,
        "admin",
    )
    assert nombre not in clave


def test_claves_distintas_para_el_mismo_archivo(cliente_admin):
    a = subir(cliente_admin, JPEG).json()["url"]
    b = subir(cliente_admin, JPEG).json()["url"]
    assert a != b


def test_demasiado_grande_413_sin_rastro(base_con_admin):
    with crear_cliente(base_con_admin, upload_max_bytes=1000) as c:
        entrar(c)
        r = subir(c, JPEG + b"\x00" * 2000, "grande.jpg")
    assert r.status_code == 413
    assert r.json()["error"].startswith("Máximo")
    assert consultar(base_con_admin, "SELECT count(*) FROM archivos")[0][0] == 0


def test_tipo_no_admitido_400_sin_rastro(cliente_admin, base_con_admin):
    for datos, nombre in [
        (b"<svg xmlns='http://www.w3.org/2000/svg'/>", "a.svg"),
        (b"hola", "a.jpg"),
    ]:
        r = subir(cliente_admin, datos, nombre)
        assert r.status_code == 400
        assert r.json() == {"error": "Sube imágenes JPG, PNG o WebP, documentos PDF o rutas GPX."}
    assert consultar(base_con_admin, "SELECT count(*) FROM archivos")[0][0] == 0


def test_sin_archivo_o_campos_inesperados_400(cliente_admin):
    token = {"X-CSRF-Token": csrf(cliente_admin)}
    casos = [
        cliente_admin.post("/api/upload", headers=token, data={"otro": "x"}),
        cliente_admin.post(
            "/api/upload",
            headers=token,
            files=[("file", ("a.jpg", JPEG)), ("file", ("b.jpg", JPEG))],
        ),
        cliente_admin.post(
            "/api/upload", headers=token, files={"file": ("a.jpg", JPEG)}, data={"extra": "1"}
        ),
        cliente_admin.post("/api/upload", headers=token),
    ]
    for r in casos:
        assert r.status_code == 400, r.text


def test_proteccion_de_la_002(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        assert c.post("/api/upload", files={"file": ("a.jpg", JPEG)}).status_code == 401
        entrar(c)
        assert c.post("/api/upload", files={"file": ("a.jpg", JPEG)}).status_code == 403  # sin CSRF
        c.headers["Origin"] = "https://atacante.example"
        assert subir(c, JPEG).status_code == 403
        c.headers["Origin"] = ORIGEN
    assert consultar(base_con_admin, "SELECT count(*) FROM archivos")[0][0] == 0


def test_fallo_del_almacenamiento_503_sin_fila(cliente_admin, base_con_admin):
    class Roto:
        def guardar(self, *_):
            raise AlmacenamientoNoDisponible

        def leer(self, *_):
            raise AlmacenamientoNoDisponible

    cliente_admin.app.state.almacenamiento = Roto()
    r = subir(cliente_admin, JPEG)
    assert r.status_code == 503
    assert r.json() == {"error": "No se ha podido guardar el archivo. Inténtalo más tarde."}
    assert consultar(base_con_admin, "SELECT count(*) FROM archivos")[0][0] == 0
