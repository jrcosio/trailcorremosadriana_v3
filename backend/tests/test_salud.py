"""US2 · Comprobación de salud: responde mientras el proceso esté vivo, sin depender de la BD."""

from tests.conftest import crear_cliente

URL_INACCESIBLE = "postgresql+psycopg://trail:clave@127.0.0.1:1/trail"


def test_salud_responde_viva_aunque_la_base_no_exista():
    with crear_cliente(URL_INACCESIBLE) as c:
        r = c.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"estado": "viva"}


def test_salud_lleva_cabeceras_seguras():
    with crear_cliente(URL_INACCESIBLE) as c:
        r = c.get("/api/health")
    assert r.headers["cache-control"] == "no-store"
    assert r.headers["x-content-type-options"] == "nosniff"
