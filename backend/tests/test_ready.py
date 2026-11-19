"""US2 · Disponibilidad: base accesible y esquema en la última versión de Alembic."""

import time

from tests.conftest import crear_cliente


def test_disponible_con_esquema_aplicado(cliente):
    r = cliente.get("/api/ready")
    assert r.status_code == 200
    assert r.json() == {"estado": "disponible"}


def test_no_disponible_con_migraciones_pendientes(base_temporal):
    with crear_cliente(base_temporal) as c:
        r = c.get("/api/ready")
    assert r.status_code == 503
    assert r.json() == {"estado": "no_disponible", "motivo": "migraciones_pendientes"}


def test_no_disponible_con_base_inaccesible_sin_exponer_detalles():
    url = "postgresql+psycopg://trail:clave_secreta@127.0.0.1:1/trail"
    with crear_cliente(url) as c:
        r = c.get("/api/ready")
    assert r.status_code == 503
    assert r.json() == {"estado": "no_disponible", "motivo": "base_de_datos_inaccesible"}
    assert "clave_secreta" not in r.text
    assert "127.0.0.1" not in r.text


def test_base_que_no_responde_se_detecta_en_menos_de_5_segundos():
    # Dirección no enrutable: la conexión no se rechaza, expira por timeout (3 s por defecto).
    url = "postgresql+psycopg://trail:clave@10.255.255.1:5432/trail"
    with crear_cliente(url) as c:
        inicio = time.monotonic()
        r = c.get("/api/ready")
        duracion = time.monotonic() - inicio
    assert r.status_code == 503
    assert r.json()["motivo"] == "base_de_datos_inaccesible"
    assert duracion < 5, f"La disponibilidad tardó {duracion:.1f} s"
