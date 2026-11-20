"""Configuración de contacto de fila única con versión (feature 010)."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Configuracion
from app.schemas.contacto import ContactoEntrada
from app.services.errores import Conflicto


def obtener(db: Session) -> Configuracion | None:
    return db.get(Configuracion, 1)


def a_contrato(c: Configuracion) -> dict:
    return {"email": c.correo, "phone": c.telefono, "instagram": c.instagram, "version": c.version}


def guardar(db: Session, entrada: ContactoEntrada) -> dict:
    conf = db.scalar(select(Configuracion).where(Configuracion.id == 1).with_for_update())
    if entrada.version != (conf.version if conf else 0):
        db.rollback()
        raise Conflicto
    if conf is None:
        conf = Configuracion(id=1, version=0)
        db.add(conf)
    conf.correo, conf.telefono, conf.instagram = entrada.email, entrada.phone, entrada.instagram
    conf.version += 1
    try:
        db.commit()
    except IntegrityError:  # dos altas simultáneas de la fila única
        db.rollback()
        raise Conflicto from None
    return a_contrato(conf)
