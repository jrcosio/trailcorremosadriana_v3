"""Feature 012 · US2: dominio con «ñ». El origen se compara siempre en *punycode*."""

import pytest

from app.core.config import Settings, normalizar_origen
from tests.conftest import PASSWORD, crear_cliente

PUNYCODE = "https://xn--trailpeasagra-okb.com"


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("https://trailpeñasagra.com", PUNYCODE),
        ("https://TrailPeñasagra.com/", PUNYCODE),
        (PUNYCODE, PUNYCODE),
        ("https://trailpeñasagra.com:8443/ruta", "https://xn--trailpeasagra-okb.com:8443"),
        ("http://localhost:8080", "http://localhost:8080"),
        ("ftp://trailpeñasagra.com", ""),
        ("no es una url", ""),
        ("https://", ""),
    ],
)
def test_normalizar_origen(valor, esperado):
    assert normalizar_origen(valor) == esperado


def test_origenes_validos_y_publico_con_ene():
    ajustes = Settings(public_origin="https://trailpeñasagra.com")
    assert PUNYCODE in ajustes.origenes_validos
    assert ajustes.origen_publico == PUNYCODE


def test_acceso_con_dominio_con_ene(base_con_admin):
    # Configuración escrita con «ñ»; el navegador envía el origen en punycode.
    with crear_cliente(base_con_admin, public_origin="https://trailpeñasagra.com") as c:
        c.headers["Origin"] = PUNYCODE
        r = c.post("/api/login", json={"username": "admin", "password": PASSWORD})
        assert r.status_code == 200, r.text
        c.headers["Origin"] = "https://otro.example"
        assert c.post("/api/logout").status_code == 403
