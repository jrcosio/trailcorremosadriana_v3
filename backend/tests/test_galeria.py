"""Feature 008 · Galería: álbumes, fotos, históricos, versiones y validación."""

import pytest

from tests.conftest import JPEG, consultar, crear_cliente, escribir, importar_datos, subir

HISTORICOS = {
    "edicion-2026": "https://photos.app.goo.gl/A5ksyLsC3cSc2HHWA",
    "edicion-2025": "https://photos.app.goo.gl/cubEC9ev2Y9N5LAYA",
    "edicion-2024": "https://photos.app.goo.gl/NvoukMiSsSCHmijw9",
}


def _publicos(c):
    return c.get("/api/content").json()["data"]["albums"]


def _privados(c):
    return {
        a["id"]: a for a in c.get("/api/content", params={"admin": "1"}).json()["data"]["albums"]
    }


def _album(c, **extra):
    fotos = [subir(c, JPEG, f"f{i}.jpg").json()["url"] for i in range(2)]
    return {
        "title": "Entrenamiento 2027",
        "year": "2027",
        "image": fotos[0],
        "url": "",
        "photos": fotos,
        "published": False,
        **extra,
    }


def test_historicos_importados_en_orden(admin_importado):
    publicos = _publicos(admin_importado)
    assert [a["id"] for a in publicos] == list(HISTORICOS)
    assert {a["id"]: a["url"] for a in publicos} == HISTORICOS
    assert all(a["photos"] == [] and a["photoAlts"] == [] for a in publicos)


def test_borrador_publicar_quitar_foto_retirar_borrar(admin_importado, base_importada):
    datos = _album(admin_importado)
    r = escribir(admin_importado, "PUT", "/api/admin/albumes/entreno-2027", json=datos)
    assert r.status_code == 200 and r.json()["version"] == 1
    assert r.json()["photoAlts"] == [
        "Entrenamiento 2027 · fotografía 1",
        "Entrenamiento 2027 · fotografía 2",
    ]
    assert "entreno-2027" not in [a["id"] for a in _publicos(admin_importado)]
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/albumes/entreno-2027",
        json={**datos, "published": True, "version": 1},
    )
    assert [a["id"] for a in _publicos(admin_importado)][
        0
    ] == "entreno-2027"  # 2027, el más reciente
    archivos_antes = consultar(base_importada, "SELECT count(*) FROM archivos")[0][0]
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/albumes/entreno-2027",
        json={**datos, "photos": datos["photos"][1:], "published": True, "version": 2},
    )
    assert r.json()["photos"] == datos["photos"][1:]
    assert (
        consultar(base_importada, "SELECT count(*) FROM archivos")[0][0] == archivos_antes
    )  # no se borran
    assert admin_importado.get(datos["photos"][0]).status_code == 200
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/albumes/entreno-2027",
        json={**datos, "published": False, "version": 3},
    )
    assert "entreno-2027" not in [a["id"] for a in _publicos(admin_importado)]
    assert (
        escribir(
            admin_importado, "DELETE", "/api/admin/albumes/entreno-2027", params={"version": 1}
        ).status_code
        == 409
    )
    assert (
        escribir(
            admin_importado, "DELETE", "/api/admin/albumes/entreno-2027", params={"version": 4}
        ).status_code
        == 200
    )
    assert consultar(base_importada, "SELECT count(*) FROM fotografias")[0][0] == 0


def test_doble_envio_y_conflicto(admin_importado, base_importada):
    datos = _album(admin_importado)
    assert (
        escribir(admin_importado, "PUT", "/api/admin/albumes/doble", json=datos).status_code == 200
    )
    assert (
        escribir(admin_importado, "PUT", "/api/admin/albumes/doble", json=datos).status_code == 409
    )
    assert consultar(base_importada, "SELECT count(*) FROM albumes WHERE slug = 'doble'")[0][0] == 1


@pytest.mark.parametrize(
    ("cambio", "campo"),
    [
        ({"title": ""}, "nombre"),
        ({"year": "1999"}, "edición"),
        ({"image": ""}, "fotografía"),
        ({"url": "http://photos.example/x"}, "álbum externo"),
        ({"photos": ["javascript:alert(1)"]}, "fotografías del álbum"),
        (
            {"photos": ["/media/0123456789abcdef0123456789abcdef.jpg"] * 501},
            "fotografías del álbum",
        ),
    ],
)
def test_validaciones(admin_importado, cambio, campo):
    datos = {
        "title": "X",
        "year": "2027",
        "image": "/reused/fondos/fondo.webp",
        "url": "",
        "photos": [],
        **cambio,
    }
    r = escribir(admin_importado, "PUT", "/api/admin/albumes/malo", json=datos)
    assert r.status_code == 400 and r.json() == {"error": f"Revisa el campo «{campo}»."}


def test_proteccion_persistencia_e_importacion(admin_importado, base_importada):
    with crear_cliente(base_importada) as anonimo:
        assert anonimo.put("/api/admin/albumes/x", json={}).status_code == 401
    historico = _privados(admin_importado)["edicion-2026"]
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/albumes/edicion-2026",
        json={**historico, "title": "Editado", "version": historico["version"]},
    )
    importar_datos(base_importada)
    with crear_cliente(base_importada) as reiniciada:
        assert {a["id"]: a["title"] for a in _publicos(reiniciada)}["edicion-2026"] == "Editado"
    assert consultar(base_importada, "SELECT count(*) FROM albumes")[0][0] == 3
