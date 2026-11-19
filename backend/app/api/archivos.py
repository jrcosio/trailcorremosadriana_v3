"""Subida autenticada de archivos (contracts/api-archivos.openapi.yaml de la feature 003)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.formparsers import MultiPartException

from app.api.deps import ajustes, requiere_escritura
from app.core.db import get_db
from app.services.archivos import ArchivoRechazado, guardar_subida
from app.services.sesiones import SesionValida

router = APIRouter(prefix="/api", tags=["archivos"])

MARGEN_MULTIPART = 64 * 1024
BLOQUE = 1024 * 1024
SIN_ARCHIVO = "Selecciona un archivo."


def _limite_legible(maximo: int) -> str:
    return f"{maximo / 1_000_000:g} MB"


@router.post("/upload")
async def subir(
    request: Request,
    sesion: SesionValida = Depends(requiere_escritura),
    db: Session = Depends(get_db),
) -> dict:
    maximo = ajustes(request).upload_max_bytes
    demasiado_grande = HTTPException(
        status_code=413, detail=f"Máximo {_limite_legible(maximo)} por archivo."
    )
    longitud = request.headers.get("content-length")
    if longitud and longitud.isdigit() and int(longitud) > maximo + MARGEN_MULTIPART:
        raise demasiado_grande

    try:
        formulario = await request.form(max_files=2, max_fields=2)
    except (StarletteHTTPException, MultiPartException) as exc:  # demasiados campos o mal formado
        raise HTTPException(status_code=400, detail=SIN_ARCHIVO) from exc
    try:
        claves = list(formulario.keys())
        archivos = formulario.getlist("file")
        if claves != ["file"] or len(archivos) != 1 or not isinstance(archivos[0], UploadFile):
            raise HTTPException(status_code=400, detail=SIN_ARCHIVO)
        archivo = archivos[0]
        datos = bytearray()
        while bloque := await archivo.read(BLOQUE):
            datos.extend(bloque)
            if len(datos) > maximo:
                raise demasiado_grande
        nombre = archivo.filename
    finally:
        await formulario.close()

    if not datos:
        raise HTTPException(status_code=400, detail=SIN_ARCHIVO)
    try:
        guardado = await run_in_threadpool(
            guardar_subida,
            db,
            request.app.state.almacenamiento,
            bytes(datos),
            nombre,
            sesion.administrador_id,
        )
    except ArchivoRechazado as exc:
        raise HTTPException(status_code=exc.estado, detail=exc.mensaje) from exc
    return {"url": f"/media/{guardado.clave}"}
