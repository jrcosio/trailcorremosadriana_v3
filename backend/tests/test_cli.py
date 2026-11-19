"""US1 · Comando de operador: alta y gestión segura de administradores."""

import io
import os
import subprocess
import sys

import pytest

from app import cli
from tests.conftest import PASSWORD, consultar, crear_cliente, entrar


def ejecutar(url: str, *args: str, entrada: str = "") -> tuple[int, str]:
    salida = io.StringIO()
    codigo = cli.main(list(args), database_url=url, entrada=io.StringIO(entrada), salida=salida)
    return codigo, salida.getvalue()


def test_alta_correcta_con_argon2id(base_migrada):
    codigo, texto = ejecutar(
        base_migrada, "crear-admin", "Admin", "--password-stdin", entrada=PASSWORD + "\n"
    )
    assert codigo == 0, texto
    assert "admin" in texto and PASSWORD not in texto
    [(usuario, hash_, activo)] = consultar(
        base_migrada, "SELECT usuario, hash_password, activo FROM administradores"
    )
    assert usuario == "admin"  # normalizado
    assert hash_.startswith("$argon2id$")
    assert PASSWORD not in hash_
    assert activo is True


def test_alta_duplicada_no_modifica(base_migrada):
    ejecutar(base_migrada, "crear-admin", "admin", "--password-stdin", entrada=PASSWORD + "\n")
    [(hash_antes,)] = consultar(base_migrada, "SELECT hash_password FROM administradores")
    codigo, texto = ejecutar(
        base_migrada,
        "crear-admin",
        " ADMIN ",
        "--password-stdin",
        entrada="otra-clave-distinta-1\n",
    )
    assert codigo == 1
    assert "restablecer-password" in texto
    [(hash_despues,)] = consultar(base_migrada, "SELECT hash_password FROM administradores")
    assert hash_antes == hash_despues


@pytest.mark.parametrize(
    ("usuario", "password"),
    [
        ("admin", "corta"),
        ("admin", "x" * 129),
        ("organizacion", "Organizacion"),  # igual al usuario
        ("ab", PASSWORD),  # usuario demasiado corto
        (".admin", PASSWORD),  # empieza por punto
        ("ad min", PASSWORD),  # espacio interior
    ],
)
def test_politica_rechaza(base_migrada, usuario, password):
    codigo, _ = ejecutar(
        base_migrada, "crear-admin", usuario, "--password-stdin", entrada=password + "\n"
    )
    assert codigo == 2
    assert consultar(base_migrada, "SELECT count(*) FROM administradores")[0][0] == 0


def test_password_nunca_como_argumento(base_migrada):
    with pytest.raises(SystemExit):
        cli.main(["crear-admin", "admin", "--password", PASSWORD], database_url=base_migrada)


def test_confirmacion_interactiva_que_no_coincide(base_migrada, monkeypatch):
    respuestas = iter([PASSWORD, PASSWORD + "x"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda _: next(respuestas))
    codigo, texto = ejecutar(base_migrada, "crear-admin", "admin")
    assert codigo == 2
    assert "no coinciden" in texto


def test_restablecer_revoca_sesiones_y_cambia_password(base_migrada):
    ejecutar(base_migrada, "crear-admin", "admin", "--password-stdin", entrada=PASSWORD + "\n")
    with crear_cliente(base_migrada) as c:
        assert entrar(c).status_code == 200
        nueva = "otra-clave-segura-2026"
        codigo, _ = ejecutar(
            base_migrada, "restablecer-password", "admin", "--password-stdin", entrada=nueva + "\n"
        )
        assert codigo == 0
        assert c.get("/api/content", params={"admin": "1"}).status_code == 401
    with crear_cliente(base_migrada) as c:
        assert entrar(c).status_code == 401
        assert entrar(c, password=nueva).status_code == 200


def test_desactivar_activar_y_revocar(base_migrada):
    ejecutar(base_migrada, "crear-admin", "admin", "--password-stdin", entrada=PASSWORD + "\n")
    assert ejecutar(base_migrada, "desactivar", "admin")[0] == 0
    assert consultar(base_migrada, "SELECT activo FROM administradores")[0][0] is False
    assert ejecutar(base_migrada, "activar", "admin")[0] == 0
    codigo, texto = ejecutar(base_migrada, "revocar-sesiones", "admin")
    assert codigo == 0 and "0 sesiones revocadas" in texto
    assert ejecutar(base_migrada, "desactivar", "noexiste")[0] == 1


def test_listar_sin_hashes(base_migrada):
    ejecutar(base_migrada, "crear-admin", "admin", "--password-stdin", entrada=PASSWORD + "\n")
    codigo, texto = ejecutar(base_migrada, "listar-admins")
    assert codigo == 0
    assert "admin" in texto and "argon2" not in texto


def test_ejecutable_como_modulo(base_migrada):
    """`python -m app.cli` con la contraseña por stdin, como se usa en Docker."""
    entorno = {**os.environ, "DATABASE_URL": base_migrada}
    r = subprocess.run(
        [sys.executable, "-m", "app.cli", "crear-admin", "operador", "--password-stdin"],
        input=PASSWORD + "\n",
        capture_output=True,
        text=True,
        env=entorno,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert PASSWORD not in r.stdout + r.stderr
    assert consultar(base_migrada, "SELECT usuario FROM administradores")[0][0] == "operador"
