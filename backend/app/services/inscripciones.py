"""Apertura de inscripciones y Dorsal Solidario de la edición actual (feature 005)."""

from sqlalchemy.orm import Session

from app.core.referencias import url_externa_segura
from app.models import Edicion
from app.schemas.evento import InscripcionesEntrada
from app.services import carreras, evento
from app.services.errores import Conflicto, NoEncontrado

SIN_DESTINOS = (
    "No puedes abrir las inscripciones sin ningún enlace de inscripción "
    "ni de pago del Dorsal Solidario."
)
SIN_EDICION = "No hay una edición actual configurada."


class AperturaSinDestinos(ValueError):
    pass


def a_contrato(edicion: Edicion | None) -> dict:
    if edicion is None:
        return {
            "registrationsOpen": False,
            "registrationMessage": "",
            "solidarityRegistration": "",
            "version": 0,
        }
    return {
        "registrationsOpen": edicion.inscripciones_abiertas,
        "registrationMessage": edicion.mensaje_inscripciones,
        "solidarityRegistration": edicion.url_dorsal_solidario,
        "version": edicion.version,
    }


def hay_destino(db: Session, url_dorsal: str) -> bool:
    """Dorsal válido o alguna prueba publicada (ficha más reciente publicada) con enlace."""
    if url_dorsal and url_externa_segura(url_dorsal):
        return True
    return any(p["registration"] for p in carreras.listar(db, privado=False))


def guardar(db: Session, entrada: InscripcionesEntrada) -> dict:
    vigente = evento.actual(db, bloquear=True)
    if vigente is None:
        db.rollback()
        raise NoEncontrado(SIN_EDICION)
    if entrada.version != vigente.version:
        db.rollback()
        raise Conflicto
    if entrada.registrationsOpen and not hay_destino(db, entrada.solidarityRegistration):
        db.rollback()
        raise AperturaSinDestinos(SIN_DESTINOS)
    vigente.inscripciones_abiertas = entrada.registrationsOpen
    vigente.mensaje_inscripciones = entrada.registrationMessage
    vigente.url_dorsal_solidario = entrada.solidarityRegistration
    vigente.version += 1
    db.commit()
    return a_contrato(vigente)
