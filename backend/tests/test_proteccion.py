"""US3 · Protección de escrituras: origen → sesión → CSRF (sobre recursos reales desde la 010)."""

import pytest

from tests.conftest import ORIGEN, PASSWORD, crear_cliente, csrf, entrar

ESCRITURAS = [("PUT", "/api/admin/contacto"), ("POST", "/api/upload")]
ORIGEN_AJENO = "https://atacante.example"


def _peticion(c, metodo, ruta, origen=ORIGEN, token=None):
    cabeceras = {"Origin": origen} if origen else {}
    if token is not None:
        cabeceras["X-CSRF-Token"] = token
    # El cliente añade Origin por defecto: se sustituye o elimina explícitamente.
    c.headers.pop("Origin", None)
    respuesta = c.request(metodo, ruta, headers=cabeceras)
    c.headers["Origin"] = ORIGEN
    return respuesta


@pytest.mark.parametrize(("metodo", "ruta"), ESCRITURAS)
def test_sin_sesion_401(base_con_admin, metodo, ruta):
    with crear_cliente(base_con_admin) as c:
        assert _peticion(c, metodo, ruta).status_code == 401


@pytest.mark.parametrize(
    ("metodo", "ruta"), [*ESCRITURAS, ("POST", "/api/logout"), ("POST", "/api/login")]
)
@pytest.mark.parametrize(
    "origen", [None, ORIGEN_AJENO, "null", "http://localhost:8080.atacante.example"]
)
def test_origen_ausente_o_ajeno_403(cliente_admin, metodo, ruta, origen):
    r = _peticion(cliente_admin, metodo, ruta, origen=origen, token=csrf(cliente_admin))
    assert r.status_code == 403
    assert r.json() == {"error": "Origen no permitido."}


def test_origen_se_comprueba_antes_que_la_sesion(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        r = _peticion(c, "PUT", "/api/admin/contacto", origen=ORIGEN_AJENO)
        assert r.status_code == 403


@pytest.mark.parametrize(("metodo", "ruta"), ESCRITURAS)
def test_sin_csrf_o_csrf_ajeno_403(base_con_admin, metodo, ruta):
    with crear_cliente(base_con_admin) as a, crear_cliente(base_con_admin) as b:
        entrar(a)
        entrar(b)
        for token in (None, "", "inventado", csrf(b)):
            r = _peticion(a, metodo, ruta, token=token)
            assert r.status_code == 403, token
            assert r.json()["error"].startswith("Comprobación de seguridad no válida")


def test_escritura_con_proteccion_valida_llega_al_recurso(cliente_admin):
    cuerpo = {
        "email": "organizacion@example.com",
        "phone": "+34 600 00 00 00",
        "instagram": "https://www.instagram.com/cuenta/",
        "version": 0,
    }
    cabeceras = {"X-CSRF-Token": csrf(cliente_admin)}
    r = cliente_admin.put("/api/admin/contacto", json=cuerpo, headers=cabeceras)
    assert r.status_code == 200


def test_guardado_del_documento_completo_retirado(cliente_admin):
    # DISCREPANCIAS M1 (feature 010): el panel guarda por recursos; PUT /api/content no existe.
    r = _peticion(cliente_admin, "PUT", "/api/content", token=csrf(cliente_admin))
    assert r.status_code == 405 and set(r.json()) == {"error"}


def test_subida_con_proteccion_valida_llega_a_validar_el_archivo(cliente_admin):
    # Desde la feature 003 la subida es real: sin archivo responde 400 (no 501).
    r = _peticion(cliente_admin, "POST", "/api/upload", token=csrf(cliente_admin))
    assert r.status_code == 400


def test_logout_con_sesion_exige_csrf(cliente_admin):
    assert _peticion(cliente_admin, "POST", "/api/logout").status_code == 403
    assert cliente_admin.get("/api/session").json()["authenticated"] is True


def test_origen_de_desarrollo_solo_si_se_configura(base_con_admin):
    vite = "http://localhost:5173"
    with crear_cliente(base_con_admin) as c:
        c.headers["Origin"] = vite
        assert entrar(c).status_code == 403
    with crear_cliente(base_con_admin, origenes_permitidos=vite) as c:
        c.headers["Origin"] = vite
        assert entrar(c).status_code == 200


def test_lectura_privada_sin_sesion_401(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        assert c.get("/api/content", params={"admin": "1"}).status_code == 401


def test_errores_sin_secretos_ni_detalles_internos(cliente_admin):
    token = cliente_admin.cookies.get("penasagra_admin")
    comprobante = csrf(cliente_admin)
    respuestas = [
        _peticion(cliente_admin, "PUT", "/api/admin/contacto"),
        _peticion(cliente_admin, "PUT", "/api/admin/contacto", origen=ORIGEN_AJENO),
        _peticion(cliente_admin, "PUT", "/api/admin/contacto", token=csrf(cliente_admin)),
        cliente_admin.post("/api/login", json={"username": "admin", "password": "mal"}),
        cliente_admin.post("/api/login", content=b"{no json"),
    ]
    for r in respuestas:
        texto = r.text
        assert set(r.json()) == {"error"}
        for secreto in (token, comprobante, PASSWORD, "Traceback", "sqlalchemy", "psycopg"):
            assert secreto not in texto
