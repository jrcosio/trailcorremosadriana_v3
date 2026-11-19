"""Fechas del evento en Europe/Madrid (FR-002, casos límite de cambio horario)."""

import pytest

from app.services.fechas import FechaNoValida, a_instante, a_iso, hora_peninsular


@pytest.mark.parametrize(
    ("local", "utc"),
    [
        ("2027-07-10T09:00", "2027-07-10T07:00:00.000Z"),  # verano (CEST, +02:00)
        ("2027-01-15T09:00", "2027-01-15T08:00:00.000Z"),  # invierno (CET, +01:00)
        ("2026-07-11T09:00:00", "2026-07-11T07:00:00.000Z"),
    ],
)
def test_hora_local_sin_zona_es_peninsular(local, utc):
    instante = a_instante(local)
    assert a_iso(instante) == utc
    assert hora_peninsular(instante) == local[:16]


def test_iso_con_zona_se_respeta():
    assert a_iso(a_instante("2027-07-10T07:00:00.000Z")) == "2027-07-10T07:00:00.000Z"
    assert a_iso(a_instante("2027-07-10T09:00:00+02:00")) == "2027-07-10T07:00:00.000Z"


def test_hora_inexistente_avanza():
    # 28/03/2027 02:30 no existe en Madrid (salto 02:00 → 03:00): avanza a 03:30 CEST.
    assert hora_peninsular(a_instante("2027-03-28T02:30")) == "2027-03-28T03:30"


def test_hora_ambigua_toma_la_primera():
    # 31/10/2027 02:30 ocurre dos veces: la primera es en horario de verano (+02:00).
    assert a_iso(a_instante("2027-10-31T02:30")) == "2027-10-31T00:30:00.000Z"


def test_vacio_y_no_valido():
    assert a_instante("") is None and a_instante("  ") is None
    assert a_iso(None) == ""
    with pytest.raises(FechaNoValida):
        a_instante("mañana")
