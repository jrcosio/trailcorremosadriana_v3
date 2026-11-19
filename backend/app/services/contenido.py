"""Contenido público transitorio servido desde la semilla curada (backend/seed)."""

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from app.schemas.contenido import SiteData

RUTA_SEMILLA = Path(__file__).resolve().parents[2] / "seed" / "contenido_inicial.json"
COLECCIONES = ("races", "news", "albums", "results", "sponsors", "collaborators")


def cargar_contenido(ruta: Path = RUTA_SEMILLA) -> SiteData:
    """Lee y valida la semilla. Un error de validación impide arrancar el servicio."""
    return SiteData.model_validate(json.loads(ruta.read_text(encoding="utf-8")))


def _normalizar(valor: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", valor)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", sin_tildes.lower())


def es_modalidad_solidaria(item: dict[str, Any]) -> bool:
    """Misma regla que `isSolidarityRace` del frontend (DISCREPANCIAS M4)."""
    return any(
        "solidari" in _normalizar(str(item.get(campo) or ""))
        for campo in ("id", "title", "race", "raceId")
    )


def _clasificacion_visible(item: dict[str, Any]) -> bool:
    filas = item.get("rows")
    return (
        item.get("published") is True
        and not es_modalidad_solidaria(item)
        and isinstance(filas, list)
        and len(filas) > 0
    )


def datos_publicos(contenido: SiteData) -> dict[str, Any]:
    """Equivalente a `publicData` del frontend: solo elementos publicados."""
    data = contenido.model_dump(mode="json")
    for clave in COLECCIONES:
        if clave == "results":
            data[clave] = [i for i in data[clave] if _clasificacion_visible(i)]
        else:
            data[clave] = [i for i in data[clave] if i.get("published") is True]
    return data
