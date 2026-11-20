"""Contrato transitorio `SiteData` (GET /api/content).

Desde la feature 004, la edición, la fecha, el contador y las pruebas proceden de PostgreSQL. El
resto de secciones sigue saliendo de la semilla curada hasta su feature. En una base sin
inicializar (sin ediciones ni pruebas) se usa la semilla completa (comportamiento transitorio).
"""

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.schemas.contenido import SiteData

RUTA_SEMILLA = Path(__file__).resolve().parents[2] / "seed" / "contenido_inicial.json"
COLECCIONES = ("races", "news", "albums", "results", "sponsors", "collaborators")
registro = logging.getLogger(__name__)


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
    participantes = item.get("participants") or (len(filas) if isinstance(filas, list) else 0)
    return item.get("published") is True and not es_modalidad_solidaria(item) and participantes > 0


def filtrar_publicos(data: dict[str, Any]) -> dict[str, Any]:
    """Equivalente a `publicData` del frontend: solo elementos publicados."""
    for clave in COLECCIONES:
        if clave == "results":
            data[clave] = [i for i in data[clave] if _clasificacion_visible(i)]
        else:
            data[clave] = [i for i in data[clave] if i.get("published") is True]
    return data


def datos_publicos(contenido: SiteData) -> dict[str, Any]:
    return filtrar_publicos(contenido.model_dump(mode="json"))


def construir(db: Session, semilla: SiteData, privado: bool) -> dict[str, Any]:
    """`SiteData` con las secciones migradas leídas de la base de datos."""
    from app.services import (
        carreras,
        clasificaciones,
        entidades,
        evento,
        galeria,
        inscripciones,
        noticias,
    )  # diferida: evita ciclos

    data = semilla.model_dump(mode="json")
    if carreras.hay_datos(db):
        ev = evento.a_contrato(evento.actual(db))
        data["settings"].update(edition=ev["edition"], date=ev["date"], countdown=ev["countdown"])
        if (actual := evento.actual(db)) is not None:
            ins = inscripciones.a_contrato(actual)
            data["settings"].update(
                registrationsOpen=ins["registrationsOpen"],
                registrationMessage=ins["registrationMessage"],
                solidarityRegistration=ins["solidarityRegistration"],
            )
        if privado:
            data["settings"]["eventVersion"] = ev["version"]
        data["races"] = carreras.listar(db, privado=privado)
        data["results"] = clasificaciones.listar(db, privado=privado)
        data["news"] = noticias.listar(db, privado=privado)
        data["albums"] = galeria.listar(db, privado=privado)
        data["sponsors"] = entidades.listar(db, "patrocinador", privado=privado)
        data["collaborators"] = entidades.listar(db, "colaborador", privado=privado)
    else:
        registro.warning(
            "Base sin ediciones ni pruebas: se sirve la semilla (ejecuta importar-inicial)."
        )
    return data if privado else filtrar_publicos(data)
