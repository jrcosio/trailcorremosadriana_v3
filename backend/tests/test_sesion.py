"""US5 · Hasta la feature 002 no hay acceso al panel: nunca se concede ni se simula."""

from tests.conftest import crear_cliente

URL = "postgresql+psycopg://trail:clave@127.0.0.1:1/trail"


def test_sesion_siempre_sin_autenticar():
    with crear_cliente(URL) as c:
        r = c.get("/api/session")
    assert r.status_code == 200
    assert r.json() == {"authenticated": False}


def test_login_no_disponible_y_sin_cookie():
    with crear_cliente(URL) as c:
        r = c.post("/api/login", json={"username": "admin", "password": "cualquiera"})
    assert r.status_code == 503
    assert r.json() == {"error": "El acceso de administración todavía no está disponible."}
    assert "set-cookie" not in r.headers
