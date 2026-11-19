"""US3 · Contenido público transitorio (`GET /api/content`)."""

import json

import pytest
from pydantic import ValidationError

from app.schemas.contenido import SiteData
from app.services.contenido import RUTA_SEMILLA, datos_publicos
from tests.conftest import crear_cliente

URL = "postgresql+psycopg://trail:clave@127.0.0.1:1/trail"


@pytest.fixture
def contenido():
    with crear_cliente(URL) as c:
        r = c.get("/api/content")
    assert r.status_code == 200
    return r


def test_forma_del_contrato(contenido):
    cuerpo = contenido.json()
    assert set(cuerpo) == {"data", "revision"}
    assert cuerpo["revision"] == 0
    data = cuerpo["data"]
    assert set(data) >= {
        "settings",
        "races",
        "news",
        "albums",
        "results",
        "sponsors",
        "collaborators",
        "regulation",
    }
    SiteData.model_validate(data)


def test_contenido_de_referencia(contenido):
    data = contenido.json()["data"]
    s = data["settings"]
    assert s["edition"] == "2027"
    assert s["date"] == ""
    assert s["registrationsOpen"] is False
    assert [r["id"] for r in data["races"]] == ["trail-27k", "speed-14k", "familiar-7k"]
    assert [n["id"] for n in data["news"]] == ["proxima-edicion"]
    assert [a["id"] for a in data["albums"]] == ["edicion-2026", "edicion-2025", "edicion-2024"]
    assert len(data["sponsors"]) == 8
    assert all(p["url"] == "" for p in data["sponsors"])


def test_sin_datos_de_prueba(contenido):
    texto = contenido.text
    data = contenido.json()["data"]
    assert data["settings"]["edition"] != "2028"  # D1
    assert data["races"][0]["image"] == "/reused/img/trail_inscripciones.webp"  # D2
    assert data["collaborators"] == []  # D3
    assert "PRUEBA" not in data["regulation"]  # D4
    assert "/media/" not in texto


def test_cabeceras(contenido):
    assert contenido.headers["cache-control"] == "no-store"
    assert contenido.headers["x-content-type-options"] == "nosniff"


def test_variante_admin_requiere_sesion():
    with crear_cliente(URL) as c:
        r = c.get("/api/content", params={"admin": "1"})
    assert r.status_code == 401
    assert "error" in r.json()


def test_solo_publicados_y_sin_clasificaciones_solidarias_ni_legadas():
    semilla = json.loads(RUTA_SEMILLA.read_text(encoding="utf-8"))
    semilla["news"].append({"id": "borrador", "title": "Borrador", "published": False})
    semilla["sponsors"].append({"id": "oculto", "name": "Oculto", "published": False})
    fila = {"position": 1, "bib": "1", "name": "Ana", "time": "1:00:00"}
    semilla["results"] = [
        {"id": "ok", "published": True, "raceId": "trail-27k", "race": "Trail", "rows": [fila]},
        {
            "id": "solidaria",
            "published": True,
            "raceId": "dorsal-solidario",
            "race": "Dorsal Solidario",
            "rows": [fila],
        },
        {"id": "legada", "published": True, "title": "Antigua", "url": "https://example.com/r.pdf"},
        {"id": "borrador-clas", "published": False, "raceId": "speed-14k", "rows": [fila]},
    ]
    publico = datos_publicos(SiteData.model_validate(semilla))
    assert [n["id"] for n in publico["news"]] == ["proxima-edicion"]
    assert "oculto" not in [p["id"] for p in publico["sponsors"]]
    assert [r["id"] for r in publico["results"]] == ["ok"]


@pytest.mark.parametrize(
    "cambio",
    [
        lambda d: d["settings"].update(edition="2O27"),
        lambda d: d["settings"].update(date="mañana"),
        lambda d: d["settings"].update(date="2027-07-10T09:00:00"),  # sin zona horaria
        lambda d: d["settings"].update(solidarityRegistration="http://example.com/pago"),
        lambda d: d["settings"].update(solidarityRegistration="https://u:p@example.com/pago"),
        lambda d: d["settings"].update(registrationMessage="x" * 2001),
        lambda d: d["settings"].update(email="no-es-un-correo"),
        lambda d: d["settings"].update(phone="9" * 41),
        lambda d: d["settings"].update(instagram="/reused/logos/logo1.webp"),
        lambda d: d["settings"].update(instagram="http://instagram.com/x"),
        lambda d: d["races"][0].update(id="id con espacios"),
        lambda d: d["races"][0].pop("published"),
        lambda d: d.update(regulation="x" * 100001),
        lambda d: d.update(races=[dict(d["races"][0], id=f"r{i}") for i in range(31)]),
    ],
)
def test_semilla_invalida_se_rechaza(cambio):
    semilla = json.loads(RUTA_SEMILLA.read_text(encoding="utf-8"))
    cambio(semilla)
    with pytest.raises(ValidationError):
        SiteData.model_validate(semilla)


def test_fecha_con_zona_es_valida():
    semilla = json.loads(RUTA_SEMILLA.read_text(encoding="utf-8"))
    semilla["settings"]["date"] = "2027-07-10T07:00:00.000Z"
    SiteData.model_validate(semilla)
