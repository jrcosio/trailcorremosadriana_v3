"""Reglamento por edición (feature 010): el de la edición actual o, si no tiene, el más reciente."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Edicion
from app.schemas.reglamento import ReglamentoEntrada
from app.services import evento
from app.services.errores import Conflicto, NoEncontrado
from app.services.inscripciones import SIN_EDICION


def mostrado(db: Session) -> str | None:
    """Texto que ven la web y el editor (research R2); `None` si ninguna edición lo tiene."""
    actual = evento.actual(db)
    if actual is not None and actual.reglamento:
        return actual.reglamento
    return db.scalar(
        select(Edicion.reglamento)
        .where(Edicion.reglamento != "")
        .order_by(Edicion.anio.desc())
        .limit(1)
    )


def guardar(db: Session, entrada: ReglamentoEntrada) -> dict:
    vigente = evento.actual(db, bloquear=True)
    if vigente is None:
        db.rollback()
        raise NoEncontrado(SIN_EDICION)
    if entrada.version != vigente.version:  # versión compartida con evento e inscripciones
        db.rollback()
        raise Conflicto
    vigente.reglamento = entrada.regulation
    vigente.version += 1
    db.commit()
    return {"regulation": vigente.reglamento, "version": vigente.version}
