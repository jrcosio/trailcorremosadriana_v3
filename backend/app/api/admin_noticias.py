"""Gestión de noticias (contracts/api-noticias de la feature 007)."""

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.noticias import NoticiaEntrada
from app.services import noticias

router = APIRouter(
    prefix="/api/admin/noticias", tags=["noticias"], dependencies=[Depends(requiere_escritura)]
)
Identificador = Path(pattern=r"^[A-Za-z0-9_-]{1,100}$")


@router.put("/{slug}")
def guardar(
    entrada: NoticiaEntrada, slug: str = Identificador, db: Session = Depends(get_db)
) -> dict:
    return noticias.guardar(db, slug, entrada)


@router.delete("/{slug}")
def borrar(
    slug: str = Identificador, version: int = Query(ge=0), db: Session = Depends(get_db)
) -> dict:
    noticias.borrar(db, slug, version)
    return {"ok": True}
