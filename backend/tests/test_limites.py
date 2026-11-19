"""US4 · Límite persistente de 8 accesos fallidos por IP en 15 minutos."""

from tests.conftest import PASSWORD, consultar, crear_cliente, entrar


def _fallar(c, veces):
    for _ in range(veces):
        assert entrar(c, password="contraseña-equivocada").status_code == 401


def test_noveno_intento_bloqueado_aunque_sea_correcto(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        _fallar(c, 8)
        r = entrar(c, password=PASSWORD)
    assert r.status_code == 429
    assert r.json() == {
        "error": "Demasiados intentos. Espera unos minutos antes de volver a intentarlo."
    }
    assert 0 < int(r.headers["retry-after"]) <= 15 * 60 + 1
    assert "set-cookie" not in r.headers


def test_acierto_antes_del_umbral_reinicia(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        _fallar(c, 7)
        assert entrar(c).status_code == 200
        _fallar(c, 7)
        assert entrar(c).status_code == 200


def test_ventana_expirada_permite_entrar(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        _fallar(c, 8)
        assert entrar(c).status_code == 429
        consultar(
            base_con_admin,
            "UPDATE limites_login SET inicio = now() - interval '15 minutes 1 second'",
        )
        assert entrar(c).status_code == 200


def test_bloqueo_persiste_tras_reinicio(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        _fallar(c, 8)
    with crear_cliente(base_con_admin) as reiniciada:
        assert entrar(reiniciada).status_code == 429


def test_usuarios_distintos_suman_e_ips_distintas_son_independientes(base_con_admin):
    with crear_cliente(base_con_admin, ip="198.51.100.1") as c:
        for i in range(8):
            assert entrar(c, usuario=f"usuario{i}", password="x" * 20).status_code == 401
        assert entrar(c).status_code == 429
    with crear_cliente(base_con_admin, ip="198.51.100.2") as otra:
        assert entrar(otra).status_code == 200


def test_la_clave_es_una_huella(base_con_admin):
    with crear_cliente(base_con_admin, ip="198.51.100.77") as c:
        _fallar(c, 1)
    [(clave, intentos)] = consultar(base_con_admin, "SELECT clave, intentos FROM limites_login")
    assert len(clave) == 64 and "198.51.100.77" not in clave
    assert intentos == 1
