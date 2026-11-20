"""Datos de contacto (contracts/api-reglamento-contacto de la feature 010)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.contacto import ContactoEntrada
from app.services import contacto

router = APIRouter(prefix="/api/admin", tags=["contacto"])


@router.put("/contacto", dependencies=[Depends(requiere_escritura)])
def guardar(entrada: ContactoEntrada, db: Session = Depends(get_db)) -> dict:
    return contacto.guardar(db, entrada)
