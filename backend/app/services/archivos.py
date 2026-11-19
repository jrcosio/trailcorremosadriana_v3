"""Validación, guardado y consulta de archivos subidos (feature 003)."""

import hashlib
import re
import unicodedata
import uuid
from dataclasses import dataclass

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import ParseError, fromstring
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Archivo
from app.storage import Almacenamiento

EXTENSIONES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
    "application/gpx+xml": "gpx",
}
PATRON_CLAVE = re.compile(r"^[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$")
TIPO_NO_ADMITIDO = "Sube imágenes JPG, PNG o WebP, documentos PDF o rutas GPX."


@dataclass
class ArchivoRechazado(Exception):
    mensaje: str
    estado: int = 400


def es_gpx(datos: bytes) -> bool:
    """XML bien formado con raíz `gpx`, sin DTD, entidades ni referencias externas."""
    inicio = datos.removeprefix(b"\xef\xbb\xbf").lstrip()
    if not inicio.startswith(b"<"):
        return False
    try:
        raiz = fromstring(datos, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except (ParseError, DefusedXmlException, ValueError):
        return False
    return raiz.tag.rsplit("}", 1)[-1] == "gpx"


def detectar_tipo(datos: bytes) -> str | None:
    """Tipo por contenido real (bytes mágicos); None si no es un tipo admitido."""
    if datos.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(datos) >= 12 and datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"
    if datos.startswith(b"%PDF-"):
        return "application/pdf"
    if es_gpx(datos):
        return "application/gpx+xml"
    return None


def sanear_nombre(nombre: str | None) -> str | None:
    """Solo el nombre base, sin caracteres de control y con 255 caracteres como máximo."""
    if not nombre:
        return None
    base = re.split(r"[\\/]", nombre)[-1]
    limpio = "".join(c for c in base if unicodedata.category(c)[0] != "C").strip()
    if not limpio:
        return None
    if len(limpio) > 255:
        raiz, punto, ext = limpio.rpartition(".")
        limpio = (
            (raiz[: 255 - len(ext) - 1] + punto + ext) if punto and len(ext) <= 10 else limpio[:255]
        )
    return limpio


def guardar_subida(
    db: Session,
    almacenamiento: Almacenamiento,
    datos: bytes,
    nombre: str | None,
    administrador_id: int,
) -> Archivo:
    """Valida, guarda el objeto y después registra la fila (nunca una fila sin objeto)."""
    tipo = detectar_tipo(datos)
    if tipo is None:
        raise ArchivoRechazado(TIPO_NO_ADMITIDO)
    clave = f"{uuid.uuid4().hex}.{EXTENSIONES[tipo]}"
    almacenamiento.guardar(clave, datos, tipo)  # AlmacenamientoNoDisponible → 503
    archivo = Archivo(
        clave=clave,
        tipo=tipo,
        tamano=len(datos),
        sha256=hashlib.sha256(datos).hexdigest(),
        nombre_original=sanear_nombre(nombre),
        subido_por=administrador_id,
    )
    db.add(archivo)
    db.commit()
    return archivo


def obtener(db: Session, clave: str) -> Archivo | None:
    if not PATRON_CLAVE.match(clave):
        return None
    return db.scalar(select(Archivo).where(Archivo.clave == clave))
