"""Álbumes y fotografías con versión; retirar o quitar fotos no borra archivos (feature 008)."""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Album, Fotografia
from app.schemas.galeria import AlbumEntrada
from app.services.errores import Conflicto, NoEncontrado

NO_EXISTE = "El álbum no existe."


def alt_por_defecto(titulo: str, n: int) -> str:
    return f"{titulo} · fotografía {n}"[:250]


def a_item(a: Album, privado: bool) -> dict:
    item = {
        "id": a.slug,
        "title": a.titulo,
        "year": str(a.anio),
        "image": a.portada,
        "url": a.url_externa,
        "photos": [f.imagen for f in a.fotografias],
        "photoAlts": [f.alt for f in a.fotografias],
        "published": a.publicado,
    }
    if privado:
        item["version"] = a.version
    return item


def listar(db: Session, privado: bool) -> list[dict]:
    consulta = (
        select(Album)
        .options(selectinload(Album.fotografias))
        .order_by(Album.anio.desc(), Album.orden, Album.id)
    )
    if not privado:
        consulta = consulta.where(Album.publicado.is_(True))
    return [a_item(a, privado) for a in db.scalars(consulta)]


def guardar(db: Session, slug: str, entrada: AlbumEntrada) -> dict:
    album = db.scalar(select(Album).where(Album.slug == slug).with_for_update())
    if entrada.version != (album.version if album else 0):
        db.rollback()
        raise Conflicto
    if album is None:
        orden = (db.scalar(select(func.max(Album.orden))) or 0) + 1
        album = Album(slug=slug, orden=orden, version=0)
        db.add(album)
    album.titulo, album.anio, album.portada = entrada.title, int(entrada.year), entrada.image
    album.url_externa, album.publicado = entrada.url, entrada.published
    album.version += 1
    db.flush()
    # La lista de fotos se sustituye en la misma transacción; los archivos no se borran (FR-004).
    db.execute(delete(Fotografia).where(Fotografia.album_id == album.id))
    db.flush()
    for i, imagen in enumerate(entrada.photos):
        db.add(
            Fotografia(
                album_id=album.id, imagen=imagen, alt=alt_por_defecto(entrada.title, i + 1), orden=i
            )
        )
    db.commit()
    db.refresh(album)
    return a_item(
        db.scalar(
            select(Album).options(selectinload(Album.fotografias)).where(Album.id == album.id)
        ),
        True,
    )


def borrar(db: Session, slug: str, version: int) -> None:
    album = db.scalar(select(Album).where(Album.slug == slug).with_for_update())
    if album is None:
        raise NoEncontrado(NO_EXISTE)
    if album.version != version:
        db.rollback()
        raise Conflicto
    db.delete(album)
    db.commit()
