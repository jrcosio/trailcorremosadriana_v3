"""Lector CSV del servidor: equivalente a frontend/tests/clasificaciones.test.tsx (feature 006)."""

import pytest

from app.services.csv_clasificaciones import (
    CsvNoValido,
    adivinar_mapeo,
    decodificar,
    leer_csv,
    mapear,
    texto_busqueda,
)

PLANTILLA = (
    "posicion;dorsal;nombre;apellidos;tiempo;categoria;club;sexo;estado\n"
    "1;101;Participante;Ejemplo Uno;01:42:10;Senior;Club ejemplo;F;\n"
    "2;102;Participante;Ejemplo Dos;01:47:32;Veterano A;;M;\n"
    "DNF;103;Participante;Ejemplo Tres;;Senior;;M;Retirado\n"
)


def _filas(texto, mapeo=None):
    tabla = leer_csv(texto)
    return mapear(tabla, mapeo if mapeo is not None else adivinar_mapeo(tabla.cabeceras))


def test_plantilla():
    filas = _filas(PLANTILLA)
    assert len(filas) == 3
    assert filas[2]["position"] is None and filas[2]["status"] == "Retirado"
    assert filas[0]["name"] == "Participante Ejemplo Uno"


def test_bom_crlf_y_windows_1252():
    assert len(leer_csv("﻿" + PLANTILLA.replace("\n", "\r\n")).registros) == 3
    texto = decodificar("pos;dorsal;nombre;tiempo\n1;1;José Peña;1:00:00\n".encode("cp1252"))
    assert _filas(texto)[0]["name"] == "José Peña"


def test_comas_comillas_y_orden():
    filas = _filas(
        'Rank,Bib,Name,Time\n2,002,"López, Ana",1:23:45\n1,001,"Peña ""Paz""",1:20:00',
        {"position": 0, "bib": 1, "name": 2, "time": 3},
    )
    assert [f["name"] for f in filas] == ['Peña "Paz"', "López, Ana"]


def test_tabulador_y_ceros_a_la_izquierda():
    assert leer_csv("Puesto\tDorsal\tNombre\tTiempo\n1\t01\tAna\t1:01:01").separador == "\t"
    filas = _filas(
        "Orden;Número;Atleta;Marca\n1;001;Ana;00:45:03",
        {"position": 0, "bib": 1, "name": 2, "time": 3},
    )
    assert filas[0]["bib"] == "001"


def test_posiciones_con_sufijo_y_no_clasificados():
    filas = _filas(
        "pos;dorsal;nombre;tiempo;estado\n1º;1;A;1:00;\n2.;2;B;1:01;\nNC;3;C;;\n-;4;D;;DSQ\n"
    )
    assert [f["position"] for f in filas] == [1, 2, None, None]
    assert [f["status"] for f in filas[2:]] == ["NC", "DSQ"]


@pytest.mark.parametrize(
    ("texto", "mensaje"),
    [
        ("pos;dorsal;nombre;tiempo\n1;2;Ana", "columnas"),
        ('pos;dorsal\n1;"Ana', "(?i)comillas"),
        ("x" * 1_000_001, "1 MB"),
        ("pos;dorsal\n" + "1;2\n" * 5001, "5000"),
        ("a;" * 61 + "b\n" + "1;" * 61 + "1\n", "60 columnas"),
        ("pos;dorsal\n", "no contiene participantes"),
        ("pos;;tiempo\n1;2;3\n", "cabecera"),
    ],
)
def test_archivo_no_valido(texto, mensaje):
    with pytest.raises(CsvNoValido, match=mensaje):
        _filas(texto)


@pytest.mark.parametrize(
    ("cambio", "mensaje"),
    [
        (lambda t: t.replace(";102;", ";101;"), "repetido"),
        (lambda t: t.replace("01:42:10", ""), "tiempo"),
        (lambda t: t.replace("\n2;102", "\nx;102"), "posición inválida"),
        (lambda t: t.replace("Participante;Ejemplo Dos", ";"), "nombre"),
    ],
)
def test_filas_no_validas(cambio, mensaje):
    with pytest.raises(CsvNoValido, match=mensaje):
        _filas(cambio(PLANTILLA))


def test_mapeo_obligatorio_y_columnas_distintas():
    tabla = leer_csv(PLANTILLA)
    with pytest.raises(CsvNoValido, match="Posición"):
        mapear(tabla, {})
    mapeo = adivinar_mapeo(tabla.cabeceras)
    with pytest.raises(CsvNoValido, match="distinta"):
        mapear(tabla, {**mapeo, "bib": mapeo["name"]})
    with pytest.raises(CsvNoValido, match="inválida"):
        mapear(tabla, {**mapeo, "club": 99})


def test_formato_de_produccion():
    texto = (
        "﻿Pos,Dorsal,Nombre,Apellidos,Categoria,Pos Categoria,Genero,Pos Genero,Club,Meta,Estado\n"
        "1,250,Fernando,Montes Fernandez,Senior M,1,Masculino,1,"
        "La Braña solorunners,01:19:45,Finalizado\n"
        ",77,Ana,Pérez,,,Femenino,,,,Sin salida\n"
    )
    tabla = leer_csv(texto)
    mapeo = adivinar_mapeo(tabla.cabeceras)
    assert mapeo == {
        "position": 0,
        "bib": 1,
        "name": 2,
        "surname": 3,
        "time": 9,
        "category": 4,
        "club": 8,
        "gender": 6,
        "status": 10,
    }
    filas = mapear(tabla, mapeo)
    assert (
        filas[0]["time"] == "01:19:45"
        and filas[1]["position"] is None
        and filas[1]["status"] == "Sin salida"
    )


def test_dorsal_vacio_solo_para_no_clasificados():
    filas = _filas(
        "pos;dorsal;nombre;tiempo;estado\n1;1;A;1:00;\n;;B;;Sin salida\n;;C;;Sin salida\n"
    )
    assert [(f["bib"], f["status"]) for f in filas] == [
        ("1", ""),
        ("", "Sin salida"),
        ("", "Sin salida"),
    ]
    with pytest.raises(CsvNoValido, match="dorsal es obligatorio para los clasificados"):
        _filas("pos;dorsal;nombre;tiempo\n1;;A;1:00\n")


def test_texto_de_busqueda_sin_tildes():
    assert texto_busqueda("07", "José Peña", "Club Ñandú") == "07 jose pena club nandu"
