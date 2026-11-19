"""Gestión de cuentas de administración (solo mediante el comando de operador)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seguridad import hash_password, validar_password, validar_usuario
from app.models import Administrador
from app.services import sesiones


class AdminYaExiste(Exception):
    pass


class AdminNoEncontrado(Exception):
    pass


def buscar(db: Session, usuario: str) -> Administrador | None:
    return db.scalar(select(Administrador).where(Administrador.usuario == usuario))


def _obtener(db: Session, usuario: str) -> Administrador:
    admin = buscar(db, validar_usuario(usuario))
    if admin is None:
        raise AdminNoEncontrado(usuario)
    return admin


def crear(db: Session, usuario: str, password: str) -> Administrador:
    """Crea una cuenta activa. Nunca modifica una existente (FR-002)."""
    normalizado = validar_usuario(usuario)
    validar_password(password, normalizado)
    if buscar(db, normalizado) is not None:
        raise AdminYaExiste(normalizado)
    admin = Administrador(usuario=normalizado, hash_password=hash_password(password))
    db.add(admin)
    db.commit()
    return admin


def restablecer_password(db: Session, usuario: str, password: str) -> int:
    """Cambia la contraseña y revoca todas las sesiones de la cuenta (FR-005)."""
    admin = _obtener(db, usuario)
    validar_password(password, admin.usuario)
    admin.hash_password = hash_password(password)
    admin.password_cambiada_en = datetime.now(UTC)
    revocadas = sesiones.revocar_todas(db, admin.id, confirmar=False)
    db.commit()
    return revocadas


def desactivar(db: Session, usuario: str) -> int:
    admin = _obtener(db, usuario)
    admin.activo = False
    revocadas = sesiones.revocar_todas(db, admin.id, confirmar=False)
    db.commit()
    return revocadas


def activar(db: Session, usuario: str) -> None:
    admin = _obtener(db, usuario)
    admin.activo = True
    db.commit()


def revocar_sesiones(db: Session, usuario: str) -> int:
    admin = _obtener(db, usuario)
    return sesiones.revocar_todas(db, admin.id)


def listar(db: Session) -> list[Administrador]:
    return list(db.scalars(select(Administrador).order_by(Administrador.usuario)))
