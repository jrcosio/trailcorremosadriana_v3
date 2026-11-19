"""Apertura de inscripciones y Dorsal Solidario (contracts/api-inscripciones de la feature 005)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import requiere_admin, requiere_escritura
from app.core.db import get_db
from app.schemas.evento import InscripcionesEntrada
from app.services import evento, inscripciones

router = APIRouter(prefix="/api/admin", tags=["inscripciones"])


@router.get("/inscripciones", dependencies=[Depends(requiere_admin)])
def leer(db: Session = Depends(get_db)) -> dict:
    return inscripciones.a_contrato(evento.actual(db))


@router.put("/inscripciones", dependencies=[Depends(requiere_escritura)])
def guardar(entrada: InscripcionesEntrada, db: Session = Depends(get_db)) -> dict:
    try:
        return inscripciones.guardar(db, entrada)
    except inscripciones.AperturaSinDestinos as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
