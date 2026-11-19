"""US4 · El contrato de contenido toma evento y pruebas de PostgreSQL (FR-011, SC-005)."""

import json

from app.services.contenido import RUTA_SEMILLA
from tests.conftest import consultar, crear_cliente, escribir


def test_publico_igual_que_la_semilla_tras_importar(base_importada):
    semilla = json.loads(RUTA_SEMILLA.read_text(encoding="utf-8"))
    with crear_cliente(base_importada) as c:
        data = c.get("/api/content").json()["data"]
    assert data["settings"]["edition"] == "2027" and data["settings"]["date"] == ""
    campos = [
        "id",
        "title",
        "label",
        "km",
        "elevation",
        "price",
        "image",
        "color",
        "description",
        "terrain",
        "start",
        "route",
        "wikiloc",
        "gpx",
        "registration",
        "edition",
        "aid",
        "published",
    ]
    assert [{k: r[k] for k in campos} for r in data["races"]] == [
        {k: r[k] for k in campos} for r in semilla["races"]
    ]
    assert "version" not in data["races"][0] and "eventVersion" not in data["settings"]


def test_privado_con_versiones_y_borradores(admin_importado):
    actual = admin_importado.get("/api/content", params={"admin": "1"}).json()["data"]
    assert actual["settings"]["eventVersion"] == 1
    assert all("version" in r for r in actual["races"])
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/borrador",
        json={**actual["races"][0], "version": 0, "published": False},
    )
    assert r.status_code == 200
    privadas = [
        r["id"]
        for r in admin_importado.get("/api/content", params={"admin": "1"}).json()["data"]["races"]
    ]
    publicas = [r["id"] for r in admin_importado.get("/api/content").json()["data"]["races"]]
    assert "borrador" in privadas and "borrador" not in publicas


def test_ficha_publicada_mas_reciente(admin_importado, base_importada):
    actual = {
        r["id"]: r
        for r in admin_importado.get("/api/content", params={"admin": "1"}).json()["data"]["races"]
    }
    # Nueva ficha 2027 en borrador: lo público sigue mostrando la de 2026.
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/trail-27k",
        json={**actual["trail-27k"], "edition": "2027", "price": "30 €", "published": False},
    )
    publica = {r["id"]: r for r in admin_importado.get("/api/content").json()["data"]["races"]}[
        "trail-27k"
    ]
    assert (publica["edition"], publica["price"]) == ("2026", "28 €")


def test_otros_campos_siguen_de_la_semilla(base_importada):
    with crear_cliente(base_importada) as c:
        data = c.get("/api/content").json()["data"]
    assert data["settings"]["email"] == "asociacionpenasagra@gmail.com"
    assert len(data["sponsors"]) == 8 and len(data["albums"]) == 3


def test_base_caida_503(base_importada):
    with crear_cliente("postgresql+psycopg://trail:clave@127.0.0.1:1/trail") as c:
        assert c.get("/api/content").status_code == 503


def test_cambios_persisten_en_otra_instancia(admin_importado, base_importada):
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/evento",
        json={
            "edition": "2027",
            "date": "2027-07-10T07:00:00.000Z",
            "countdown": True,
            "version": 1,
        },
    )
    with crear_cliente(base_importada) as reiniciada:
        assert (
            reiniciada.get("/api/content").json()["data"]["settings"]["date"]
            == "2027-07-10T07:00:00.000Z"
        )
    assert consultar(base_importada, "SELECT count(*) FROM ediciones")[0][0] == 2
