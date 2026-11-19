"""US2 · Acceso al panel: cookies, mensajes genéricos, errores de servicio."""

import statistics
import time

from tests.conftest import PASSWORD, consultar, crear_admin, crear_cliente, entrar

GENERICO = {"error": "Usuario o contraseña incorrectos."}


def test_acceso_correcto_emite_cookies_seguras(base_con_admin):
    with crear_cliente(base_con_admin, cookie_secure=True) as c:
        r = entrar(c)
    assert r.status_code == 200
    assert r.json() == {"ok": True, "usuario": "admin"}
    cookies = {h.split("=", 1)[0]: h for h in r.headers.get_list("set-cookie")}
    sesion, csrf = cookies["penasagra_admin"], cookies["penasagra_csrf"]
    for atributo in ("Max-Age=28800", "Path=/", "SameSite=strict", "Secure"):
        assert atributo.lower() in sesion.lower() and atributo.lower() in csrf.lower()
    assert "httponly" in sesion.lower()
    assert "httponly" not in csrf.lower()  # el panel debe poder leerla


def test_cookie_sin_secure_solo_si_se_configura(base_con_admin):
    with crear_cliente(base_con_admin, cookie_secure=False) as c:
        r = entrar(c)
    assert all("secure" not in h.lower() for h in r.headers.get_list("set-cookie"))


def test_normaliza_usuario_y_registra_ultimo_acceso(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        assert entrar(c, usuario="  ADMIN ").status_code == 200
    assert (
        consultar(base_con_admin, "SELECT ultimo_acceso_en FROM administradores")[0][0] is not None
    )


def test_mensaje_identico_en_todos_los_fallos(base_con_admin):
    consultar(
        base_con_admin,
        "INSERT INTO administradores (usuario, hash_password, activo) "
        "VALUES ('inactivo', 'x', false)",
    )
    with crear_cliente(base_con_admin) as c:
        casos = [
            entrar(c, usuario="noexiste"),
            entrar(c, password="contraseña-equivocada"),
            entrar(c, usuario="inactivo", password=PASSWORD),
            entrar(c, password=""),
            entrar(c, password="x" * 300),
        ]
    for r in casos:
        assert r.status_code == 401
        assert r.json() == GENERICO
        assert "set-cookie" not in r.headers


def test_tiempo_comparable_usuario_inexistente(base_con_admin):
    def mediana(usuario):
        tiempos = []
        with crear_cliente(base_con_admin, login_max_intentos=100) as c:
            for _ in range(5):
                t0 = time.perf_counter()
                entrar(c, usuario=usuario, password="contraseña-equivocada")
                tiempos.append(time.perf_counter() - t0)
        return statistics.median(tiempos)

    ratio = mediana("noexiste") / mediana("admin")
    assert 0.5 < ratio < 2, f"ratio de tiempos {ratio:.2f}"


def test_cuerpo_mal_formado(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        r = c.post("/api/login", json={"username": "admin"})
    assert r.status_code == 400
    assert r.json() == {"error": "Datos no válidos."}


def test_base_caida_da_error_de_servicio_sin_acceso():
    with crear_cliente("postgresql+psycopg://trail:clave@127.0.0.1:1/trail") as c:
        r = entrar(c)
    assert r.status_code == 503
    assert r.json() == {"error": "El servicio no está disponible. Inténtalo más tarde."}
    assert "set-cookie" not in r.headers


def test_crear_admin_helper_funciona(base_migrada):
    crear_admin(base_migrada, "segundo")
    assert consultar(base_migrada, "SELECT usuario FROM administradores")[0][0] == "segundo"
