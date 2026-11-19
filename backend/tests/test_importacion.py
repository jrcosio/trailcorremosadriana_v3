"""US3 · Importación idempotente de los datos aprobados (FR-010, SC-006)."""

import io

from app import cli
from tests.conftest import consultar, importar_datos


def _cli(url, *args, entrada=""):
    salida = io.StringIO()
    codigo = cli.main(list(args), database_url=url, entrada=io.StringIO(entrada), salida=salida)
    return codigo, salida.getvalue()


def test_base_vacia_crea_ediciones_y_pruebas(base_migrada):
    codigo, texto = _cli(base_migrada, "importar-inicial")
    assert codigo == 0 and "Ediciones creadas" in texto and "Pruebas creadas" in texto
    ediciones = consultar(
        base_migrada,
        "SELECT anio, to_char(fecha_hora AT TIME ZONE 'Europe/Madrid', 'YYYY-MM-DD HH24:MI'), "
        "mostrar_contador, es_actual FROM ediciones ORDER BY anio",
    )
    assert ediciones == [(2026, "2026-07-11 09:00", False, False), (2027, None, True, True)]
    pruebas = consultar(
        base_migrada,
        "SELECT c.slug, c.orden, e.anio, f.km::text, f.desnivel, f.publicada FROM carreras c "
        "JOIN carreras_edicion f ON f.carrera_id = c.id JOIN ediciones e ON e.id = f.edicion_id "
        "ORDER BY c.orden",
    )
    assert pruebas == [
        ("trail-27k", 0, 2026, "27.00", 1700, True),
        ("speed-14k", 1, 2026, "14.00", 800, True),
        ("familiar-7k", 2, 2026, "7.00", 250, True),
    ]


def test_repetir_no_cambia_nada(base_migrada):
    _cli(base_migrada, "importar-inicial")
    antes = consultar(base_migrada, "SELECT * FROM carreras_edicion ORDER BY id")
    codigo, texto = _cli(base_migrada, "importar-inicial")
    assert codigo == 0 and "Sin cambios" in texto
    assert consultar(base_migrada, "SELECT * FROM carreras_edicion ORDER BY id") == antes
    assert consultar(base_migrada, "SELECT count(*) FROM ediciones")[0][0] == 2


def test_no_sobrescribe_datos_existentes(base_migrada):
    importar_datos(base_migrada)
    consultar(base_migrada, "UPDATE carreras_edicion SET precio = '30 €'")
    importar_datos(base_migrada)
    assert {p for (p,) in consultar(base_migrada, "SELECT precio FROM carreras_edicion")} == {
        "30 €"
    }


def test_reemplazar_exige_confirmacion(base_migrada):
    importar_datos(base_migrada)
    consultar(base_migrada, "UPDATE carreras_edicion SET precio = '30 €'")
    codigo, texto = _cli(base_migrada, "importar-inicial", "--reemplazar", entrada="no\n")
    assert codigo == 1 and "Cancelado" in texto
    assert {p for (p,) in consultar(base_migrada, "SELECT precio FROM carreras_edicion")} == {
        "30 €"
    }
    codigo, _ = _cli(base_migrada, "importar-inicial", "--reemplazar", entrada="REEMPLAZAR\n")
    assert codigo == 0
    assert "28 €" in {p for (p,) in consultar(base_migrada, "SELECT precio FROM carreras_edicion")}
