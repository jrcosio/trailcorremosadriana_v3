"""US2 · Pruebas y sus datos por edición (FR-004–009)."""

import pytest

from tests.conftest import consultar, crear_cliente, escribir

BASE = {
    "title": "Trail Peñasagra",
    "label": "LA PRUEBA REINA",
    "color": "#dc693a",
    "edition": "2026",
    "km": "27",
    "elevation": "1700",
    "price": "28 €",
    "start": "09:00",
    "terrain": "Sendero y pista de montaña",
    "description": "Descripción",
    "aid": "Braña de Roja · Meta",
    "image": "/reused/img/trail_inscripciones.webp",
    "route": "https://es.wikiloc.com/rutas-carrera-por-montana/trail-sierra-penasagra-260167031",
    "wikiloc": "260167031",
    "gpx": "",
    "registration": "",
    "published": True,
}


def _privadas(c):
    return {
        r["id"]: r for r in c.get("/api/content", params={"admin": "1"}).json()["data"]["races"]
    }


def _publicas(c):
    return {r["id"]: r for r in c.get("/api/content").json()["data"]["races"]}


def test_editar_prueba_existente(admin_importado):
    actual = _privadas(admin_importado)["trail-27k"]
    r = escribir(admin_importado, "PUT", "/api/admin/carreras/trail-27k", json={**actual, "km": 28})
    assert r.status_code == 200, r.text
    assert r.json()["km"] == "28" and r.json()["version"] == actual["version"] + 1
    assert _publicas(admin_importado)["trail-27k"]["km"] == "28"


def test_nueva_prueba_borrador_y_publicacion(admin_importado):
    nueva = {**BASE, "title": "Vertical", "km": "5.5", "published": False}
    r = escribir(admin_importado, "PUT", "/api/admin/carreras/vertical-5k", json=nueva)
    assert r.status_code == 200 and r.json()["version"] == 1 and r.json()["km"] == "5.5"
    assert "vertical-5k" not in _publicas(admin_importado)
    assert _privadas(admin_importado)["vertical-5k"]["published"] is False
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/vertical-5k",
        json={**nueva, "published": True, "version": 1},
    )
    assert r.status_code == 200
    assert list(_publicas(admin_importado))[-1] == "vertical-5k"  # orden al final


def test_doble_envio_no_duplica(admin_importado, base_importada):
    nueva = {**BASE, "published": False}
    assert (
        escribir(admin_importado, "PUT", "/api/admin/carreras/nueva", json=nueva).status_code == 200
    )
    assert (
        escribir(admin_importado, "PUT", "/api/admin/carreras/nueva", json=nueva).status_code == 409
    )
    assert (
        consultar(base_importada, "SELECT count(*) FROM carreras WHERE slug = 'nueva'")[0][0] == 1
    )


def test_cambiar_edicion_conserva_historico(admin_importado, base_importada):
    actual = _privadas(admin_importado)["speed-14k"]
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/speed-14k",
        json={**actual, "edition": "2027", "price": "20 €"},
    )
    assert r.status_code == 200 and r.json()["edition"] == "2027" and r.json()["version"] == 1
    fichas = consultar(
        base_importada,
        "SELECT e.anio, f.precio FROM carreras_edicion f JOIN carreras c ON c.id = f.carrera_id "
        "JOIN ediciones e ON e.id = f.edicion_id WHERE c.slug = 'speed-14k' ORDER BY e.anio",
    )
    assert fichas == [(2026, "18 €"), (2027, "20 €")]
    assert _publicas(admin_importado)["speed-14k"]["price"] == "20 €"


def test_retirar_oculta_en_publico(admin_importado):
    actual = _privadas(admin_importado)["familiar-7k"]
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/familiar-7k",
        json={**actual, "published": False},
    )
    assert "familiar-7k" not in _publicas(admin_importado)
    assert "familiar-7k" in _privadas(admin_importado)


def test_version_obsoleta_409(admin_importado):
    actual = _privadas(admin_importado)["trail-27k"]
    assert (
        escribir(
            admin_importado, "PUT", "/api/admin/carreras/trail-27k", json={**actual, "km": 30}
        ).status_code
        == 200
    )
    r = escribir(admin_importado, "PUT", "/api/admin/carreras/trail-27k", json={**actual, "km": 31})
    assert r.status_code == 409
    assert _privadas(admin_importado)["trail-27k"]["km"] == "30"


def test_borrar(admin_importado, base_importada):
    actual = _privadas(admin_importado)["familiar-7k"]
    r = escribir(
        admin_importado,
        "DELETE",
        "/api/admin/carreras/familiar-7k",
        params={"version": actual["version"] + 5},
    )
    assert r.status_code == 409
    r = escribir(
        admin_importado,
        "DELETE",
        "/api/admin/carreras/familiar-7k",
        params={"version": actual["version"]},
    )
    assert r.status_code == 200
    assert (
        consultar(base_importada, "SELECT count(*) FROM carreras WHERE slug = 'familiar-7k'")[0][0]
        == 0
    )
    assert (
        escribir(
            admin_importado, "DELETE", "/api/admin/carreras/familiar-7k", params={"version": 1}
        ).status_code
        == 404
    )


@pytest.mark.parametrize(
    ("cambio", "campo"),
    [
        ({"title": ""}, "nombre"),
        ({"title": "x" * 151}, "nombre"),
        ({"km": "-1"}, "distancia"),
        ({"km": "abc"}, "distancia"),
        ({"km": "1.234"}, "distancia"),
        ({"elevation": "-5"}, "desnivel"),
        ({"elevation": "mil"}, "desnivel"),
        ({"edition": "1999"}, "edición"),
        ({"start": "25:00"}, "hora de salida"),
        ({"wikiloc": "abc"}, "ID de Wikiloc"),
        ({"image": ""}, "fotografía"),
        ({"image": "http://inseguro.example/x.jpg"}, "fotografía"),
        ({"route": "javascript:alert(1)"}, "enlace a la ruta"),
        ({"gpx": "/media/0123456789abcdef0123456789abcdef.jpg"}, "track GPX"),
        ({"registration": "https://u:p@pago.example"}, "enlace de inscripción"),
        ({"color": "rojo"}, "color"),
        ({"price": ""}, "precio"),
        ({"description": "x" * 5001}, "descripción"),
    ],
)
def test_validaciones(admin_importado, cambio, campo):
    r = escribir(
        admin_importado, "PUT", "/api/admin/carreras/nueva-prueba", json={**BASE, **cambio}
    )
    assert r.status_code == 400
    assert r.json() == {"error": f"Revisa el campo «{campo}»."}


def test_identificador_no_valido(admin_importado):
    assert escribir(
        admin_importado, "PUT", "/api/admin/carreras/no válido", json=BASE
    ).status_code in (400, 404)


def test_proteccion(base_importada):
    with crear_cliente(base_importada) as c:
        assert c.put("/api/admin/carreras/trail-27k", json=BASE).status_code == 401
