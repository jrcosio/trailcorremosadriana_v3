"""Acceso, estado y cierre de la sesión de administración (contracts/api-administracion)."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import (
    COOKIE_CSRF,
    COOKIE_SESION,
    ajustes,
    comprobar_csrf,
    requiere_origen,
    sesion_actual,
)
from app.core.config import Settings
from app.core.db import get_db
from app.core.seguridad import (
    HASH_FICTICIO,
    PASSWORD_MAX,
    USUARIO_MAX,
    hash_password,
    huella,
    huellas_iguales,
    necesita_rehash,
    normalizar_usuario,
    verificar_password,
)
from app.services import administradores, clasificaciones, limites, sesiones
from app.services.sesiones import SesionValida

router = APIRouter(prefix="/api", tags=["sesion"])

CREDENCIALES_INCORRECTAS = "Usuario o contraseña incorrectos."
DEMASIADOS_INTENTOS = "Demasiados intentos. Espera unos minutos antes de volver a intentarlo."


class Credenciales(BaseModel):
    username: str = Field(max_length=256)
    password: str = Field(max_length=1024)


def _cookie(
    response: Response, nombre: str, valor: str, segundos: int, s: Settings, http_only: bool
) -> None:
    response.set_cookie(
        nombre,
        valor,
        max_age=segundos,
        path="/",
        secure=s.cookie_secure,
        httponly=http_only,
        samesite="strict",
    )


def _borrar_cookies(response: Response, s: Settings) -> None:
    for nombre, http_only in ((COOKIE_SESION, True), (COOKIE_CSRF, False)):
        response.delete_cookie(
            nombre, path="/", secure=s.cookie_secure, httponly=http_only, samesite="strict"
        )


def _ip_cliente(request: Request) -> str:
    # Uvicorn (--proxy-headers) ya resuelve la IP real a partir de X-Forwarded-For de Caddy.
    return request.client.host if request.client else "desconocido"


@router.post("/login", dependencies=[Depends(requiere_origen)])
def login(
    datos: Credenciales, request: Request, response: Response, db: Session = Depends(get_db)
) -> dict:
    s = ajustes(request)
    clave = huella(_ip_cliente(request))
    ventana = timedelta(minutes=s.login_ventana_minutos)

    espera = limites.segundos_de_bloqueo(db, clave, s.login_max_intentos, ventana)
    if espera:
        db.rollback()
        raise HTTPException(
            status_code=429, detail=DEMASIADOS_INTENTOS, headers={"Retry-After": str(espera)}
        )

    usuario = normalizar_usuario(datos.username)
    admin = administradores.buscar(db, usuario) if 0 < len(usuario) <= USUARIO_MAX else None
    if not datos.password or len(datos.password) > PASSWORD_MAX:
        correcto = False  # sin calcular el hash: evita abusar del coste de Argon2id
    elif admin is not None and admin.activo:
        correcto = verificar_password(admin.hash_password, datos.password)
    else:
        verificar_password(HASH_FICTICIO, datos.password)  # iguala el tiempo de respuesta
        correcto = False

    if not correcto or admin is None:
        limites.registrar_fallo(db, clave)
        db.commit()
        raise HTTPException(status_code=401, detail=CREDENCIALES_INCORRECTAS)

    if necesita_rehash(admin.hash_password):
        admin.hash_password = hash_password(datos.password)
    admin.ultimo_acceso_en = datetime.now(UTC)
    limites.reiniciar(db, clave)
    limites.limpiar_caducados(db, ventana)
    sesiones.limpiar_antiguas(db)
    clasificaciones.limpiar_caducadas(db)
    token, csrf, _ = sesiones.crear(db, admin, s.session_hours)
    db.commit()

    segundos = s.session_hours * 3600
    _cookie(response, COOKIE_SESION, token, segundos, s, http_only=True)
    _cookie(response, COOKIE_CSRF, csrf, segundos, s, http_only=False)
    return {"ok": True, "usuario": admin.usuario}


@router.get("/session")
def estado_sesion(
    request: Request,
    response: Response,
    sesion: SesionValida | None = Depends(sesion_actual),
    db: Session = Depends(get_db),
) -> dict:
    if sesion is None:
        return {"authenticated": False}
    actual = request.cookies.get(COOKIE_CSRF) or ""
    if not actual or not huellas_iguales(huella(actual), sesion.csrf_hash):
        csrf = sesiones.renovar_csrf(db, sesion.sesion_id)
        restante = max(1, int((sesion.expira_en - datetime.now(UTC)).total_seconds()))
        _cookie(response, COOKIE_CSRF, csrf, restante, ajustes(request), http_only=False)
    return {"authenticated": True, "usuario": sesion.usuario}


@router.post("/logout", dependencies=[Depends(requiere_origen)])
def logout(
    request: Request,
    response: Response,
    sesion: SesionValida | None = Depends(sesion_actual),
    db: Session = Depends(get_db),
) -> dict:
    if sesion is not None:
        comprobar_csrf(request, sesion)
        sesiones.revocar(db, sesion.sesion_id)
    _borrar_cookies(response, ajustes(request))
    return {"ok": True}
