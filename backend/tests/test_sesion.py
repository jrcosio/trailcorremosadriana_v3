"""US2 · Sesión: estado, CSRF, contenido privado, caducidad, cierre, persistencia y huellas."""

from tests.conftest import consultar, crear_cliente, csrf, entrar

URL_SIN_BASE = "postgresql+psycopg://trail:clave@127.0.0.1:1/trail"


def test_sin_sesion():
    with crear_cliente(URL_SIN_BASE) as c:
        r = c.get("/api/session")
    assert r.status_code == 200
    assert r.json() == {"authenticated": False}


def test_con_sesion(cliente_admin):
    r = cliente_admin.get("/api/session")
    assert r.json() == {"authenticated": True, "usuario": "admin"}
    assert cliente_admin.cookies.get("penasagra_admin") not in r.text


def test_reemite_csrf_si_falta(cliente_admin):
    anterior = csrf(cliente_admin)
    cliente_admin.cookies.delete("penasagra_csrf")
    r = cliente_admin.get("/api/session")
    nuevo = cliente_admin.cookies.get("penasagra_csrf")
    assert r.json()["authenticated"] is True
    assert nuevo and nuevo != anterior
    # El nuevo comprobante es válido para escribir; el anterior ya no.
    assert cliente_admin.post("/api/logout", headers={"X-CSRF-Token": anterior}).status_code == 403
    assert cliente_admin.post("/api/logout", headers={"X-CSRF-Token": nuevo}).status_code == 200


def test_contenido_privado_incluye_borradores(cliente_admin):
    r = cliente_admin.get("/api/content", params={"admin": "1"})
    assert r.status_code == 200
    assert set(r.json()) == {"data", "revision"}
    assert r.json()["data"]["settings"]["edition"] == "2027"


def test_token_inventado_o_manipulado(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        entrar(c)
        token = c.cookies.get("penasagra_admin")
        for falso in ("inventado", token[:-1] + ("A" if token[-1] != "A" else "B"), "x" * 500):
            c.cookies.set("penasagra_admin", falso)
            assert c.get("/api/session").json() == {"authenticated": False}
            assert c.get("/api/content", params={"admin": "1"}).status_code == 401


def test_caducidad(cliente_admin, base_con_admin):
    consultar(base_con_admin, "UPDATE sesiones SET expira_en = now() - interval '1 second'")
    assert cliente_admin.get("/api/session").json() == {"authenticated": False}
    assert cliente_admin.get("/api/content", params={"admin": "1"}).status_code == 401


def test_duracion_de_8_horas(cliente_admin, base_con_admin):
    [(horas,)] = consultar(
        base_con_admin, "SELECT extract(epoch FROM expira_en - creada_en) / 3600 FROM sesiones"
    )
    assert abs(float(horas) - 8) < 0.01


def test_logout_revoca_y_borra_cookies(cliente_admin, base_con_admin):
    token = cliente_admin.cookies.get("penasagra_admin")
    r = cliente_admin.post("/api/logout", headers={"X-CSRF-Token": csrf(cliente_admin)})
    assert r.status_code == 200 and r.json() == {"ok": True}
    borradas = [h for h in r.headers.get_list("set-cookie") if "max-age=0" in h.lower()]
    assert len(borradas) == 2
    assert consultar(base_con_admin, "SELECT revocada_en IS NOT NULL FROM sesiones")[0][0] is True
    with crear_cliente(base_con_admin) as otro:
        otro.cookies.set("penasagra_admin", token)
        assert otro.get("/api/content", params={"admin": "1"}).status_code == 401


def test_logout_sin_sesion_es_inocuo(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        r = c.post("/api/logout")
    assert r.status_code == 200


def test_sesion_sobrevive_a_otra_instancia(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        entrar(c)
        token = c.cookies.get("penasagra_admin")
    with crear_cliente(base_con_admin) as reiniciada:  # equivale a reiniciar el servicio
        reiniciada.cookies.set("penasagra_admin", token)
        assert reiniciada.get("/api/session").json()["authenticated"] is True


def test_en_base_solo_hay_huellas(cliente_admin, base_con_admin):
    token = cliente_admin.cookies.get("penasagra_admin")
    comprobante = csrf(cliente_admin)
    filas = consultar(base_con_admin, "SELECT token_hash, csrf_hash FROM sesiones")
    volcado = str(filas)
    assert token not in volcado and comprobante not in volcado
    assert all(len(t) == 64 and len(c) == 64 for t, c in filas)


def test_dos_sesiones_independientes(base_con_admin):
    with crear_cliente(base_con_admin) as a, crear_cliente(base_con_admin) as b:
        entrar(a)
        entrar(b)
        a.post("/api/logout", headers={"X-CSRF-Token": csrf(a)})
        assert a.get("/api/session").json()["authenticated"] is False
        assert b.get("/api/session").json()["authenticated"] is True
