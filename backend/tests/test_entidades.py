"""Feature 009 · Patrocinadores y colaboradores: mismo modelo, secciones independientes."""

import pytest

from tests.conftest import consultar, crear_cliente, escribir, importar_datos

LOGO = "/reused/logos/patrocinadores/banner_andros.png"
NUEVA = {
    "name": "Colaborador de prueba",
    "image": LOGO,
    "url": "https://example.com",
    "order": 1,
    "published": False,
}


def _publico(c, clave):
    return c.get("/api/content").json()["data"][clave]


def test_patrocinadores_importados(admin_importado):
    sp = _publico(admin_importado, "sponsors")
    assert [p["name"] for p in sp] == [
        "Carandía",
        "JV Cosío",
        "Andros",
        "Aljomar",
        "Artipublic",
        "Grupo Choví",
        "Natuber",
        "Ayuntamiento de Rionansa",
    ]
    assert all(p["url"] == "" for p in sp)
    assert _publico(admin_importado, "collaborators") == []


def test_colaborador_ciclo_completo_e_independencia(admin_importado, base_importada):
    antes = consultar(
        base_importada, "SELECT * FROM entidades WHERE tipo = 'patrocinador' ORDER BY id"
    )
    # Mismo id que un patrocinador: es una entidad distinta.
    url = "/api/admin/entidades/colaboradores/andros"
    r = escribir(admin_importado, "PUT", url, json=NUEVA)
    assert r.status_code == 200 and r.json()["version"] == 1
    assert _publico(admin_importado, "collaborators") == []
    escribir(admin_importado, "PUT", url, json={**NUEVA, "published": True, "version": 1})
    assert [c["id"] for c in _publico(admin_importado, "collaborators")] == ["andros"]
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/entidades/colaboradores/otro",
        json={**NUEVA, "order": 0, "published": True},
    )
    assert [c["id"] for c in _publico(admin_importado, "collaborators")] == ["otro", "andros"]
    escribir(admin_importado, "PUT", url, json={**NUEVA, "published": False, "version": 2})
    assert [c["id"] for c in _publico(admin_importado, "collaborators")] == ["otro"]
    assert escribir(admin_importado, "DELETE", url, params={"version": 1}).status_code == 409
    assert escribir(admin_importado, "DELETE", url, params={"version": 3}).status_code == 200
    assert (
        consultar(base_importada, "SELECT * FROM entidades WHERE tipo = 'patrocinador' ORDER BY id")
        == antes
    )


def test_doble_envio_conflicto_y_seccion_invalida(admin_importado, base_importada):
    url = "/api/admin/entidades/patrocinadores/nuevo"
    assert escribir(admin_importado, "PUT", url, json=NUEVA).status_code == 200
    assert escribir(admin_importado, "PUT", url, json=NUEVA).status_code == 409
    assert (
        consultar(base_importada, "SELECT count(*) FROM entidades WHERE slug = 'nuevo'")[0][0] == 1
    )
    assert escribir(
        admin_importado, "PUT", "/api/admin/entidades/otros/x", json=NUEVA
    ).status_code in (400, 404, 422)


@pytest.mark.parametrize(
    ("cambio", "campo"),
    [
        ({"name": ""}, "nombre de la entidad"),
        ({"image": ""}, "logotipo"),
        ({"url": "http://example.com"}, "web de la entidad"),
        ({"url": "https://usuario:clave@example.com"}, "web de la entidad"),
        ({"order": "-1"}, "orden de aparición"),
    ],
)
def test_validaciones(admin_importado, cambio, campo):
    r = escribir(
        admin_importado, "PUT", "/api/admin/entidades/colaboradores/malo", json={**NUEVA, **cambio}
    )
    assert r.status_code == 400 and r.json() == {"error": f"Revisa el campo «{campo}»."}


def test_proteccion_persistencia_e_importacion(admin_importado, base_importada):
    with crear_cliente(base_importada) as anonimo:
        assert anonimo.put("/api/admin/entidades/colaboradores/x", json=NUEVA).status_code == 401
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/entidades/colaboradores/persiste",
        json={**NUEVA, "published": True},
    )
    consultar(base_importada, "UPDATE entidades SET nombre = 'Editado' WHERE slug = 'carandia'")
    importar_datos(base_importada)
    with crear_cliente(base_importada) as reiniciada:
        datos = reiniciada.get("/api/content").json()["data"]
    assert datos["sponsors"][0]["name"] == "Editado"
    assert [c["id"] for c in datos["collaborators"]] == ["persiste"]
