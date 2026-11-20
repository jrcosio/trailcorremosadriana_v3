"""Feature 010 · Reglamento por edición y configuración de contacto."""

import json

import pytest

from app.services.contenido import RUTA_SEMILLA
from tests.conftest import consultar, crear_cliente, escribir, importar_datos

SEMILLA = json.loads(RUTA_SEMILLA.read_text(encoding="utf-8"))
REGLAMENTO = "/api/admin/reglamento"
CONTACTO = "/api/admin/contacto"
NUEVO_CONTACTO = {
    "email": "organizacion@example.com",
    "phone": "+34 600 00 00 00",
    "instagram": "https://www.instagram.com/otra_cuenta/",
}


def _datos(c, privado=False):
    return c.get("/api/content", params={"admin": "1"} if privado else None).json()["data"]


def _version(c):
    return _datos(c, privado=True)["settings"]["eventVersion"]


def _reglamentos(base):
    return dict(consultar(base, "SELECT anio, reglamento FROM ediciones ORDER BY anio"))


# --- Historia 1: reglamento -------------------------------------------------------------------


def test_reglamento_de_referencia_en_2026_y_mostrado(base_importada):
    assert "PRUEBA" not in SEMILLA["regulation"]
    assert _reglamentos(base_importada) == {2026: SEMILLA["regulation"], 2027: ""}
    with crear_cliente(base_importada) as anonimo:
        assert _datos(anonimo)["regulation"] == SEMILLA["regulation"]


def test_guardar_en_la_edicion_actual_sin_tocar_2026(admin_importado, base_importada):
    texto = "Reglamento 2027\n\nINSCRIPCIONES\nTexto nuevo del apartado."
    r = escribir(
        admin_importado,
        "PUT",
        REGLAMENTO,
        json={"regulation": texto, "version": _version(admin_importado)},
    )
    assert r.status_code == 200 and r.json()["regulation"] == texto
    assert _reglamentos(base_importada) == {2026: SEMILLA["regulation"], 2027: texto}
    with crear_cliente(base_importada) as nuevo:  # persistencia: otra conexión, otro proceso
        assert _datos(nuevo)["regulation"] == texto
        assert _datos(nuevo)["regulation"] == _datos(admin_importado, privado=True)["regulation"]


def test_respaldo_a_la_edicion_mas_reciente_con_reglamento(admin_importado, base_importada):
    consultar(base_importada, "UPDATE ediciones SET reglamento = 'Texto 2027' WHERE anio = 2027")
    assert _datos(admin_importado)["regulation"] == "Texto 2027"
    cuerpo = {
        "edition": "2028",
        "date": "",
        "countdown": True,
        "version": _version(admin_importado),
    }
    assert escribir(admin_importado, "PUT", "/api/admin/evento", json=cuerpo).status_code == 200
    assert _datos(admin_importado)["regulation"] == "Texto 2027"  # 2028 aún no tiene
    assert _datos(admin_importado, privado=True)["regulation"] == "Texto 2027"


def test_sin_reglamento_en_ninguna_edicion_se_sirve_la_semilla(admin_importado, base_importada):
    # Respaldo coherente con «base sin inicializar»: /reglamento nunca queda vacío.
    consultar(base_importada, "UPDATE ediciones SET reglamento = ''")
    assert _datos(admin_importado)["regulation"] == SEMILLA["regulation"]
    assert _datos(admin_importado, privado=True)["regulation"] == SEMILLA["regulation"]


def test_texto_integro_hasta_200000_caracteres(admin_importado, base_importada):
    bloque = "ÁRTICULO ñ — «uno»\nLínea con  dos espacios\tinternos.\n\n"
    texto = (bloque * 4000)[:199_990].rstrip()
    texto += "Z" * (200_000 - len(texto))
    assert len(texto) == 200_000
    r = escribir(
        admin_importado,
        "PUT",
        REGLAMENTO,
        json={"regulation": texto, "version": _version(admin_importado)},
    )
    assert r.status_code == 200
    guardado = consultar(base_importada, "SELECT reglamento FROM ediciones WHERE anio = 2027")[0][0]
    assert guardado == texto and _datos(admin_importado)["regulation"] == texto
    r = escribir(
        admin_importado,
        "PUT",
        REGLAMENTO,
        json={"regulation": texto + "Z", "version": r.json()["version"]},
    )
    assert r.status_code == 400 and r.json() == {"error": "Revisa el campo «reglamento»."}


def test_normalizacion_y_vacio(admin_importado):
    v = _version(admin_importado)
    cuerpo = {"regulation": "  Título\r\nLínea\r\n\r\nOtro\rFin  \n", "version": v}
    r = escribir(admin_importado, "PUT", REGLAMENTO, json=cuerpo)
    assert r.status_code == 200 and r.json()["regulation"] == "Título\nLínea\n\nOtro\nFin"
    for vacio in ("", "  \r\n\t "):
        cuerpo = {"regulation": vacio, "version": v + 1}
        r = escribir(admin_importado, "PUT", REGLAMENTO, json=cuerpo)
        assert r.status_code == 400 and r.json() == {"error": "Revisa el campo «reglamento»."}
    assert _datos(admin_importado)["regulation"] == "Título\nLínea\n\nOtro\nFin"


def test_version_compartida_con_evento_e_inscripciones(admin_importado):
    v = _version(admin_importado)
    r = escribir(admin_importado, "PUT", REGLAMENTO, json={"regulation": "Uno", "version": v})
    assert r.json()["version"] == v + 1
    evento = {"edition": "2027", "date": "", "countdown": True, "version": v}
    assert escribir(admin_importado, "PUT", "/api/admin/evento", json=evento).status_code == 409
    ins = {"registrationsOpen": False, "registrationMessage": "Pronto.", "version": v + 1}
    assert escribir(admin_importado, "PUT", "/api/admin/inscripciones", json=ins).status_code == 200
    r = escribir(admin_importado, "PUT", REGLAMENTO, json={"regulation": "Dos", "version": v + 1})
    assert r.status_code == 409
    assert _datos(admin_importado)["regulation"] == "Uno"


def test_sin_edicion_actual_y_sin_sesion(admin_importado, base_importada):
    with crear_cliente(base_importada) as anonimo:
        r = anonimo.put(REGLAMENTO, json={"regulation": "x", "version": 0})
        assert r.status_code == 401
    consultar(base_importada, "UPDATE ediciones SET es_actual = false")
    r = escribir(admin_importado, "PUT", REGLAMENTO, json={"regulation": "x", "version": 0})
    assert r.status_code == 404
    assert r.json() == {"error": "No hay una edición actual configurada."}


# --- Historia 2: contacto ---------------------------------------------------------------------


def test_contacto_importado_y_version_privada(admin_importado, base_importada):
    ajustes = SEMILLA["settings"]
    with crear_cliente(base_importada) as anonimo:
        publico = _datos(anonimo)["settings"]
    privado = _datos(admin_importado, privado=True)["settings"]
    for clave in ("email", "phone", "instagram"):
        assert publico[clave] == privado[clave] == ajustes[clave]
    assert "contactVersion" not in publico and privado["contactVersion"] == 1


def test_contacto_edicion_conflicto_y_persistencia(admin_importado, base_importada):
    r = escribir(admin_importado, "PUT", CONTACTO, json={**NUEVO_CONTACTO, "version": 1})
    assert r.status_code == 200 and r.json() == {**NUEVO_CONTACTO, "version": 2}
    r = escribir(admin_importado, "PUT", CONTACTO, json={**NUEVO_CONTACTO, "version": 1})
    assert r.status_code == 409
    with crear_cliente(base_importada) as nuevo:
        ajustes = _datos(nuevo)["settings"]
    assert {k: ajustes[k] for k in NUEVO_CONTACTO} == NUEVO_CONTACTO


def test_contacto_alta_con_version_0_y_doble_envio(cliente_admin, base_con_admin):
    r = escribir(cliente_admin, "PUT", CONTACTO, json={**NUEVO_CONTACTO, "version": 0})
    assert r.status_code == 200 and r.json()["version"] == 1
    r = escribir(cliente_admin, "PUT", CONTACTO, json={**NUEVO_CONTACTO, "version": 0})
    assert r.status_code == 409
    assert consultar(base_con_admin, "SELECT count(*) FROM configuracion")[0][0] == 1


@pytest.mark.parametrize(
    ("cambio", "campo"),
    [
        ({"email": "sin-arroba"}, "correo de la organización"),
        ({"email": "a@b"}, "correo de la organización"),
        ({"email": ""}, "correo de la organización"),
        ({"phone": "600 ABC 123"}, "teléfono de contacto"),
        ({"phone": "12345"}, "teléfono de contacto"),
        ({"phone": "+34 60000000000000"}, "teléfono de contacto"),  # 16 dígitos
        ({"phone": "34+600000000"}, "teléfono de contacto"),
        ({"instagram": "http://www.instagram.com/x/"}, "Instagram"),
        ({"instagram": "https://example.com/x"}, "Instagram"),
        ({"instagram": "https://u:p@instagram.com/x"}, "Instagram"),
        ({"instagram": ""}, "Instagram"),
    ],
)
def test_contacto_validaciones(admin_importado, cambio, campo):
    cuerpo = {**NUEVO_CONTACTO, **cambio, "version": 1}
    r = escribir(admin_importado, "PUT", CONTACTO, json=cuerpo)
    assert r.status_code == 400 and r.json() == {"error": f"Revisa el campo «{campo}»."}
    assert _datos(admin_importado)["settings"]["email"] == SEMILLA["settings"]["email"]


def test_contacto_admite_formatos_habituales(admin_importado):
    version = 1
    for telefono in ("+34619364819", "942 00 00 00", "(942) 00-00-00"):
        cuerpo = {**NUEVO_CONTACTO, "phone": telefono, "version": version}
        r = escribir(admin_importado, "PUT", CONTACTO, json=cuerpo)
        assert r.status_code == 200, (telefono, r.text)
        version = r.json()["version"]
    instagram = "https://instagram.com/otra/"
    cuerpo = {**NUEVO_CONTACTO, "instagram": instagram, "version": version}
    assert escribir(admin_importado, "PUT", CONTACTO, json=cuerpo).status_code == 200


def test_contacto_sin_sesion(base_importada):
    with crear_cliente(base_importada) as anonimo:
        r = anonimo.put(CONTACTO, json={**NUEVO_CONTACTO, "version": 1})
        assert r.status_code == 401


def test_importacion_no_pisa_reglamento_ni_contacto(admin_importado, base_importada):
    v = _version(admin_importado)
    escribir(admin_importado, "PUT", REGLAMENTO, json={"regulation": "Propio", "version": v})
    escribir(admin_importado, "PUT", CONTACTO, json={**NUEVO_CONTACTO, "version": 1})
    consultar(base_importada, "UPDATE ediciones SET reglamento = '' WHERE anio = 2026")
    importar_datos(base_importada)
    assert _reglamentos(base_importada) == {2026: "", 2027: "Propio"}
    with crear_cliente(base_importada) as nuevo:
        datos = _datos(nuevo)
    assert datos["regulation"] == "Propio"
    assert datos["settings"]["email"] == NUEVO_CONTACTO["email"]
