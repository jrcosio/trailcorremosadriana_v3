"""Metadatos de página para las plantillas de Caddy (contracts/meta-y-rutas de la feature 011)."""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services import meta

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/meta", response_class=PlainTextResponse)
def metadatos(
    request: Request, ruta: str = Query(max_length=300), db: Session = Depends(get_db)
) -> str:
    # Siempre 200: `httpInclude` de Caddy trata cualquier otro estado como un fallo de plantilla.
    datos = meta.resolver(db, ruta, request.app.state.settings.origen_publico)
    return meta.NO_ENCONTRADA if datos is None else meta.renderizar(datos)
