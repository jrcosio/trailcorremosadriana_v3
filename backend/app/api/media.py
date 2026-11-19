"""Entrega pública de archivos subidos (FR-008/FR-009 de la feature 003)."""

import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.db import get_db
from app.services.archivos import obtener

router = APIRouter(tags=["media"])

NO_ENCONTRADO = "Archivo no encontrado."
CACHE = "public, max-age=31536000, immutable"
CSP = "default-src 'none'; sandbox"
NOMBRE_SEGURO = re.compile(r"[^A-Za-z0-9._-]+")


def _disposicion(tipo: str, nombre: str | None, clave: str) -> str:
    if tipo != "application/gpx+xml":
        return "inline"
    base = NOMBRE_SEGURO.sub("-", (nombre or "").rsplit(".", 1)[0]).strip("-.")[:80]
    return f'attachment; filename="{base or "recorrido-" + clave[:8]}.gpx"'


@router.api_route("/media/{clave}", methods=["GET", "HEAD"])
async def entregar(clave: str, request: Request, db: Session = Depends(get_db)) -> Response:
    archivo = await run_in_threadpool(obtener, db, clave)
    if archivo is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    etag = f'"{archivo.sha256}"'
    cabeceras = {
        "Cache-Control": CACHE,
        "ETag": etag,
        "Content-Security-Policy": CSP,
        "X-Content-Type-Options": "nosniff",
        "Content-Disposition": _disposicion(archivo.tipo, archivo.nombre_original, clave),
    }
    solicitadas = [
        e.strip().removeprefix("W/") for e in request.headers.get("if-none-match", "").split(",")
    ]
    if etag in solicitadas:
        return Response(
            status_code=304, headers={k: cabeceras[k] for k in ("Cache-Control", "ETag")}
        )
    datos = await run_in_threadpool(request.app.state.almacenamiento.leer, clave)
    if datos is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return Response(content=datos, media_type=archivo.tipo, headers=cabeceras)


@router.get("/media/{resto:path}", include_in_schema=False)
async def ruta_no_valida(resto: str) -> Response:
    # Rutas con barras o codificaciones extrañas: mismo 404 genérico, sin detalles internos.
    raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
