"""Contrato transitorio de contenido (adaptador de solo lectura; DISCREPANCIAS M1)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import SIN_SESION, requiere_escritura
from app.core.db import get_db
from app.services import sesiones
from app.services.contenido import datos_publicos

router = APIRouter(prefix="/api", tags=["contenido"])

SIN_PERSISTENCIA = "Esta sección del panel todavía no guarda cambios."


@router.get("/content")
def obtener_contenido(
    request: Request, admin: str | None = None, db: Session = Depends(get_db)
) -> dict:
    contenido = request.app.state.contenido
    if admin is None:
        return {"data": datos_publicos(contenido), "revision": 0}
    # Variante privada: requiere sesión e incluye borradores (FR-016 de la feature 002).
    if sesiones.validar(db, request.cookies.get("penasagra_admin")) is None:
        raise HTTPException(status_code=401, detail=SIN_SESION)
    return {"data": contenido.model_dump(mode="json"), "revision": 0}


@router.put("/content", dependencies=[Depends(requiere_escritura)])
def guardar_contenido() -> None:
    # La edición por documento completo no existe: cada feature añade endpoints por recurso.
    raise HTTPException(status_code=501, detail=SIN_PERSISTENCIA)
