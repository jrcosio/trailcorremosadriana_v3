"""Reglamento de la edición actual (contracts/api-reglamento-contacto de la feature 010)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.reglamento import ReglamentoEntrada
from app.services import reglamento

router = APIRouter(prefix="/api/admin", tags=["reglamento"])


@router.put("/reglamento", dependencies=[Depends(requiere_escritura)])
def guardar(entrada: ReglamentoEntrada, db: Session = Depends(get_db)) -> dict:
    return reglamento.guardar(db, entrada)
