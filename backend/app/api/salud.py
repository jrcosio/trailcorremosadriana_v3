"""Comprobaciones de salud (proceso vivo) y disponibilidad (base + esquema)."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.esquema import EstadoEsquema, estado_esquema

router = APIRouter(prefix="/api", tags=["salud"])


@router.get("/health")
def salud() -> dict:
    return {"estado": "viva"}


@router.get("/ready")
def disponibilidad(request: Request) -> JSONResponse:
    estado = estado_esquema(request.app.state.engine)
    if estado is EstadoEsquema.DISPONIBLE:
        return JSONResponse({"estado": "disponible"})
    return JSONResponse({"estado": "no_disponible", "motivo": estado.value}, status_code=503)
