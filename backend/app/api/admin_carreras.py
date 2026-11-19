"""Pruebas y datos por edición (contracts/api-evento-carreras de la feature 004)."""

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.evento import CarreraEntrada
from app.services import carreras

router = APIRouter(
    prefix="/api/admin", tags=["carreras"], dependencies=[Depends(requiere_escritura)]
)

Identificador = Path(pattern=r"^[A-Za-z0-9_-]{1,100}$")


@router.put("/carreras/{slug}")
def guardar(
    entrada: CarreraEntrada, slug: str = Identificador, db: Session = Depends(get_db)
) -> dict:
    return carreras.guardar(db, slug, entrada)


@router.delete("/carreras/{slug}")
def borrar(
    slug: str = Identificador, version: int = Query(ge=0), db: Session = Depends(get_db)
) -> dict:
    carreras.borrar(db, slug, version)
    return {"ok": True}
