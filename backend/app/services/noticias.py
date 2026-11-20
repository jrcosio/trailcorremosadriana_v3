"""Noticias con borradores, orden explícito y control de versión (feature 007)."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Noticia
from app.schemas.noticias import NoticiaEntrada
from app.services.errores import Conflicto, NoEncontrado

NO_EXISTE = "La noticia no existe."


def a_item(n: Noticia, privado: bool) -> dict:
    item = {
        "id": n.slug,
        "title": n.titulo,
        "category": n.categoria,
        "date": n.fecha.isoformat() if n.fecha else "",
        "image": n.imagen,
        "excerpt": n.extracto,
        "body": n.cuerpo,
        "published": n.publicada,
    }
    if privado:
        item["version"] = n.version
    return item


def listar(db: Session, privado: bool) -> list[dict]:
    consulta = select(Noticia).order_by(
        Noticia.fecha.desc().nulls_first(), Noticia.creado_en.desc(), Noticia.id.desc()
    )
    if not privado:
        consulta = consulta.where(Noticia.publicada.is_(True))
    return [a_item(n, privado) for n in db.scalars(consulta)]


def guardar(db: Session, slug: str, entrada: NoticiaEntrada) -> dict:
    noticia = db.scalar(select(Noticia).where(Noticia.slug == slug).with_for_update())
    if entrada.version != (noticia.version if noticia else 0):
        db.rollback()
        raise Conflicto
    if noticia is None:
        noticia = Noticia(slug=slug, version=0)
        db.add(noticia)
    noticia.titulo, noticia.categoria = entrada.title, entrada.category
    noticia.fecha = date.fromisoformat(entrada.date) if entrada.date else None
    noticia.imagen, noticia.extracto, noticia.cuerpo = entrada.image, entrada.excerpt, entrada.body
    noticia.publicada = entrada.published
    noticia.version += 1
    db.commit()
    return a_item(noticia, privado=True)


def borrar(db: Session, slug: str, version: int) -> None:
    noticia = db.scalar(select(Noticia).where(Noticia.slug == slug).with_for_update())
    if noticia is None:
        raise NoEncontrado(NO_EXISTE)
    if noticia.version != version:
        db.rollback()
        raise Conflicto
    db.delete(noticia)
    db.commit()
