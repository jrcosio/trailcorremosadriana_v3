"""Dependencias de seguridad: origen, sesión y comprobante CSRF.

Orden en escrituras (FR-013): origen (403) → sesión (401) → CSRF (403).
"""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import Settings, normalizar_origen
from app.core.db import get_db
from app.core.seguridad import huella, huellas_iguales
from app.services import sesiones
from app.services.sesiones import SesionValida

COOKIE_SESION = "penasagra_admin"
COOKIE_CSRF = "penasagra_csrf"
CABECERA_CSRF = "x-csrf-token"

SIN_SESION = "Sesión no válida o caducada."
ORIGEN_PROHIBIDO = "Origen no permitido."
CSRF_INVALIDO = "Comprobación de seguridad no válida. Recarga la página."


def ajustes(request: Request) -> Settings:
    return request.app.state.settings


def comprobar_origen(request: Request) -> None:
    origen = request.headers.get("origin")
    if not origen or normalizar_origen(origen) not in ajustes(request).origenes_validos:
        raise HTTPException(status_code=403, detail=ORIGEN_PROHIBIDO)


def requiere_origen(request: Request) -> None:
    comprobar_origen(request)


def sesion_actual(request: Request, db: Session = Depends(get_db)) -> SesionValida | None:
    return sesiones.validar(db, request.cookies.get(COOKIE_SESION))


def requiere_admin(sesion: SesionValida | None = Depends(sesion_actual)) -> SesionValida:
    if sesion is None:
        raise HTTPException(status_code=401, detail=SIN_SESION)
    return sesion


def comprobar_csrf(request: Request, sesion: SesionValida) -> None:
    enviado = request.headers.get(CABECERA_CSRF) or ""
    if not enviado or len(enviado) > 128 or not huellas_iguales(huella(enviado), sesion.csrf_hash):
        raise HTTPException(status_code=403, detail=CSRF_INVALIDO)


def requiere_escritura(request: Request, db: Session = Depends(get_db)) -> SesionValida:
    """Protección completa de una escritura autenticada, en el orden de FR-013."""
    comprobar_origen(request)
    sesion = sesiones.validar(db, request.cookies.get(COOKIE_SESION))
    if sesion is None:
        raise HTTPException(status_code=401, detail=SIN_SESION)
    comprobar_csrf(request, sesion)
    return sesion
