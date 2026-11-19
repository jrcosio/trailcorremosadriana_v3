"""US1 · Apertura de inscripciones y Dorsal Solidario (feature 005)."""

import pytest

from tests.conftest import consultar, crear_cliente, escribir

DORSAL = "https://example.com/dorsal-solidario-prueba"
MENSAJE = (
    "Estamos preparando la próxima edición. "
    "Pronto anunciaremos la fecha y la apertura de inscripciones."
)


def _estado(c):
    return c.get("/api/admin/inscripciones").json()


def _guardar(c, **cambios):
    datos = {**_estado(c), **cambios}
    return escribir(c, "PUT", "/api/admin/inscripciones", json=datos)


def _publico(c):
    return c.get("/api/content").json()["data"]


def _carrera(c, slug):
    return {
        r["id"]: r for r in c.get("/api/content", params={"admin": "1"}).json()["data"]["races"]
    }[slug]


def test_estado_importado(admin_importado):
    assert _estado(admin_importado) == {
        "registrationsOpen": False,
        "registrationMessage": MENSAJE,
        "solidarityRegistration": "",
        "version": 1,
    }


def test_abrir_sin_destinos_400(admin_importado, base_importada):
    r = _guardar(admin_importado, registrationsOpen=True)
    assert r.status_code == 400
    assert r.json()["error"].startswith("No puedes abrir las inscripciones")
    assert (
        consultar(base_importada, "SELECT inscripciones_abiertas FROM ediciones WHERE es_actual")[
            0
        ][0]
        is False
    )


def test_abrir_solo_con_el_dorsal(admin_importado):
    r = _guardar(admin_importado, registrationsOpen=True, solidarityRegistration=DORSAL)
    assert r.status_code == 200 and r.json()["registrationsOpen"] is True
    s = _publico(admin_importado)["settings"]
    assert (s["registrationsOpen"], s["solidarityRegistration"]) == (True, DORSAL)


def test_abrir_con_una_prueba_publicada_con_enlace(admin_importado):
    trail = _carrera(admin_importado, "trail-27k")
    enlace = "https://example.com/inscripcion-trail-prueba"
    assert (
        escribir(
            admin_importado,
            "PUT",
            "/api/admin/carreras/trail-27k",
            json={**trail, "registration": enlace},
        ).status_code
        == 200
    )
    assert _guardar(admin_importado, registrationsOpen=True).status_code == 200
    publica = {r["id"]: r for r in _publico(admin_importado)["races"]}["trail-27k"]
    assert publica["registration"] == enlace


def test_prueba_retirada_no_cuenta(admin_importado):
    trail = _carrera(admin_importado, "trail-27k")
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/trail-27k",
        json={**trail, "registration": "https://example.com/insc", "published": False},
    )
    assert _guardar(admin_importado, registrationsOpen=True).status_code == 400


def test_cerrar_conserva_los_enlaces(admin_importado):
    _guardar(admin_importado, registrationsOpen=True, solidarityRegistration=DORSAL)
    r = _guardar(admin_importado, registrationsOpen=False)
    assert r.status_code == 200
    assert _estado(admin_importado)["solidarityRegistration"] == DORSAL
    assert _publico(admin_importado)["settings"]["registrationsOpen"] is False


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/pago",
        "javascript:alert(1)",
        "https://u:p@example.com/x",
        "https://",
        "ftp://x.example",
    ],
)
def test_destinos_peligrosos_400(admin_importado, url):
    r = _guardar(admin_importado, solidarityRegistration=url)
    assert r.status_code == 400
    assert r.json() == {"error": "Revisa el campo «enlace de pago del dorsal solidario»."}
    trail = _carrera(admin_importado, "trail-27k")
    r = escribir(
        admin_importado, "PUT", "/api/admin/carreras/trail-27k", json={**trail, "registration": url}
    )
    assert r.status_code == 400 and r.json() == {
        "error": "Revisa el campo «enlace de inscripción»."
    }


@pytest.mark.parametrize("mensaje", ["", "x" * 2001])
def test_mensaje_no_valido(admin_importado, mensaje):
    r = _guardar(admin_importado, registrationMessage=mensaje)
    assert r.status_code == 400 and r.json() == {
        "error": "Revisa el campo «mensaje al participante»."
    }


def test_version_compartida_con_el_evento_409(admin_importado):
    estado = _estado(admin_importado)
    ev = admin_importado.get("/api/admin/evento").json()
    assert (
        escribir(
            admin_importado, "PUT", "/api/admin/evento", json={**ev, "countdown": False}
        ).status_code
        == 200
    )
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/inscripciones",
        json={**estado, "registrationMessage": "Otro"},
    )
    assert r.status_code == 409


def test_proteccion_y_persistencia(admin_importado, base_importada):
    with crear_cliente(base_importada) as anonimo:
        assert anonimo.get("/api/admin/inscripciones").status_code == 401
        assert (
            anonimo.put("/api/admin/inscripciones", json=_estado(admin_importado)).status_code
            == 401
        )
    _guardar(admin_importado, solidarityRegistration=DORSAL)
    with crear_cliente(base_importada) as reiniciada:
        assert (
            reiniciada.get("/api/content").json()["data"]["settings"]["solidarityRegistration"]
            == DORSAL
        )


def test_edicion_nueva_empieza_cerrada(admin_importado):
    _guardar(admin_importado, registrationsOpen=True, solidarityRegistration=DORSAL)
    ev = admin_importado.get("/api/admin/evento").json()
    escribir(admin_importado, "PUT", "/api/admin/evento", json={**ev, "edition": "2028"})
    s = _publico(admin_importado)["settings"]
    assert (s["registrationsOpen"], s["solidarityRegistration"], s["edition"]) == (
        False,
        "",
        "2028",
    )


def test_importar_completa_una_base_anterior_sin_pisar(base_importada):
    from tests.conftest import importar_datos

    consultar(
        base_importada, "UPDATE ediciones SET mensaje_inscripciones = 'Editado' WHERE es_actual"
    )
    importar_datos(base_importada)
    assert (
        consultar(base_importada, "SELECT mensaje_inscripciones FROM ediciones WHERE es_actual")[0][
            0
        ]
        == "Editado"
    )
    consultar(base_importada, "UPDATE ediciones SET mensaje_inscripciones = '' WHERE es_actual")
    importar_datos(base_importada)
    assert (
        consultar(base_importada, "SELECT mensaje_inscripciones FROM ediciones WHERE es_actual")[0][
            0
        ]
        == MENSAJE
    )


def test_url_con_espacios_alrededor_se_recorta(admin_importado):
    r = _guardar(admin_importado, solidarityRegistration=f"  {DORSAL}  ")
    assert r.status_code == 200 and r.json()["solidarityRegistration"] == DORSAL
    trail = _carrera(admin_importado, "trail-27k")
    enlace = "https://example.com/inscripcion"
    r = escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/trail-27k",
        json={**trail, "registration": f" {enlace} "},
    )
    assert r.status_code == 200 and r.json()["registration"] == enlace
