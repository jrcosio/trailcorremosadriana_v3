"""Sesión del administrador: hasta la feature 002 no hay autenticación disponible.

`/api/session` informa de que no hay sesión y `/api/login` responde 503 sin conceder acceso
ni emitir cookies (FR-019). La feature 002 sustituye este módulo.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["sesion"])


@router.get("/session")
def sesion() -> dict:
    return {"authenticated": False}


@router.post("/login")
def login() -> None:
    raise HTTPException(
        status_code=503, detail="El acceso de administración todavía no está disponible."
    )
