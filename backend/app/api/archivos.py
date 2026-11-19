"""Subida de archivos: llega en la feature 003. Hasta entonces, protegida y sin efecto."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.contenido import SIN_PERSISTENCIA
from app.api.deps import requiere_escritura

router = APIRouter(prefix="/api", tags=["archivos"])


@router.post("/upload", dependencies=[Depends(requiere_escritura)])
def subir() -> None:
    raise HTTPException(status_code=501, detail=SIN_PERSISTENCIA)
