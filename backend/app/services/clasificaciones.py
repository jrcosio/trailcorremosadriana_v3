"""Clasificaciones: importación transaccional, gestión y consulta pública (feature 006)."""

import hashlib
import json
import math
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, exists, func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Carrera, CarreraEdicion, Clasificacion, Edicion, ImportacionCsv, Resultado
from app.schemas.clasificaciones import ClasificacionEntrada, VistaPreviaEntrada
from app.services.contenido import es_modalidad_solidaria
from app.services.csv_clasificaciones import CsvNoValido, leer_csv, mapear, texto_busqueda
from app.services.errores import Conflicto, NoEncontrado
from app.services.fechas import a_iso

CADUCIDAD_IMPORTACION = timedelta(minutes=30)
TAMANO_PAGINA = 50
DUPLICADA = "Ya existe una clasificación de esta carrera y edición. Edita su CSV para sustituirla."
IMPORTACION_NO_VALIDA = "La importación ha caducado o no es válida. Vuelve a seleccionar el CSV."
SIN_CSV = "Importa y confirma un CSV antes de guardar."
NO_ENCONTRADA = "La clasificación no está disponible."


class ClasificacionRechazada(ValueError):
    """Error de datos explicable al usuario (400)."""


def _ahora() -> datetime:
    return datetime.now(UTC)


def _huella(filas: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(filas, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def _ficha(db: Session, slug: str, anio: str) -> CarreraEdicion:
    carrera = db.scalar(select(Carrera).where(Carrera.slug == slug))
    if carrera is None:
        raise ClasificacionRechazada("Selecciona una carrera válida.")
    if es_modalidad_solidaria({"id": carrera.slug, "title": carrera.nombre}):
        raise ClasificacionRechazada("El Dorsal Solidario no tiene clasificación.")
    ficha = db.scalar(
        select(CarreraEdicion)
        .join(Edicion, Edicion.id == CarreraEdicion.edicion_id)
        .where(CarreraEdicion.carrera_id == carrera.id, Edicion.anio == int(anio))
    )
    if ficha is None:
        raise ClasificacionRechazada(
            f"Configura primero la prueba para la edición {anio} en «Pruebas y rutas»."
        )
    return ficha


def _comprobar_unica(db: Session, ficha: CarreraEdicion, identificador: str | None) -> None:
    otra = db.scalar(
        select(Clasificacion.identificador).where(
            Clasificacion.carrera_edicion_id == ficha.id,
            Clasificacion.identificador != (identificador or ""),
        )
    )
    if otra is not None:
        raise Conflicto(DUPLICADA)


def validar_filas(filas: list[dict]) -> None:
    """Revalidación de filas normalizadas antes de escribir (defensa en profundidad)."""
    if not 1 <= len(filas) <= 5000:
        raise ClasificacionRechazada(IMPORTACION_NO_VALIDA)
    dorsales = set()
    for f in filas:
        pos = f.get("position")
        if pos is not None and (not isinstance(pos, int) or not 1 <= pos <= 100_000):
            raise ClasificacionRechazada(IMPORTACION_NO_VALIDA)
        dorsal = str(f.get("bib", ""))
        if (
            (pos is not None and not dorsal)
            or len(dorsal) > 30
            or (dorsal and dorsal.lower() in dorsales)
        ):
            raise ClasificacionRechazada(IMPORTACION_NO_VALIDA)
        if dorsal:
            dorsales.add(dorsal.lower())
        if not f.get("name") or len(f["name"]) > 200:
            raise ClasificacionRechazada(IMPORTACION_NO_VALIDA)
        if (pos is not None and not f.get("time")) or (pos is None and not f.get("status")):
            raise ClasificacionRechazada(IMPORTACION_NO_VALIDA)


def limpiar_caducadas(db: Session) -> None:
    """Borra importaciones pendientes caducadas (contienen datos personales; FR-014)."""
    db.execute(delete(ImportacionCsv).where(ImportacionCsv.expira_en <= _ahora()))


def preparar(db: Session, sesion_id: int, entrada: VistaPreviaEntrada) -> dict:
    """Valida el CSV completo y guarda la importación pendiente ligada a la sesión."""
    ficha = _ficha(db, entrada.raceId, entrada.year)
    _comprobar_unica(db, ficha, entrada.id)
    try:
        filas = mapear(leer_csv(entrada.csv), entrada.mapping)
    except CsvNoValido as exc:
        raise ClasificacionRechazada(str(exc)) from exc
    limpiar_caducadas(db)
    importacion = ImportacionCsv(
        sesion_id=sesion_id,
        carrera_edicion_id=ficha.id,
        archivo_origen=entrada.sourceFile,
        filas=filas,
        sha256=_huella(filas),
        expira_en=_ahora() + CADUCIDAD_IMPORTACION,
    )
    db.add(importacion)
    db.commit()
    return {"token": str(importacion.token), "participants": len(filas)}


def _insertar_filas(db: Session, clasificacion_id: int, filas: list[dict]) -> None:
    db.execute(
        insert(Resultado),
        [
            {
                "clasificacion_id": clasificacion_id,
                "orden": i,
                "posicion": f["position"],
                "dorsal": f["bib"],
                "nombre": f["name"],
                "tiempo": f["time"],
                "categoria": f["category"],
                "club": f["club"],
                "sexo": f["gender"],
                "estado": f["status"],
                "busqueda": texto_busqueda(f["bib"], f["name"], f["club"]),
            }
            for i, f in enumerate(filas)
        ],
    )


def _sustituir(db: Session, clasificacion: Clasificacion, filas: list[dict], archivo: str) -> None:
    db.execute(delete(Resultado).where(Resultado.clasificacion_id == clasificacion.id))
    _insertar_filas(db, clasificacion.id, filas)
    clasificacion.archivo_origen = archivo
    clasificacion.importada_en = _ahora()
    clasificacion.participantes = len(filas)


def guardar(db: Session, identificador: str, sesion_id: int, entrada: ClasificacionEntrada) -> dict:
    """Crea o actualiza; con `importToken` sustituye los participantes en una transacción."""
    try:
        existente = db.scalar(
            select(Clasificacion)
            .where(Clasificacion.identificador == identificador)
            .with_for_update()
        )
        if entrada.version != (existente.version if existente else 0):
            raise Conflicto
        ficha = _ficha(db, entrada.raceId, entrada.year)
        _comprobar_unica(db, ficha, identificador)
        importacion = None
        if entrada.importToken is not None:
            importacion = db.scalar(
                select(ImportacionCsv)
                .where(ImportacionCsv.token == entrada.importToken)
                .with_for_update()
            )
            if (
                importacion is None
                or importacion.sesion_id != sesion_id
                or importacion.expira_en <= _ahora()
                or importacion.carrera_edicion_id != ficha.id
                or importacion.sha256 != _huella(importacion.filas)
            ):
                raise ClasificacionRechazada(IMPORTACION_NO_VALIDA)
            validar_filas(importacion.filas)
        elif existente is None:
            raise ClasificacionRechazada(SIN_CSV)

        if existente is None:
            existente = Clasificacion(
                identificador=identificador,
                carrera_edicion_id=ficha.id,
                titulo=entrada.title,
                archivo_origen=importacion.archivo_origen,
                importada_en=_ahora(),
                participantes=len(importacion.filas),
                version=0,
            )
            db.add(existente)
            db.flush()
        existente.titulo = entrada.title
        existente.publicada = entrada.published
        existente.carrera_edicion_id = ficha.id
        if importacion is not None:
            _sustituir(db, existente, importacion.filas, importacion.archivo_origen)
            db.delete(importacion)  # un solo uso
        existente.version += 1
        limpiar_caducadas(db)
        db.commit()
    except (Conflicto, ClasificacionRechazada):
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise Conflicto(DUPLICADA) from exc
    except Exception:
        db.rollback()  # cualquier fallo conserva la clasificación anterior (FR-006)
        raise
    return item(db, existente, privado=True)


def importar_directo(
    db: Session,
    slug: str,
    anio: str,
    titulo: str,
    archivo: str,
    filas: list[dict],
    publicar: bool,
    sustituir: bool,
) -> tuple[str, int]:
    """Importación del operador con las mismas reglas (FR-013): devuelve (acción, participantes)."""
    ficha = _ficha(db, slug, anio)
    validar_filas(filas)
    existente = db.scalar(
        select(Clasificacion).where(Clasificacion.carrera_edicion_id == ficha.id).with_for_update()
    )
    if existente is not None and not sustituir:
        db.rollback()
        return ("sin cambios", existente.participantes)
    try:
        if existente is None:
            existente = Clasificacion(
                identificador=f"{slug}-{anio}",
                carrera_edicion_id=ficha.id,
                titulo=titulo,
                archivo_origen=archivo,
                importada_en=_ahora(),
                participantes=len(filas),
                publicada=publicar,
                version=0,
            )
            db.add(existente)
            db.flush()
            accion = "creada"
        else:
            accion = "sustituida"
        existente.titulo = titulo
        existente.publicada = publicar
        _sustituir(db, existente, filas, archivo)
        existente.version += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    return (accion, len(filas))


def borrar(db: Session, identificador: str, version: int) -> None:
    clasificacion = db.scalar(
        select(Clasificacion).where(Clasificacion.identificador == identificador).with_for_update()
    )
    if clasificacion is None:
        raise NoEncontrado(NO_ENCONTRADA)
    if clasificacion.version != version:
        db.rollback()
        raise Conflicto
    db.delete(clasificacion)
    db.commit()


def _fila(r: Resultado) -> dict:
    return {
        "position": r.posicion,
        "bib": r.dorsal,
        "name": r.nombre,
        "time": r.tiempo,
        "category": r.categoria,
        "club": r.club,
        "gender": r.sexo,
        "status": r.estado,
    }


def item(db: Session, c: Clasificacion, privado: bool) -> dict:
    ficha = db.get(
        CarreraEdicion,
        c.carrera_edicion_id,
        options=[joinedload(CarreraEdicion.carrera), joinedload(CarreraEdicion.edicion)],
    )
    datos = {
        "id": c.identificador,
        "title": c.titulo,
        "year": str(ficha.edicion.anio),
        "raceId": ficha.carrera.slug,
        "race": ficha.carrera.nombre,
        "sourceFile": c.archivo_origen,
        "importedAt": a_iso(c.importada_en),
        "participants": c.participantes,
        "published": c.publicada,
        "rows": [],
    }
    if privado:
        datos["version"] = c.version
        filas = db.scalars(
            select(Resultado).where(Resultado.clasificacion_id == c.id).order_by(Resultado.orden)
        )
        datos["rows"] = [_fila(r) for r in filas]
    return datos


def listar(db: Session, privado: bool) -> list[dict]:
    consulta = select(Clasificacion).order_by(Clasificacion.id)
    if not privado:
        consulta = consulta.where(Clasificacion.publicada.is_(True))
    return [item(db, c, privado) for c in db.scalars(consulta)]


def _escapar_like(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _podio(db: Session, de_esta, categoria: str, sexo: str, con_sexo: bool, ids: list[int]) -> dict:
    """Puesto en el podio (1–3) de las filas `ids` (feature 012, US10, decisión P12).

    Se calcula sobre quienes tienen puesto y cumplen los filtros de categoría y sexo. La búsqueda
    no cuenta, así que buscar o cambiar de página no cambia quién está en el podio. Hay un podio
    por sexo; si la clasificación no tiene datos de sexo, uno de la general. Si los tiene, quien
    no tiene sexo no entra. Los empates comparten puesto (`rank`).
    """
    if not ids:
        return {}
    grupo = [de_esta, Resultado.posicion.is_not(None)]
    if categoria:
        grupo.append(Resultado.categoria == categoria)
    if sexo:
        grupo.append(Resultado.sexo == sexo)
    if con_sexo:
        grupo.append(Resultado.sexo != "")
    puesto = func.rank().over(partition_by=Resultado.sexo, order_by=Resultado.posicion)
    ranking = select(Resultado.id, puesto.label("puesto")).where(*grupo).subquery()
    consulta = select(ranking.c.id, ranking.c.puesto).where(
        ranking.c.puesto <= 3, ranking.c.id.in_(ids)
    )
    return {fila_id: p for fila_id, p in db.execute(consulta)}


def consultar(
    db: Session, identificador: str, q: str, categoria: str, sexo: str, pagina: int
) -> dict:
    """Consulta pública paginada (FR-008): solo publicadas y no solidarias."""
    clasificacion = db.scalar(
        select(Clasificacion).where(
            Clasificacion.identificador == identificador, Clasificacion.publicada.is_(True)
        )
    )
    if clasificacion is None:
        raise NoEncontrado(NO_ENCONTRADA)
    datos = item(db, clasificacion, privado=False)
    if es_modalidad_solidaria({"id": datos["raceId"], "race": datos["race"]}):
        raise NoEncontrado(NO_ENCONTRADA)

    de_esta = Resultado.clasificacion_id == clasificacion.id
    filtros = [de_esta]
    if categoria:
        filtros.append(Resultado.categoria == categoria)
    if sexo:
        filtros.append(Resultado.sexo == sexo)
    termino = texto_busqueda(q).strip()
    if termino:
        filtros.append(Resultado.busqueda.like(f"%{_escapar_like(termino)}%", escape="\\"))
    filtrados = db.scalar(select(func.count()).select_from(Resultado).where(*filtros)) or 0
    paginas = max(1, math.ceil(filtrados / TAMANO_PAGINA))
    actual = min(max(1, pagina), paginas)
    filas = list(
        db.scalars(
            select(Resultado)
            .where(*filtros)
            .order_by(Resultado.orden)
            .offset((actual - 1) * TAMANO_PAGINA)
            .limit(TAMANO_PAGINA)
        )
    )

    def distintos(columna):
        return sorted(
            v for v in db.scalars(select(columna).where(de_esta, columna != "").distinct())
        )

    def tiene(columna) -> bool:
        return bool(db.scalar(select(exists().where(de_esta, columna != ""))))

    con_sexo = tiene(Resultado.sexo)
    podio = _podio(db, de_esta, categoria, sexo, con_sexo, [r.id for r in filas])
    return {
        "rows": [{**_fila(r), "podium": podio.get(r.id)} for r in filas],
        "total": clasificacion.participantes,
        "filtered": filtrados,
        "page": actual,
        "pages": paginas,
        "pageSize": TAMANO_PAGINA,
        "categories": distintos(Resultado.categoria),
        "genders": distintos(Resultado.sexo),
        "columns": {
            "category": tiene(Resultado.categoria),
            "club": tiene(Resultado.club),
            "gender": con_sexo,
            "status": tiene(Resultado.estado),
        },
    }
