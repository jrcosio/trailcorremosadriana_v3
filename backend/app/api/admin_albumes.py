"""Gestión de álbumes (contracts/api-galeria de la feature 008)."""

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.galeria import AlbumEntrada
from app.services import galeria

router = APIRouter(
    prefix="/api/admin/albumes", tags=["galeria"], dependencies=[Depends(requiere_escritura)]
)
Identificador = Path(pattern=r"^[A-Za-z0-9_-]{1,100}$")


@router.put("/{slug}")
def guardar(
    entrada: AlbumEntrada, slug: str = Identificador, db: Session = Depends(get_db)
) -> dict:
    return galeria.guardar(db, slug, entrada)


@router.delete("/{slug}")
def borrar(
    slug: str = Identificador, version: int = Query(ge=0), db: Session = Depends(get_db)
) -> dict:
    galeria.borrar(db, slug, version)
    return {"ok": True}
