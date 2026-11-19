"""Errores de dominio comunes a los servicios de contenido."""

from dataclasses import dataclass

CONFLICTO_VERSION = "Otra persona ha modificado estos datos. Recarga la página antes de guardar."


@dataclass
class Conflicto(Exception):
    mensaje: str = CONFLICTO_VERSION


@dataclass
class NoEncontrado(Exception):
    mensaje: str = "El contenido no existe."
