"""Patrocinadores y colaboradores con versión; cada sección es independiente (feature 009)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Entidad
from app.schemas.entidades import EntidadEntrada
from app.services.errores import Conflicto, NoEncontrado

SECCIONES = {"patrocinadores": "patrocinador", "colaboradores": "colaborador"}
NO_EXISTE = "La entidad no existe."


def a_item(e: Entidad, privado: bool) -> dict:
    item = {
        "id": e.slug,
        "name": e.nombre,
        "image": e.logo,
        "url": e.web,
        "order": e.orden,
        "published": e.publicada,
    }
    if privado:
        item["version"] = e.version
    return item


def listar(db: Session, tipo: str, privado: bool) -> list[dict]:
    consulta = (
        select(Entidad)
        .where(Entidad.tipo == tipo)
        .order_by(Entidad.orden, Entidad.creado_en, Entidad.id)
    )
    if not privado:
        consulta = consulta.where(Entidad.publicada.is_(True))
    return [a_item(e, privado) for e in db.scalars(consulta)]


def _buscar(db: Session, tipo: str, slug: str) -> Entidad | None:
    return db.scalar(
        select(Entidad).where(Entidad.tipo == tipo, Entidad.slug == slug).with_for_update()
    )


def guardar(db: Session, tipo: str, slug: str, entrada: EntidadEntrada) -> dict:
    entidad = _buscar(db, tipo, slug)
    if entrada.version != (entidad.version if entidad else 0):
        db.rollback()
        raise Conflicto
    if entidad is None:
        entidad = Entidad(tipo=tipo, slug=slug, version=0)
        db.add(entidad)
    entidad.nombre, entidad.logo, entidad.web = entrada.name, entrada.image, entrada.url
    entidad.orden, entidad.publicada = entrada.order, entrada.published
    entidad.version += 1
    db.commit()
    return a_item(entidad, privado=True)


def borrar(db: Session, tipo: str, slug: str, version: int) -> None:
    entidad = _buscar(db, tipo, slug)
    if entidad is None:
        raise NoEncontrado(NO_EXISTE)
    if entidad.version != version:
        db.rollback()
        raise Conflicto
    db.delete(entidad)
    db.commit()
