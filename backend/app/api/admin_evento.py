"""Edición actual, fecha y contador (contracts/api-evento-carreras de la feature 004)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import requiere_admin, requiere_escritura
from app.core.db import get_db
from app.schemas.evento import EventoEntrada
from app.services import evento

router = APIRouter(prefix="/api/admin", tags=["evento"])


@router.get("/evento", dependencies=[Depends(requiere_admin)])
def leer(db: Session = Depends(get_db)) -> dict:
    return evento.a_contrato(evento.actual(db))


@router.put("/evento", dependencies=[Depends(requiere_escritura)])
def guardar(entrada: EventoEntrada, db: Session = Depends(get_db)) -> dict:
    return evento.guardar(db, entrada)
