"""Edición actual, fecha y contador (FR-001–003, FR-007 de la feature 004)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Edicion
from app.schemas.evento import EventoEntrada
from app.services.errores import Conflicto
from app.services.fechas import a_instante, a_iso


def actual(db: Session, bloquear: bool = False) -> Edicion | None:
    consulta = select(Edicion).where(Edicion.es_actual.is_(True))
    return db.scalar(consulta.with_for_update() if bloquear else consulta)


def obtener_o_crear(db: Session, anio: int) -> Edicion:
    edicion = db.scalar(select(Edicion).where(Edicion.anio == anio).with_for_update())
    if edicion is None:
        edicion = Edicion(anio=anio, mostrar_contador=True, es_actual=False, version=1)
        db.add(edicion)
        db.flush()
    return edicion


def a_contrato(edicion: Edicion | None) -> dict:
    if edicion is None:
        return {"edition": "", "date": "", "countdown": True, "version": 0}
    return {
        "edition": str(edicion.anio),
        "date": a_iso(edicion.fecha_hora),
        "countdown": edicion.mostrar_contador,
        "version": edicion.version,
    }


def guardar(db: Session, entrada: EventoEntrada) -> dict:
    vigente = actual(db, bloquear=True)
    if entrada.version != (vigente.version if vigente else 0):
        db.rollback()
        raise Conflicto
    anio = int(entrada.edition)
    if vigente is not None and vigente.anio == anio:
        destino = vigente
    else:
        destino = obtener_o_crear(db, anio)
        if vigente is not None:
            vigente.es_actual = False
            vigente.version += 1
            db.flush()  # libera el índice único parcial antes de marcar la nueva edición
        destino.es_actual = True
    destino.fecha_hora = a_instante(entrada.date)
    destino.mostrar_contador = entrada.countdown
    destino.version += 1
    db.commit()
    return a_contrato(destino)
