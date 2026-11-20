"""Contrato de contenido de solo lectura (DISCREPANCIAS M1).

Desde la feature 010 no hay guardado del documento completo: el panel guarda por recursos.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.api.deps import SIN_SESION
from app.core.db import get_db
from app.services import contenido, sesiones

router = APIRouter(prefix="/api", tags=["contenido"])


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
