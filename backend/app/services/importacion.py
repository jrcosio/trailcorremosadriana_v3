"""Importación idempotente de los datos aprobados (FR-010 de la feature 004).

Solo actúa sobre las partes vacías y nunca sobrescribe datos existentes sin `reemplazar=True`.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Album, Carrera, CarreraEdicion, Edicion, Noticia
from app.services.contenido import RUTA_SEMILLA
from app.services.fechas import MADRID

# Fecha oficial de la edición 2026 (web de producción): sábado 11/07/2026, salida a las 09:00.
FECHA_2026 = datetime(2026, 7, 11, 9, 0, tzinfo=MADRID)
RUTA_NOTICIAS = RUTA_SEMILLA.parent / "noticias"


def _semilla(ruta: Path = RUTA_SEMILLA) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def importar(db: Session, reemplazar: bool = False, ruta: Path = RUTA_SEMILLA) -> list[str]:
    """Devuelve la lista de acciones realizadas (vacía si no había nada que hacer)."""
    acciones: list[str] = []
    semilla = _semilla(ruta)
    if reemplazar:
        db.execute(delete(CarreraEdicion))
        db.execute(delete(Carrera))
        db.execute(delete(Edicion))
        acciones.append("Datos de evento y pruebas eliminados para reemplazarlos.")

    if not db.scalar(select(func.count(Edicion.id))):
        actual = int(semilla["settings"]["edition"])
        db.add(
            Edicion(
                anio=2026, fecha_hora=FECHA_2026, mostrar_contador=False, es_actual=False, version=1
            )
        )
        db.add(
            Edicion(
                anio=actual,
                fecha_hora=None,
                mostrar_contador=bool(semilla["settings"].get("countdown", True)),
                es_actual=True,
                version=1,
            )
        )
        db.flush()
        acciones.append(
            f"Ediciones creadas: 2026 (11/07/2026 09:00) y {actual} (actual, sin fecha)."
        )

    # Inscripciones de la edición actual (feature 005): solo si siguen en sus valores por defecto.
    actual = db.scalar(select(Edicion).where(Edicion.es_actual.is_(True)))
    if (
        actual is not None
        and not actual.inscripciones_abiertas
        and actual.mensaje_inscripciones == ""
        and actual.url_dorsal_solidario == ""
    ):
        ajustes = semilla["settings"]
        actual.inscripciones_abiertas = bool(ajustes.get("registrationsOpen", False))
        actual.mensaje_inscripciones = ajustes.get("registrationMessage", "")
        actual.url_dorsal_solidario = ajustes.get("solidarityRegistration", "")
        if actual.mensaje_inscripciones:
            acciones.append(
                "Inscripciones de la edición actual: cerradas, con el mensaje de la semilla."
            )

    if not db.scalar(select(func.count(Carrera.id))):
        ediciones = {e.anio: e for e in db.scalars(select(Edicion))}
        for orden, r in enumerate(semilla["races"]):
            anio = int(r["edition"])
            if anio not in ediciones:
                ediciones[anio] = Edicion(anio=anio, es_actual=False, version=1)
                db.add(ediciones[anio])
                db.flush()
            carrera = Carrera(
                slug=r["id"],
                nombre=r["title"],
                etiqueta=r.get("label", ""),
                color=r.get("color", ""),
                orden=orden,
            )
            db.add(carrera)
            db.add(
                CarreraEdicion(
                    carrera=carrera,
                    edicion=ediciones[anio],
                    km=Decimal(str(r["km"])),
                    desnivel=int(r["elevation"]),
                    precio=r["price"],
                    hora_salida=r.get("start", ""),
                    terreno=r.get("terrain", ""),
                    descripcion=r.get("description", ""),
                    avituallamientos=r.get("aid", ""),
                    imagen=r["image"],
                    ruta=r.get("route", ""),
                    wikiloc=r.get("wikiloc", ""),
                    gpx=r.get("gpx", ""),
                    url_inscripcion=r.get("registration", ""),
                    publicada=bool(r.get("published", False)),
                    version=1,
                )
            )
        acciones.append(
            "Pruebas creadas con sus datos de referencia: "
            + ", ".join(r["id"] for r in semilla["races"])
            + "."
        )
    if not db.scalar(select(func.count(Noticia.id))):
        # Orden de alta: primero la de producción y después la de la semilla (misma fecha de orden).
        produccion = json.loads(
            (RUTA_NOTICIAS / "2026-07-13-gracias-trail-2026.json").read_text("utf-8")
        )
        for n in [produccion, *semilla["news"]]:
            db.add(
                Noticia(
                    slug=n["id"],
                    titulo=n["title"],
                    categoria=n.get("category", ""),
                    fecha=date.fromisoformat(n["date"]) if n.get("date") else None,
                    imagen=n.get("image", ""),
                    extracto=n.get("excerpt", ""),
                    cuerpo=n["body"],
                    publicada=bool(n.get("published", False)),
                    version=1,
                )
            )
            db.flush()
        acciones.append("Noticias importadas: gracias-trail-2026 (producción) y la de la semilla.")
    if not db.scalar(select(func.count(Album.id))):
        for orden, a in enumerate(semilla["albums"]):
            db.add(
                Album(
                    slug=a["id"],
                    titulo=a["title"],
                    anio=int(a["year"]),
                    portada=a["image"],
                    url_externa=a.get("url", ""),
                    publicado=bool(a.get("published", False)),
                    orden=orden,
                    version=1,
                )
            )
        acciones.append("Álbumes históricos importados con sus enlaces de Google Fotos.")
    db.commit()
    return acciones
