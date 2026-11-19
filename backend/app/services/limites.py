"""Límite persistente de accesos fallidos por origen de red (data-model.md, LimiteLogin)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import LimiteLogin


def _ahora() -> datetime:
    return datetime.now(UTC)


def segundos_de_bloqueo(db: Session, clave: str, maximo: int, ventana: timedelta) -> int:
    """Bloquea la fila (FOR UPDATE) y devuelve los segundos de espera; 0 si se puede intentar.

    Debe llamarse dentro de la transacción del intento de acceso para serializar intentos
    concurrentes desde el mismo origen. Reinicia la ventana si ha expirado.
    """
    fila = db.scalar(select(LimiteLogin).where(LimiteLogin.clave == clave).with_for_update())
    if fila is None:
        return 0
    fin = fila.inicio + ventana
    ahora = _ahora()
    if fin <= ahora:
        db.delete(fila)
        db.flush()
        return 0
    if fila.intentos >= maximo:
        return max(1, int((fin - ahora).total_seconds()) + 1)
    return 0


def registrar_fallo(db: Session, clave: str) -> None:
    sentencia = insert(LimiteLogin).values(clave=clave, intentos=1, inicio=_ahora())
    db.execute(
        sentencia.on_conflict_do_update(
            index_elements=[LimiteLogin.clave],
            set_={"intentos": LimiteLogin.intentos + 1},
        )
    )


def reiniciar(db: Session, clave: str) -> None:
    db.execute(delete(LimiteLogin).where(LimiteLogin.clave == clave))


def limpiar_caducados(db: Session, ventana: timedelta) -> None:
    db.execute(delete(LimiteLogin).where(LimiteLogin.inicio < _ahora() - ventana))
