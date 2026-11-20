"""Gestión de clasificaciones (contracts/api-clasificaciones de la feature 006)."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import requiere_escritura
from app.core.db import get_db
from app.schemas.clasificaciones import ClasificacionEntrada, VistaPreviaEntrada
from app.services import clasificaciones
from app.services.sesiones import SesionValida

router = APIRouter(prefix="/api/admin/clasificaciones", tags=["clasificaciones"])
Identificador = Path(pattern=r"^[A-Za-z0-9_-]{1,100}$")


def _rechazo(exc: clasificaciones.ClasificacionRechazada) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.post("/vista-previa")
def vista_previa(
    entrada: VistaPreviaEntrada,
    sesion: SesionValida = Depends(requiere_escritura),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return clasificaciones.preparar(db, sesion.sesion_id, entrada)
    except clasificaciones.ClasificacionRechazada as exc:
        db.rollback()
        raise _rechazo(exc) from exc


@router.put("/{identificador}")
def guardar(
    entrada: ClasificacionEntrada,
    identificador: str = Identificador,
    sesion: SesionValida = Depends(requiere_escritura),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return clasificaciones.guardar(db, identificador, sesion.sesion_id, entrada)
    except clasificaciones.ClasificacionRechazada as exc:
        raise _rechazo(exc) from exc


@router.delete("/{identificador}", dependencies=[Depends(requiere_escritura)])
def borrar(
    identificador: str = Identificador, version: int = Query(ge=0), db: Session = Depends(get_db)
) -> dict:
    clasificaciones.borrar(db, identificador, version)
    return {"ok": True}
