"""Sesiones de administración opacas y revocables (data-model.md de la feature 002)."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session

from app.core.seguridad import huella, nuevo_token
from app.models import Administrador, Sesion

ACTUALIZAR_USO_CADA = timedelta(minutes=5)
CONSERVAR_ANTIGUAS = timedelta(days=7)


@dataclass(frozen=True)
class SesionValida:
    sesion_id: int
    administrador_id: int
    usuario: str
    csrf_hash: str
    expira_en: datetime


def _ahora() -> datetime:
    return datetime.now(UTC)


def crear(db: Session, admin: Administrador, horas: int) -> tuple[str, str, datetime]:
    """Crea la sesión y devuelve (token, csrf, expira_en). Solo se guardan sus huellas."""
    token, csrf = nuevo_token(), nuevo_token()
    expira = _ahora() + timedelta(hours=horas)
    db.add(
        Sesion(
            administrador_id=admin.id,
            token_hash=huella(token),
            csrf_hash=huella(csrf),
            expira_en=expira,
        )
    )
    return token, csrf, expira


def validar(db: Session, token: str | None) -> SesionValida | None:
    """Sesión no revocada, no caducada y de una cuenta activa; si no, None."""
    if not token or len(token) > 128:
        return None
    ahora = _ahora()
    fila = db.execute(
        select(Sesion, Administrador.usuario)
        .join(Administrador, Administrador.id == Sesion.administrador_id)
        .where(
            Sesion.token_hash == huella(token),
            Sesion.revocada_en.is_(None),
            Sesion.expira_en > ahora,
            Administrador.activo.is_(True),
        )
    ).first()
    if fila is None:
        return None
    sesion, usuario = fila
    if ahora - sesion.ultimo_uso_en > ACTUALIZAR_USO_CADA:
        sesion.ultimo_uso_en = ahora
        db.commit()
    return SesionValida(
        sesion.id, sesion.administrador_id, usuario, sesion.csrf_hash, sesion.expira_en
    )


def renovar_csrf(db: Session, sesion_id: int) -> str:
    csrf = nuevo_token()
    db.execute(update(Sesion).where(Sesion.id == sesion_id).values(csrf_hash=huella(csrf)))
    db.commit()
    return csrf


def revocar(db: Session, sesion_id: int) -> None:
    db.execute(
        update(Sesion)
        .where(Sesion.id == sesion_id, Sesion.revocada_en.is_(None))
        .values(revocada_en=_ahora())
    )
    db.commit()


def revocar_todas(db: Session, administrador_id: int, confirmar: bool = True) -> int:
    resultado = db.execute(
        update(Sesion)
        .where(Sesion.administrador_id == administrador_id, Sesion.revocada_en.is_(None))
        .values(revocada_en=_ahora())
    )
    if confirmar:
        db.commit()
    return resultado.rowcount or 0


def limpiar_antiguas(db: Session) -> None:
    """Borra sesiones caducadas o revocadas hace más de 7 días."""
    limite = _ahora() - CONSERVAR_ANTIGUAS
    db.execute(delete(Sesion).where(or_(Sesion.expira_en < limite, Sesion.revocada_en < limite)))
