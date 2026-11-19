"""Almacenamiento de objetos: interfaz común y fábrica (local o compatible con S3/R2)."""

from typing import Protocol

from app.core.config import Settings


class AlmacenamientoNoDisponible(Exception):
    """El almacenamiento no respondió o rechazó la operación (se traduce a 503)."""


class Almacenamiento(Protocol):
    def guardar(self, clave: str, datos: bytes, tipo: str) -> None: ...

    def leer(self, clave: str) -> bytes | None: ...


def crear_almacenamiento(settings: Settings) -> Almacenamiento:
    if settings.almacenamiento == "s3":
        from app.storage.s3 import AlmacenamientoS3

        return AlmacenamientoS3(
            endpoint_url=settings.s3_endpoint_url or None,
            bucket=settings.s3_bucket,
            region=settings.s3_region,
            access_key_id=settings.s3_access_key_id,
            secret_access_key=settings.s3_secret_access_key,
            crear_bucket=settings.s3_crear_bucket,
        )
    from app.storage.local import AlmacenamientoLocal

    return AlmacenamientoLocal(settings.media_dir)
