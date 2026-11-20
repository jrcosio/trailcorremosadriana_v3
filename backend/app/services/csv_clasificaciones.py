"""Lector y validador de CSV de clasificaciones (adaptación de frontend/src/lib/classifications.ts).

Reglas de docs/referencia/13_CLASIFICACIONES_CSV.md. El servidor es la validación autoritativa
(FR-005 de la feature 006); el cliente usa el lector TS para la vista previa inmediata.
"""

import re
import unicodedata
from dataclasses import dataclass

MAX_CSV_CARACTERES = 1_000_000
MAX_FILAS = 5000
MAX_COLUMNAS = 60
MAX_CELDA = 10_000

CAMPOS = (
    ("position", "Posición", True),
    ("bib", "Dorsal", True),
    ("name", "Nombre", True),
    ("surname", "Apellidos", False),
    ("time", "Tiempo", True),
    ("category", "Categoría", False),
    ("club", "Club", False),
    ("gender", "Sexo", False),
    ("status", "Estado", False),
)
ALIAS = {
    "position": [
        "posicion",
        "pos",
        "puesto",
        "posgeneral",
        "posiciongeneral",
        "puestogeneral",
        "clasificacion",
        "rank",
        "ranking",
        "position",
    ],
    "bib": ["dorsal", "numdorsal", "numerodorsal", "bib", "bibnumber", "numero", "num"],
    "name": [
        "nombre",
        "nombrecompleto",
        "nombreyapellidos",
        "participante",
        "corredor",
        "atleta",
        "name",
        "firstname",
        "fullname",
    ],
    "surname": ["apellido", "apellidos", "surname", "lastname"],
    "time": [
        "tiempo",
        "tiempototal",
        "tiempooficial",
        "tiempofinal",
        "tiemporeal",
        "time",
        "totaltime",
        "finishtime",
        "marca",
        "meta",
    ],
    "category": ["categoria", "category", "cat"],
    "club": ["club", "equipo", "team"],
    "gender": ["sexo", "genero", "gender", "sex"],
    "status": ["estado", "status", "situacion"],
}
POSICION = re.compile(r"^[1-9]\d*[.ºª]?$")
NO_CLASIFICADO = re.compile(
    r"^(?:-|nc|dnf|dns|dsq|dq|ret|retirad[oa]|abandono"
    r"|no clasificad[oa]|no presentad[oa]|descalificad[oa])$",
    re.IGNORECASE,
)


class CsvNoValido(ValueError):
    pass


@dataclass
class TablaCsv:
    cabeceras: list[str]
    registros: list[list[str]]
    separador: str


def normalizar(valor: str) -> str:
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", valor) if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]", "", sin_tildes.lower())


def texto_busqueda(*valores: str) -> str:
    """Minúsculas y sin tildes, para búsqueda insensible (FR-008)."""
    texto = " ".join(valores)
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    ).lower()


def decodificar(datos: bytes) -> str:
    """UTF-8 (con o sin BOM) o, si no es válido, Windows-1252."""
    try:
        return datos.decode("utf-8")
    except UnicodeDecodeError:
        return datos.decode("cp1252", errors="replace")


def _dividir(texto: str, separador: str) -> list[list[str]]:
    filas: list[list[str]] = []
    fila: list[str] = []
    celda = ""
    entre_comillas = False
    cerrada = False

    def meter_celda() -> None:
        nonlocal celda, cerrada
        fila.append(celda.strip())
        celda = ""
        cerrada = False
        if len(fila) > MAX_COLUMNAS:
            raise CsvNoValido(f"El CSV supera las {MAX_COLUMNAS} columnas.")

    def meter_fila() -> None:
        nonlocal fila
        meter_celda()
        if any(v != "" for v in fila):
            filas.append(fila)
        fila = []
        if len(filas) > MAX_FILAS + 1:
            raise CsvNoValido(f"Máximo {MAX_FILAS} participantes por CSV.")

    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]
        if entre_comillas:
            if c == '"':
                if i + 1 < n and texto[i + 1] == '"':
                    celda += '"'
                    i += 1
                else:
                    entre_comillas = False
                    cerrada = True
            else:
                celda += c
            i += 1
            continue
        if c == separador:
            meter_celda()
        elif c in "\n\r":
            if c == "\r" and i + 1 < n and texto[i + 1] == "\n":
                i += 1
            meter_fila()
        elif c == '"':
            if cerrada or celda.strip():
                raise CsvNoValido("Comillas incorrectas en el CSV.")
            celda = ""
            entre_comillas = True
        else:
            if cerrada and c.strip():
                raise CsvNoValido("Hay texto después del cierre de unas comillas.")
            celda += c
            if len(celda) > MAX_CELDA:
                raise CsvNoValido("Una celda del CSV es demasiado larga.")
        i += 1
    if entre_comillas:
        raise CsvNoValido("Hay comillas sin cerrar en el CSV.")
    if celda or fila or cerrada:
        meter_fila()
    return filas


def leer_csv(texto: str) -> TablaCsv:
    if len(texto) > MAX_CSV_CARACTERES:
        raise CsvNoValido("El CSV debe ocupar como máximo 1 MB.")
    texto = texto.removeprefix("﻿")
    candidatos: list[tuple[list[list[str]], str]] = []
    fallo = ""
    for separador in (";", ",", "\t"):
        try:
            filas = _dividir(texto, separador)
        except CsvNoValido as exc:
            fallo = str(exc)
            continue
        if filas and len(filas[0]) > 1:
            candidatos.append((filas, separador))
    if not candidatos:
        raise CsvNoValido(
            fallo or "Usa un CSV con cabeceras separado por coma, punto y coma o tabulador."
        )
    filas, separador = max(
        candidatos, key=lambda c: len(c[0][0])
    )  # estable: gana el primero en empate
    cabeceras, *registros = filas
    if any(not h for h in cabeceras):
        raise CsvNoValido("Todas las columnas deben tener una cabecera.")
    if not registros:
        raise CsvNoValido("El CSV no contiene participantes.")
    for i, registro in enumerate(registros):
        if len(registro) != len(cabeceras):
            raise CsvNoValido(
                f"Fila de datos {i + 1}: hay {len(registro)} columnas; "
                f"se esperaban {len(cabeceras)}."
            )
    return TablaCsv(cabeceras, registros, separador)


def adivinar_mapeo(cabeceras: list[str]) -> dict[str, int]:
    mapeo: dict[str, int] = {}
    for campo, _, _ in CAMPOS:
        coincidencias = [i for i, h in enumerate(cabeceras) if normalizar(h) in ALIAS[campo]]
        if len(coincidencias) == 1:
            mapeo[campo] = coincidencias[0]
    return mapeo


def mapear(tabla: TablaCsv, mapeo: dict[str, int]) -> list[dict]:
    """Filas normalizadas (position, bib, name, time, category, club, gender, status) ordenadas."""
    campos_validos = {c for c, _, _ in CAMPOS}
    if any(k not in campos_validos for k in mapeo):
        raise CsvNoValido("Asignación de columnas no válida.")
    for clave, etiqueta, obligatorio in CAMPOS:
        indice = mapeo.get(clave)
        if obligatorio and indice is None:
            raise CsvNoValido(f"Selecciona la columna «{etiqueta}».")
        if indice is not None and (
            not isinstance(indice, int)
            or isinstance(indice, bool)
            or not 0 <= indice < len(tabla.cabeceras)
        ):
            raise CsvNoValido(f"Columna inválida para «{etiqueta}».")
    seleccion = list(mapeo.values())
    if len(set(seleccion)) != len(seleccion):
        raise CsvNoValido("Cada campo debe utilizar una columna distinta.")

    dorsales: set[str] = set()
    filas: list[dict] = []
    for i, registro in enumerate(tabla.registros):

        def leer(clave: str, registro: list[str] = registro) -> str:
            return "" if clave not in mapeo else re.sub(r"\s+", " ", registro[mapeo[clave]]).strip()

        def fallo(mensaje: str, i: int = i) -> CsvNoValido:
            return CsvNoValido(f"Fila de datos {i + 1}: {mensaje}")

        bruta = leer("position")
        posicion = int(re.sub(r"[.ºª]$", "", bruta)) if POSICION.match(bruta) else None
        if posicion is not None and posicion > 100_000:
            raise fallo("posición demasiado grande.")
        if posicion is None and bruta and not NO_CLASIFICADO.match(bruta):
            raise fallo("posición inválida. Usa un número, NC, DNF, DNS o DSQ.")
        dorsal = leer("bib")
        nombre = " ".join(v for v in (leer("name"), leer("surname")) if v)
        tiempo = leer("time")
        estado = leer("status") or (bruta if posicion is None else "")
        # Decisión del propietario (P3): el dorsal solo es obligatorio para los clasificados.
        if (posicion is not None and not dorsal) or len(dorsal) > 30:
            raise fallo(
                "el dorsal es obligatorio para los clasificados y admite hasta 30 caracteres."
            )
        if dorsal and dorsal.lower() in dorsales:
            raise fallo(f"el dorsal «{dorsal}» está repetido.")
        if dorsal:
            dorsales.add(dorsal.lower())
        if not nombre or len(nombre) > 200:
            raise fallo("el nombre es obligatorio y admite hasta 200 caracteres.")
        if posicion is not None and not tiempo:
            raise fallo("falta el tiempo de un participante clasificado.")
        if posicion is None and (not estado or estado == "-"):
            raise fallo("indica un estado (por ejemplo, DNF) para un participante sin posición.")
        fila = {
            "position": posicion,
            "bib": dorsal,
            "name": nombre,
            "time": tiempo,
            "category": leer("category"),
            "club": leer("club"),
            "gender": leer("gender"),
            "status": estado,
        }
        for clave in ("category", "club"):
            if len(fila[clave]) > 150:
                raise fallo(f"«{clave}» admite hasta 150 caracteres.")
        for clave in ("time", "gender", "status"):
            if len(fila[clave]) > 60:
                raise fallo(f"«{clave}» admite hasta 60 caracteres.")
        filas.append(fila)
    # Orden estable por posición; los no clasificados al final (igual que el cliente).
    return sorted(filas, key=lambda f: (f["position"] is None, f["position"] or 0))
