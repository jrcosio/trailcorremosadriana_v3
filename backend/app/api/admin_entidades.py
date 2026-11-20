"""Gestión de patrocinadores y colaboradores (contracts/api-entidades de la feature 009)."""

from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.entidades import EntidadEntrada
from app.services import entidades

router = APIRouter(
    prefix="/api/admin/entidades", tags=["entidades"], dependencies=[Depends(requiere_escritura)]
)
Seccion = Literal["patrocinadores", "colaboradores"]
Identificador = Path(pattern=r"^[A-Za-z0-9_-]{1,100}$")


@router.put("/{seccion}/{slug}")
def guardar(
    entrada: EntidadEntrada,
    seccion: Seccion,
    slug: str = Identificador,
    db: Session = Depends(get_db),
) -> dict:
    return entidades.guardar(db, entidades.SECCIONES[seccion], slug, entrada)


@router.delete("/{seccion}/{slug}")
def borrar(
    seccion: Seccion,
    slug: str = Identificador,
    version: int = Query(ge=0),
    db: Session = Depends(get_db),
) -> dict:
    entidades.borrar(db, entidades.SECCIONES[seccion], slug, version)
    return {"ok": True}
