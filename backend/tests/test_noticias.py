"""Feature 007 · Noticias: borradores, orden, versiones, validación e importación."""

import pytest

from tests.conftest import consultar, crear_cliente, escribir, importar_datos

NUEVA = {
    "title": "Abrimos voluntariado",
    "category": "Organización",
    "date": "2027-03-01",
    "image": "/reused/fondos/fondo.webp",
    "excerpt": "Resumen",
    "body": "Primer párrafo.\n\nSegundo <script>alert(1)</script> párrafo.",
    "published": False,
}


def _publicas(c):
    return [n["id"] for n in c.get("/api/content").json()["data"]["news"]]


def _privadas(c):
    return {n["id"]: n for n in c.get("/api/content", params={"admin": "1"}).json()["data"]["news"]}


def test_importadas_y_orden(admin_importado):
    # Sin fecha primero (anuncio vigente) y después por fecha descendente.
    assert _publicas(admin_importado) == ["proxima-edicion", "gracias-trail-2026"]
    gracias = _privadas(admin_importado)["gracias-trail-2026"]
    assert gracias["date"] == "2026-07-13" and gracias["category"] == ""
    assert gracias["image"] == "/reused/noticias/gracias_2026.webp"
    assert gracias["body"].count("\n\n") == 3


def test_borrador_publicar_retirar_borrar(admin_importado):
    r = escribir(admin_importado, "PUT", "/api/admin/noticias/voluntariado", json=NUEVA)
    assert r.status_code == 200 and r.json()["version"] == 1 and r.json()["published"] is False
    assert "voluntariado" not in _publicas(admin_importado)
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/noticias/voluntariado",
        json={**NUEVA, "published": True, "version": 1},
    )
    assert r.status_code == 200
    assert _publicas(admin_importado) == ["proxima-edicion", "voluntariado", "gracias-trail-2026"]
    assert (
        _privadas(admin_importado)["voluntariado"]["body"] == NUEVA["body"]
    )  # texto íntegro, sin interpretar
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/noticias/voluntariado",
        json={**NUEVA, "published": False, "version": 2},
    )
    assert "voluntariado" not in _publicas(admin_importado)
    assert (
        escribir(
            admin_importado, "DELETE", "/api/admin/noticias/voluntariado", params={"version": 1}
        ).status_code
        == 409
    )
    assert (
        escribir(
            admin_importado, "DELETE", "/api/admin/noticias/voluntariado", params={"version": 3}
        ).status_code
        == 200
    )
    assert "voluntariado" not in _privadas(admin_importado)
    assert (
        escribir(
            admin_importado, "DELETE", "/api/admin/noticias/voluntariado", params={"version": 3}
        ).status_code
        == 404
    )


def test_doble_envio_y_conflicto(admin_importado, base_importada):
    assert (
        escribir(admin_importado, "PUT", "/api/admin/noticias/doble", json=NUEVA).status_code == 200
    )
    assert (
        escribir(admin_importado, "PUT", "/api/admin/noticias/doble", json=NUEVA).status_code == 409
    )
    assert (
        consultar(base_importada, "SELECT count(*) FROM noticias WHERE slug = 'doble'")[0][0] == 1
    )


@pytest.mark.parametrize(
    ("cambio", "campo"),
    [
        ({"title": ""}, "nombre"),
        ({"title": "x" * 201}, "nombre"),
        ({"body": ""}, "contenido de la noticia"),
        ({"date": "31/12/2027"}, "fecha y hora"),
        ({"image": "javascript:alert(1)"}, "fotografía"),
        ({"category": "x" * 61}, "categoría"),
        ({"excerpt": "x" * 501}, "resumen"),
    ],
)
def test_validaciones(admin_importado, cambio, campo):
    r = escribir(admin_importado, "PUT", "/api/admin/noticias/mala", json={**NUEVA, **cambio})
    assert r.status_code == 400 and r.json() == {"error": f"Revisa el campo «{campo}»."}


def test_fecha_iso_completa_se_reduce_al_dia(admin_importado):
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/noticias/iso",
        json={**NUEVA, "date": "2027-03-01T10:00:00.000Z"},
    )
    assert r.status_code == 200 and r.json()["date"] == "2027-03-01"


def test_proteccion_y_persistencia(admin_importado, base_importada):
    with crear_cliente(base_importada) as anonimo:
        assert anonimo.put("/api/admin/noticias/x", json=NUEVA).status_code == 401
    escribir(
        admin_importado, "PUT", "/api/admin/noticias/persiste", json={**NUEVA, "published": True}
    )
    with crear_cliente(base_importada) as reiniciada:
        assert "persiste" in [
            n["id"] for n in reiniciada.get("/api/content").json()["data"]["news"]
        ]


def test_importacion_no_pisa(base_importada):
    consultar(
        base_importada, "UPDATE noticias SET titulo = 'Editada' WHERE slug = 'proxima-edicion'"
    )
    importar_datos(base_importada)
    assert (
        consultar(base_importada, "SELECT titulo FROM noticias WHERE slug = 'proxima-edicion'")[0][
            0
        ]
        == "Editada"
    )
    assert consultar(base_importada, "SELECT count(*) FROM noticias")[0][0] == 2
