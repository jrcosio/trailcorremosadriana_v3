"""US5 · Revocación: desactivar, activar, revocar sesiones y restablecer contraseña."""

import io

from app import cli
from tests.conftest import PASSWORD, crear_cliente, entrar


def _cli(url, *args, entrada=""):
    return cli.main(
        list(args), database_url=url, entrada=io.StringIO(entrada), salida=io.StringIO()
    )


def _privado(c):
    return c.get("/api/content", params={"admin": "1"}).status_code


def test_desactivar_y_activar(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        entrar(c)
        assert _privado(c) == 200
        assert _cli(base_con_admin, "desactivar", "admin") == 0
        assert _privado(c) == 401
        assert entrar(c).status_code == 401
        assert _cli(base_con_admin, "activar", "admin") == 0
        assert entrar(c).status_code == 200


def test_revocar_sesiones_permite_volver_a_entrar(base_con_admin):
    with crear_cliente(base_con_admin) as c:
        entrar(c)
        assert _cli(base_con_admin, "revocar-sesiones", "admin") == 0
        assert _privado(c) == 401
        assert entrar(c).status_code == 200
        assert _privado(c) == 200


def test_restablecer_invalida_sesion_y_password_anterior(base_con_admin):
    nueva = "nueva-clave-de-prueba-1"
    with crear_cliente(base_con_admin) as c:
        entrar(c)
        assert (
            _cli(
                base_con_admin,
                "restablecer-password",
                "admin",
                "--password-stdin",
                entrada=nueva + "\n",
            )
            == 0
        )
        assert _privado(c) == 401
        assert entrar(c, password=PASSWORD).status_code == 401
        assert entrar(c, password=nueva).status_code == 200
