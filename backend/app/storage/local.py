"""Almacenamiento en disco (volumen persistente). Solo acepta claves ya validadas."""

import os
import re
import tempfile
from pathlib import Path

from app.storage import AlmacenamientoNoDisponible

CLAVE_SEGURA = re.compile(r"^[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$")


class AlmacenamientoLocal:
    def __init__(self, directorio: str) -> None:
        self.directorio = Path(directorio)

    def _ruta(self, clave: str) -> Path:
        if not CLAVE_SEGURA.match(clave):  # defensa en profundidad: nunca rutas arbitrarias
            raise ValueError("Clave no válida")
        return self.directorio / clave

    def guardar(self, clave: str, datos: bytes, tipo: str) -> None:
        destino = self._ruta(clave)
        try:
            self.directorio.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=self.directorio, delete=False, prefix=".subida-"
            ) as tmp:
                tmp.write(datos)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp.name, destino)
        except OSError as exc:
            raise AlmacenamientoNoDisponible from exc

    def leer(self, clave: str) -> bytes | None:
        try:
            return self._ruta(clave).read_bytes()
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise AlmacenamientoNoDisponible from exc
