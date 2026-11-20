"""Consulta pública de participantes (FR-008 de la feature 006)."""

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services import clasificaciones

router = APIRouter(prefix="/api/clasificaciones", tags=["clasificaciones"])


@router.get("/{identificador}/participantes")
def participantes(
    identificador: str = Path(pattern=r"^[A-Za-z0-9_-]{1,100}$"),
    q: str = Query(default="", max_length=100),
    categoria: str = Query(default="", max_length=150),
    sexo: str = Query(default="", max_length=60),
    pagina: int = Query(default=1, ge=1, le=10_000),
    db: Session = Depends(get_db),
) -> dict:
    return clasificaciones.consultar(db, identificador, q, categoria, sexo, pagina)
