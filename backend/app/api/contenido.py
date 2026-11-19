"""Contrato transitorio de contenido (adaptador de solo lectura; DISCREPANCIAS M1)."""

from fastapi import APIRouter, HTTPException, Request

from app.services.contenido import datos_publicos

router = APIRouter(prefix="/api", tags=["contenido"])


@router.get("/content")
def obtener_contenido(request: Request, admin: str | None = None) -> dict:
    if admin is not None:
        # La variante con borradores requiere sesión de administrador (feature 002).
        raise HTTPException(status_code=401, detail="Sesión no válida o caducada.")
    return {"data": datos_publicos(request.app.state.contenido), "revision": 0}
