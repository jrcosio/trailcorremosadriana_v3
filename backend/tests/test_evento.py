"""US1 · Edición actual, fecha y contador (FR-001–003, FR-007)."""

from tests.conftest import consultar, crear_cliente, escribir


def _guardar(c, **datos):
    return escribir(c, "PUT", "/api/admin/evento", json=datos)


def test_leer_requiere_sesion(base_importada):
    with crear_cliente(base_importada) as c:
        assert c.get("/api/admin/evento").status_code == 401


def test_leer(admin_importado):
    assert admin_importado.get("/api/admin/evento").json() == {
        "edition": "2027",
        "date": "",
        "countdown": True,
        "version": 1,
    }


def test_guardar_fecha_y_contador(admin_importado):
    r = _guardar(
        admin_importado, edition="2027", date="2027-07-10T07:00:00.000Z", countdown=False, version=1
    )
    assert r.status_code == 200, r.text
    assert r.json() == {
        "edition": "2027",
        "date": "2027-07-10T07:00:00.000Z",
        "countdown": False,
        "version": 2,
    }
    publico = admin_importado.get("/api/content").json()["data"]["settings"]
    assert (publico["edition"], publico["date"], publico["countdown"]) == (
        "2027",
        "2027-07-10T07:00:00.000Z",
        False,
    )


def test_hora_local_sin_zona_es_peninsular(admin_importado):
    r = _guardar(
        admin_importado, edition="2027", date="2027-01-15T09:00", countdown=True, version=1
    )
    assert r.json()["date"] == "2027-01-15T08:00:00.000Z"


def test_vaciar_fecha(admin_importado):
    _guardar(
        admin_importado, edition="2027", date="2027-07-10T07:00:00.000Z", countdown=True, version=1
    )
    r = _guardar(admin_importado, edition="2027", date="", countdown=True, version=2)
    assert r.json()["date"] == ""


def test_cambiar_de_anio_conserva_la_anterior(admin_importado, base_importada):
    r = _guardar(admin_importado, edition="2028", date="", countdown=True, version=1)
    assert r.status_code == 200 and r.json()["edition"] == "2028"
    filas = consultar(base_importada, "SELECT anio, es_actual FROM ediciones ORDER BY anio")
    assert filas == [(2026, False), (2027, False), (2028, True)]
    # Volver a 2027: reutiliza la edición existente.
    r = _guardar(
        admin_importado, edition="2027", date="", countdown=True, version=r.json()["version"]
    )
    assert r.status_code == 200
    assert consultar(base_importada, "SELECT count(*) FROM ediciones WHERE es_actual")[0][0] == 1


def test_version_obsoleta_409_sin_cambios(admin_importado, base_importada):
    assert (
        _guardar(admin_importado, edition="2027", date="", countdown=False, version=1).status_code
        == 200
    )
    r = _guardar(
        admin_importado, edition="2027", date="2027-07-10T07:00:00.000Z", countdown=True, version=1
    )
    assert r.status_code == 409
    assert r.json()["error"].startswith("Otra persona ha modificado")
    assert consultar(
        base_importada, "SELECT fecha_hora, mostrar_contador FROM ediciones WHERE es_actual"
    ) == [(None, False)]


def test_datos_no_validos(admin_importado):
    for datos, campo in [
        ({"edition": "1999", "date": "", "countdown": True, "version": 1}, "edición"),
        ({"edition": "2027", "date": "mañana", "countdown": True, "version": 1}, "fecha y hora"),
    ]:
        r = _guardar(admin_importado, **datos)
        assert r.status_code == 400
        assert r.json() == {"error": f"Revisa el campo «{campo}»."}


def test_proteccion(base_importada):
    with crear_cliente(base_importada) as c:
        r = c.put(
            "/api/admin/evento",
            json={"edition": "2027", "date": "", "countdown": True, "version": 1},
        )
    assert r.status_code == 401
