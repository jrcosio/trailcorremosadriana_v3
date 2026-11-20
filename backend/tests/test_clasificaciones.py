"""US1/US2/US4/US5 · Importación transaccional y gestión de clasificaciones (feature 006)."""

import io
import uuid

import pytest

from app import cli
from app.schemas.clasificaciones import ClasificacionEntrada
from app.services import clasificaciones as servicio
from tests.conftest import consultar, crear_cliente, entrar, escribir

CSV3 = (
    "posicion;dorsal;nombre;apellidos;tiempo;categoria;club;sexo;estado\n"
    "1;101;Ana;García;01:42:10;Senior;Club A;F;\n"
    "2;102;Luis;Pérez;01:47:32;Veterano A;;M;\n"
    "DNF;103;Eva;Ruiz;;Senior;;F;Retirado\n"
)
CSV1 = "pos;dorsal;nombre;tiempo\n1;201;Nuevo Participante;00:59:00\n"
MAPEO3 = {
    "position": 0,
    "bib": 1,
    "name": 2,
    "surname": 3,
    "time": 4,
    "category": 5,
    "club": 6,
    "gender": 7,
    "status": 8,
}
MAPEO1 = {"position": 0, "bib": 1, "name": 2, "time": 3}


def _previa(c, csv=CSV3, mapeo=MAPEO3, race="trail-27k", year="2026", **extra):
    datos = {
        "csv": csv,
        "mapping": mapeo,
        "sourceFile": "resultados.csv",
        "raceId": race,
        "year": year,
        **extra,
    }
    return escribir(c, "POST", "/api/admin/clasificaciones/vista-previa", json=datos)


def _guardar(c, ident="clas-trail", token=None, version=0, **cambios):
    datos = {
        "title": "Clasificación Trail",
        "year": "2026",
        "raceId": "trail-27k",
        "published": True,
        "version": version,
    }
    if token:
        datos["importToken"] = token
    return escribir(c, "PUT", f"/api/admin/clasificaciones/{ident}", json={**datos, **cambios})


def _crear(c, csv=CSV3, mapeo=MAPEO3, **kw):
    token = _previa(c, csv, mapeo).json()["token"]
    r = _guardar(c, token=token, **kw)
    assert r.status_code == 200, r.text
    return r.json()


def test_vista_previa_y_creacion(admin_importado, base_importada):
    r = _previa(admin_importado)
    assert r.status_code == 200 and r.json()["participants"] == 3
    creada = _guardar(admin_importado, token=r.json()["token"]).json()
    assert (
        creada["participants"] == 3
        and creada["version"] == 1
        and creada["sourceFile"] == "resultados.csv"
    )
    assert [f["bib"] for f in creada["rows"]] == ["101", "102", "103"]
    assert creada["rows"][2] == {
        "position": None,
        "bib": "103",
        "name": "Eva Ruiz",
        "time": "",
        "category": "Senior",
        "club": "",
        "gender": "F",
        "status": "Retirado",
    }
    assert (
        consultar(base_importada, "SELECT count(*) FROM importaciones_csv")[0][0] == 0
    )  # un solo uso


@pytest.mark.parametrize(
    ("csv", "mapeo", "mensaje"),
    [
        (CSV3.replace(";102;", ";101;"), MAPEO3, "repetido"),
        (CSV3.replace("01:42:10", ""), MAPEO3, "tiempo"),
        (CSV3, {}, "Posición"),
        ("pos;dorsal;nombre;tiempo\n1;2;Ana\n", MAPEO1, "columnas"),
    ],
)
def test_vista_previa_rechaza_con_fila(admin_importado, csv, mapeo, mensaje):
    r = _previa(admin_importado, csv, mapeo)
    assert r.status_code == 400 and mensaje in r.json()["error"]


def test_prueba_sin_ficha_y_solidaria(admin_importado):
    r = _previa(admin_importado, year="2027")
    assert r.status_code == 400 and "Configura primero la prueba" in r.json()["error"]
    trail = {
        x["id"]: x
        for x in admin_importado.get("/api/content", params={"admin": "1"}).json()["data"]["races"]
    }["trail-27k"]
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/carreras/dorsal-solidario",
        json={**trail, "title": "Dorsal Solidario", "version": 0},
    )
    r = _previa(admin_importado, race="dorsal-solidario")
    assert (
        r.status_code == 400 and r.json()["error"] == "El Dorsal Solidario no tiene clasificación."
    )


def test_duplicado_por_prueba_y_edicion(admin_importado):
    _crear(admin_importado)
    r = _previa(admin_importado)
    assert r.status_code == 409 and r.json()["error"].startswith("Ya existe una clasificación")
    # Editar la propia sí se permite (sustitución).
    assert _previa(admin_importado, id="clas-trail").status_code == 200


def test_sustitucion_total(admin_importado, base_importada):
    creada = _crear(admin_importado)
    token = _previa(admin_importado, CSV1, MAPEO1, id="clas-trail").json()["token"]
    r = _guardar(admin_importado, token=token, version=creada["version"])
    assert r.status_code == 200
    filas = consultar(base_importada, "SELECT dorsal FROM resultados ORDER BY orden")
    assert filas == [("201",)]
    assert r.json()["participants"] == 1


def test_token_de_otra_sesion_caducado_o_reutilizado(admin_importado, base_importada):
    token = _previa(admin_importado).json()["token"]
    with crear_cliente(base_importada) as otra:
        entrar(otra)
        assert _guardar(otra, token=token).status_code == 400
    consultar(
        base_importada, "UPDATE importaciones_csv SET expira_en = now() - interval '1 second'"
    )
    assert _guardar(admin_importado, token=token).status_code == 400
    token = _previa(admin_importado).json()["token"]
    assert _guardar(admin_importado, token=token).status_code == 200
    assert _guardar(admin_importado, ident="otra", token=token).status_code in (400, 409)
    assert _guardar(admin_importado, token=str(uuid.uuid4()), version=1).status_code == 400


def test_huella_manipulada_se_rechaza(admin_importado, base_importada):
    token = _previa(admin_importado).json()["token"]
    consultar(
        base_importada,
        "UPDATE importaciones_csv SET filas = jsonb_set(filas, '{0,name}', '\"Otro\"')",
    )
    assert _guardar(admin_importado, token=token).status_code == 400


def test_fallo_durante_la_sustitucion_conserva_lo_anterior(
    admin_importado, base_importada, monkeypatch
):
    creada = _crear(admin_importado)
    token = _previa(admin_importado, CSV1, MAPEO1, id="clas-trail").json()["token"]

    def explota(*_):
        raise RuntimeError("fallo simulado de escritura")

    monkeypatch.setattr(servicio, "_insertar_filas", explota)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(base_importada)
    sesion_id = consultar(base_importada, "SELECT max(id) FROM sesiones")[0][0]
    with Session(engine) as db, pytest.raises(RuntimeError):
        servicio.guardar(
            db,
            "clas-trail",
            sesion_id,
            ClasificacionEntrada(
                title="X",
                year="2026",
                raceId="trail-27k",
                importToken=token,
                version=creada["version"],
            ),
        )
    engine.dispose()
    assert consultar(base_importada, "SELECT dorsal FROM resultados ORDER BY orden") == [
        ("101",),
        ("102",),
        ("103",),
    ]
    assert consultar(base_importada, "SELECT titulo, version FROM clasificaciones")[0] == (
        "Clasificación Trail",
        1,
    )


def test_metadatos_sin_token_y_versiones(admin_importado):
    creada = _crear(admin_importado)
    r = _guardar(admin_importado, version=creada["version"], published=False, title="Nuevo título")
    assert r.status_code == 200 and r.json()["published"] is False and r.json()["participants"] == 3
    assert _guardar(admin_importado, version=creada["version"]).status_code == 409
    assert (
        _guardar(admin_importado, ident="clas-trail-bis").status_code == 409
    )  # misma prueba y edición
    r = _guardar(admin_importado, ident="sin-csv", raceId="speed-14k")
    assert (
        r.status_code == 400 and r.json()["error"] == "Importa y confirma un CSV antes de guardar."
    )


def test_borrar_y_prueba_con_clasificacion(admin_importado, base_importada):
    creada = _crear(admin_importado)
    trail = {
        x["id"]: x
        for x in admin_importado.get("/api/content", params={"admin": "1"}).json()["data"]["races"]
    }["trail-27k"]
    r = escribir(
        admin_importado,
        "DELETE",
        "/api/admin/carreras/trail-27k",
        params={"version": trail["version"]},
    )
    assert (
        r.status_code == 409
        and r.json()["error"] == "No se puede borrar una prueba con clasificaciones."
    )
    assert (
        escribir(
            admin_importado,
            "DELETE",
            "/api/admin/clasificaciones/clas-trail",
            params={"version": 99},
        ).status_code
        == 409
    )
    assert (
        escribir(
            admin_importado,
            "DELETE",
            "/api/admin/clasificaciones/clas-trail",
            params={"version": creada["version"]},
        ).status_code
        == 200
    )
    assert consultar(base_importada, "SELECT count(*) FROM resultados")[0][0] == 0


def test_proteccion(base_importada):
    with crear_cliente(base_importada) as c:
        assert c.post("/api/admin/clasificaciones/vista-previa", json={}).status_code == 401
        assert c.put("/api/admin/clasificaciones/x", json={}).status_code == 401


def _cli(url, *args, datos: bytes):
    salida = io.StringIO()
    entrada = io.TextIOWrapper(io.BytesIO(datos))
    return cli.main(list(args), database_url=url, entrada=entrada, salida=salida), salida.getvalue()


def test_comando_importar_clasificacion(base_importada):
    args = [
        "importar-clasificacion",
        "--carrera",
        "speed-14k",
        "--edicion",
        "2026",
        "--titulo",
        "Speed 2026",
        "--archivo",
        "Clasificacion_14km.csv",
        "--publicar",
    ]
    produccion = (
        "﻿Pos,Dorsal,Nombre,Apellidos,Categoria,Pos Categoria,Genero,Pos Genero,Club,Meta,Estado\n"
        "1,250,José,Peña,Senior M,1,Masculino,1,Club Ñ,01:19:45,Finalizado\n"
        ",77,Ana,López,,,Femenino,,,,Sin salida\n"
    ).encode("cp1252", errors="ignore")
    codigo, texto = _cli(base_importada, *args, datos=produccion)
    assert codigo == 0 and "creada: 2 participantes" in texto
    assert (
        consultar(base_importada, "SELECT nombre FROM resultados ORDER BY orden")[0][0]
        == "José Peña"
    )
    codigo, texto = _cli(base_importada, *args, datos=b"pos;dorsal;nombre;tiempo\n1;9;X;1:00\n")
    assert codigo == 0 and "sin cambios" in texto
    codigo, texto = _cli(
        base_importada, *args, "--sustituir", datos=b"pos;dorsal;nombre;tiempo\n1;9;X;1:00\n"
    )
    assert codigo == 0 and "sustituida: 1 participantes" in texto
    codigo, _ = _cli(base_importada, *args, "--sustituir", datos=b"pos;dorsal\n1;2\n")
    assert codigo == 2


def test_importaciones_caducadas_se_limpian(admin_importado, base_importada):
    _previa(admin_importado)
    consultar(
        base_importada, "UPDATE importaciones_csv SET expira_en = now() - interval '1 second'"
    )
    _crear(admin_importado, CSV1, MAPEO1)  # guardar limpia las caducadas
    assert consultar(base_importada, "SELECT count(*) FROM importaciones_csv")[0][0] == 0
    _previa(admin_importado, race="speed-14k")
    consultar(
        base_importada, "UPDATE importaciones_csv SET expira_en = now() - interval '1 second'"
    )
    with crear_cliente(base_importada) as otra:
        entrar(otra)  # cada acceso correcto también limpia
    assert consultar(base_importada, "SELECT count(*) FROM importaciones_csv")[0][0] == 0
