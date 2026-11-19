"""Fechas del evento: entrada y salida en Europe/Madrid, almacenamiento como instante UTC."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")


class FechaNoValida(ValueError):
    pass


def a_instante(valor: str) -> datetime | None:
    """'' → None. ISO con zona → ese instante. ISO sin zona → hora peninsular (fold=0).

    Con fold=0, una hora inexistente (salto de primavera) se interpreta con el desfase anterior
    y avanza a la hora válida siguiente; una hora ambigua (otoño) toma la primera ocurrencia.
    """
    texto = (valor or "").strip()
    if not texto:
        return None
    try:
        fecha = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FechaNoValida("Fecha y hora no válidas.") from exc
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=MADRID, fold=0)
    return fecha.astimezone(UTC)


def a_iso(instante: datetime | None) -> str:
    """Instante → '2027-07-10T07:00:00.000Z' (formato del prototipo); None → ''."""
    if instante is None:
        return ""
    utc = instante.astimezone(UTC)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc.microsecond // 1000:03d}Z"


def hora_peninsular(instante: datetime) -> str:
    return instante.astimezone(MADRID).strftime("%Y-%m-%dT%H:%M")
