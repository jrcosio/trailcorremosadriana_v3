"""US3 · Consulta pública paginada, búsqueda sin tildes y contrato (feature 006)."""

import time

from tests.conftest import crear_cliente, escribir


def _csv_grande(n):
    lineas = ["pos;dorsal;nombre;tiempo;categoria;club;sexo;estado"]
    for i in range(1, n + 1):
        nombre = "José Gónzalez" if i == 7 else f"Participante {i}"
        club = "50% Montaña_Club" if i == 9 else ("Club Ñandú" if i % 2 else "")
        cat = "Senior" if i % 3 else "Veterano"
        lineas.append(
            f"{i};{i:04d};{nombre};1:{i % 60:02d}:00;{cat};{club};{'F' if i % 2 else 'M'};"
        )
    lineas.append("DNS;9999;Sin Salida;;;;;Sin salida")
    return "\n".join(lineas) + "\n"


def _publicar(c, csv, publicada=True):
    mapeo = {
        "position": 0,
        "bib": 1,
        "name": 2,
        "time": 3,
        "category": 4,
        "club": 5,
        "gender": 6,
        "status": 7,
    }
    r = escribir(
        c,
        "POST",
        "/api/admin/clasificaciones/vista-previa",
        json={
            "csv": csv,
            "mapping": mapeo,
            "sourceFile": "g.csv",
            "raceId": "trail-27k",
            "year": "2026",
        },
    )
    token = r.json()["token"]
    r = escribir(
        c,
        "PUT",
        "/api/admin/clasificaciones/grande",
        json={
            "title": "Grande",
            "year": "2026",
            "raceId": "trail-27k",
            "published": publicada,
            "importToken": token,
        },
    )
    assert r.status_code == 200


def _q(c, **params):
    return c.get("/api/clasificaciones/grande/participantes", params=params)


def test_paginacion_y_orden(admin_importado):
    _publicar(admin_importado, _csv_grande(120))
    r = _q(admin_importado).json()
    assert (r["total"], r["filtered"], r["page"], r["pages"], r["pageSize"]) == (121, 121, 1, 3, 50)
    assert [f["position"] for f in r["rows"][:3]] == [1, 2, 3]
    ultima = _q(admin_importado, pagina=3).json()
    assert len(ultima["rows"]) == 21 and ultima["rows"][-1]["status"] == "Sin salida"
    assert _q(admin_importado, pagina=99).json()["page"] == 3


def test_busqueda_sin_tildes_ni_mayusculas(admin_importado):
    _publicar(admin_importado, _csv_grande(60))
    for termino in ("gonzalez", "GÓNZALEZ", "jose"):
        assert [f["bib"] for f in _q(admin_importado, q=termino).json()["rows"]] == ["0007"]
    assert _q(admin_importado, q="0012").json()["rows"][0]["position"] == 12  # por dorsal
    assert (
        _q(admin_importado, q="nandu").json()["filtered"] == 29
    )  # club sin tilde (impares salvo el 9)
    assert [f["bib"] for f in _q(admin_importado, q="50%").json()["rows"]] == ["0009"]  # % escapado
    assert _q(admin_importado, q="_").json()["filtered"] == 1


def test_filtros_y_columnas(admin_importado):
    _publicar(admin_importado, _csv_grande(30))
    r = _q(admin_importado, categoria="Veterano", sexo="M").json()
    assert all(f["category"] == "Veterano" and f["gender"] == "M" for f in r["rows"])
    assert [f["position"] for f in r["rows"]] == [6, 12, 18, 24, 30]  # posiciones originales
    completo = _q(admin_importado).json()
    assert completo["categories"] == ["Senior", "Veterano"] and completo["genders"] == ["F", "M"]
    assert completo["columns"] == {"category": True, "club": True, "gender": True, "status": True}


def test_borrador_privado_y_contrato(admin_importado, base_importada):
    _publicar(admin_importado, _csv_grande(10), publicada=False)
    with crear_cliente(base_importada) as anonimo:
        assert anonimo.get("/api/clasificaciones/grande/participantes").status_code == 404
        assert anonimo.get("/api/content").json()["data"]["results"] == []
    privado = admin_importado.get("/api/content", params={"admin": "1"}).json()["data"]["results"]
    assert privado[0]["participants"] == 11 and len(privado[0]["rows"]) == 11
    item = privado[0]
    escribir(
        admin_importado,
        "PUT",
        "/api/admin/clasificaciones/grande",
        json={
            **{k: item[k] for k in ("title", "year", "raceId")},
            "published": True,
            "version": item["version"],
        },
    )
    publico = admin_importado.get("/api/content").json()["data"]["results"]
    assert (
        publico[0]["participants"] == 11
        and publico[0]["rows"] == []
        and "version" not in publico[0]
    )


def test_rendimiento_con_5000_participantes(admin_importado):
    _publicar(admin_importado, _csv_grande(4999))
    inicio = time.monotonic()
    r = _q(admin_importado, q="participante 4321")
    assert r.status_code == 200 and r.json()["filtered"] == 1
    assert time.monotonic() - inicio < 1.0


# --- Feature 012 · US10 (decisión P12): podio por sexo y, al filtrar por categoría, de la categoría


def _csv_podio(con_sexo=True):
    """Hombres 1–4 y 6; mujeres 5, 7 (empate), 9 y 10; con puesto y sin sexo; sin puesto."""
    filas = [
        ("1", "0001", "H1", "Vet A M", "Masculino", ""),
        ("2", "0002", "H2", "Senior M", "Masculino", ""),
        ("3", "0003", "H3", "Vet A M", "Masculino", ""),
        ("4", "0004", "H4", "Senior M", "Masculino", ""),
        ("5", "0005", "M1", "Senior F", "Femenino", ""),
        ("6", "0006", "H5", "Vet A M", "Masculino", ""),
        ("7", "0007", "M2", "Vet A F", "Femenino", ""),
        ("7", "0008", "M2b", "Senior F", "Femenino", ""),
        ("9", "0009", "M4", "Senior F", "Femenino", ""),
        ("10", "0010", "M5", "Vet A F", "Femenino", ""),
        ("11", "0012", "SinSexo", "", "", ""),
        ("DNF", "0011", "SinPuesto", "Senior F", "Femenino", "Retirado"),
    ]
    lineas = ["pos;dorsal;nombre;tiempo;categoria;club;sexo;estado"]
    for pos, dorsal, nombre, cat, sexo, estado in filas:
        lineas.append(f"{pos};{dorsal};{nombre};1:00:00;{cat};;{sexo if con_sexo else ''};{estado}")
    return "\n".join(lineas) + "\n"


def _podio(respuesta):
    return {f["name"]: f["podium"] for f in respuesta["rows"] if f["podium"]}


def test_podio_por_sexo_sin_filtros(admin_importado):
    _publicar(admin_importado, _csv_podio())
    r = _q(admin_importado).json()
    # 3 primeros hombres y 3 primeras mujeres; el empate comparte el 2.º y deja sin 3.º (rank).
    assert _podio(r) == {"H1": 1, "H2": 2, "H3": 3, "M1": 1, "M2": 2, "M2b": 2}
    por_nombre = {f["name"]: f for f in r["rows"]}
    assert por_nombre["SinSexo"]["podium"] is None  # con datos de sexo, sin sexo no entra
    assert por_nombre["SinPuesto"]["podium"] is None
    assert por_nombre["M1"]["position"] == 5  # la posición general no cambia


def test_podio_con_filtro_de_sexo(admin_importado):
    _publicar(admin_importado, _csv_podio())
    assert _podio(_q(admin_importado, sexo="Femenino").json()) == {"M1": 1, "M2": 2, "M2b": 2}
    assert _podio(_q(admin_importado, sexo="Masculino").json()) == {"H1": 1, "H2": 2, "H3": 3}


def test_podio_con_filtro_de_categoria(admin_importado):
    _publicar(admin_importado, _csv_podio())
    assert _podio(_q(admin_importado, categoria="Senior F").json()) == {"M1": 1, "M2b": 2, "M4": 3}
    assert _podio(_q(admin_importado, categoria="Vet A M").json()) == {"H1": 1, "H3": 2, "H5": 3}


def test_la_busqueda_no_cambia_el_podio(admin_importado):
    _publicar(admin_importado, _csv_podio())
    assert _podio(_q(admin_importado, q="0005").json()) == {"M1": 1}
    assert _podio(_q(admin_importado, q="0009", categoria="Senior F").json()) == {"M4": 3}
    assert _podio(_q(admin_importado, q="0009").json()) == {}  # 4.ª mujer: fuera del podio


def test_podio_general_sin_datos_de_sexo(admin_importado):
    _publicar(admin_importado, _csv_podio(con_sexo=False))
    assert _podio(_q(admin_importado).json()) == {"H1": 1, "H2": 2, "H3": 3}
