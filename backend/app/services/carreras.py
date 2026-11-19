"""Pruebas y sus datos por edición (FR-004–009 de la feature 004)."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import Carrera, CarreraEdicion, Edicion
from app.schemas.evento import CarreraEntrada
from app.services import evento
from app.services.errores import Conflicto, NoEncontrado

CON_CLASIFICACIONES = "No se puede borrar una prueba con clasificaciones."


def _numero(valor: Decimal) -> str:
    texto = format(valor.normalize(), "f")
    return texto.rstrip("0").rstrip(".") if "." in texto else texto


def _fichas_ordenadas(carrera: Carrera) -> list[CarreraEdicion]:
    return sorted(carrera.fichas, key=lambda f: f.edicion.anio, reverse=True)


def a_item(carrera: Carrera, ficha: CarreraEdicion, privado: bool = False) -> dict:
    item = {
        "id": carrera.slug,
        "title": carrera.nombre,
        "label": carrera.etiqueta,
        "km": _numero(ficha.km),
        "elevation": str(ficha.desnivel),
        "price": ficha.precio,
        "image": ficha.imagen,
        "color": carrera.color,
        "description": ficha.descripcion,
        "terrain": ficha.terreno,
        "start": ficha.hora_salida,
        "route": ficha.ruta,
        "wikiloc": ficha.wikiloc,
        "gpx": ficha.gpx,
        "registration": ficha.url_inscripcion,
        "edition": str(ficha.edicion.anio),
        "aid": ficha.avituallamientos,
        "published": ficha.publicada,
    }
    if privado:
        item["version"] = ficha.version
    return item


def _cargar(db: Session):
    return select(Carrera).options(
        selectinload(Carrera.fichas).selectinload(CarreraEdicion.edicion)
    )


def listar(db: Session, privado: bool) -> list[dict]:
    """Pública: ficha publicada más reciente. Privada: ficha más reciente (cualquier estado)."""
    items = []
    for carrera in db.scalars(_cargar(db).order_by(Carrera.orden, Carrera.id)):
        fichas = _fichas_ordenadas(carrera)
        if not privado:
            fichas = [f for f in fichas if f.publicada]
        if fichas:
            items.append(a_item(carrera, fichas[0], privado))
    return items


def guardar(db: Session, slug: str, entrada: CarreraEntrada) -> dict:
    carrera = db.scalar(_cargar(db).where(Carrera.slug == slug).with_for_update(of=Carrera))
    vigente = _fichas_ordenadas(carrera)[0] if carrera and carrera.fichas else None
    if entrada.version != (vigente.version if vigente else 0):
        db.rollback()
        raise Conflicto
    if carrera is None:
        orden = (db.scalar(select(func.max(Carrera.orden))) or 0) + 1
        carrera = Carrera(slug=slug, orden=orden, nombre=entrada.title)
        db.add(carrera)
        db.flush()
    carrera.nombre, carrera.etiqueta, carrera.color = entrada.title, entrada.label, entrada.color

    edicion = evento.obtener_o_crear(db, int(entrada.edition))
    ficha = next((f for f in carrera.fichas if f.edicion_id == edicion.id), None)
    if ficha is None:
        ficha = CarreraEdicion(carrera=carrera, edicion=edicion, version=0)
        db.add(ficha)
    ficha.km, ficha.desnivel, ficha.precio = entrada.km, entrada.elevation, entrada.price
    ficha.hora_salida, ficha.terreno, ficha.descripcion = (
        entrada.start,
        entrada.terrain,
        entrada.description,
    )
    ficha.avituallamientos, ficha.imagen, ficha.ruta = entrada.aid, entrada.image, entrada.route
    ficha.wikiloc, ficha.gpx, ficha.url_inscripcion = (
        entrada.wikiloc,
        entrada.gpx,
        entrada.registration,
    )
    ficha.publicada = entrada.published
    ficha.version = (ficha.version or 0) + 1
    db.commit()
    db.refresh(carrera)
    mostrada = _fichas_ordenadas(carrera)[0]
    return a_item(carrera, mostrada, privado=True)


def borrar(db: Session, slug: str, version: int) -> None:
    carrera = db.scalar(_cargar(db).where(Carrera.slug == slug).with_for_update(of=Carrera))
    if carrera is None:
        raise NoEncontrado
    vigente = _fichas_ordenadas(carrera)[0] if carrera.fichas else None
    if version != (vigente.version if vigente else 0):
        db.rollback()
        raise Conflicto
    db.delete(carrera)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto(CON_CLASIFICACIONES) from exc


def hay_datos(db: Session) -> bool:
    return bool(
        db.scalar(select(func.count(Edicion.id))) or db.scalar(select(func.count(Carrera.id)))
    )
