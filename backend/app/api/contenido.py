"""Contrato transitorio de contenido (adaptador de lectura; DISCREPANCIAS M1)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.api.deps import SIN_SESION, requiere_escritura
from app.core.db import get_db
from app.services import contenido, sesiones

router = APIRouter(prefix="/api", tags=["contenido"])

SIN_PERSISTENCIA = "Esta sección del panel todavía no guarda cambios."


@router.get("/content")
async def obtener_contenido(
    request: Request, admin: str | None = None, db: Session = Depends(get_db)
) -> dict:
    semilla = request.app.state.contenido
    privado = admin is not None
    if (
        privado
        and await run_in_threadpool(sesiones.validar, db, request.cookies.get("penasagra_admin"))
        is None
    ):
        raise HTTPException(status_code=401, detail=SIN_SESION)
    datos = await run_in_threadpool(contenido.construir, db, semilla, privado)
    return {"data": datos, "revision": 0}


@router.put("/content", dependencies=[Depends(requiere_escritura)])
def guardar_contenido() -> None:
    # Las secciones aún no migradas no guardan: cada feature añade endpoints por recurso.
    raise HTTPException(status_code=501, detail=SIN_PERSISTENCIA)
