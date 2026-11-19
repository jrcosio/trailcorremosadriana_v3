"""Configuración de la API a partir de variables de entorno (ver `.env.example`)."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict


def normalizar_origen(valor: str) -> str:
    """`Esquema://host[:puerto]` en minúsculas y sin barra final; vacío si no es válido."""
    partes = urlsplit(valor.strip())
    if partes.scheme not in ("http", "https") or not partes.netloc:
        return ""
    return f"{partes.scheme.lower()}://{partes.netloc.lower()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://trail:trail_dev@db:5432/trail"
    public_origin: str = "http://localhost:8080"
    entorno: Literal["desarrollo", "produccion"] = "desarrollo"
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    # Tiempo máximo de conexión a PostgreSQL (segundos); acota /api/ready con la base caída.
    db_connect_timeout: int = 3

    # Administración (feature 002)
    session_hours: int = 8
    cookie_secure: bool = True
    origenes_permitidos: str = ""
    login_max_intentos: int = 8
    login_ventana_minutos: int = 15

    # Archivos (feature 003)
    almacenamiento: Literal["local", "s3"] = "local"
    media_dir: str = "/data/media"
    upload_max_bytes: int = 10_000_000
    s3_endpoint_url: str = ""
    s3_bucket: str = ""
    s3_region: str = "auto"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_crear_bucket: bool = False

    @property
    def es_desarrollo(self) -> bool:
        return self.entorno == "desarrollo"

    @property
    def origenes_validos(self) -> frozenset[str]:
        candidatos = [self.public_origin, *self.origenes_permitidos.split(",")]
        return frozenset(o for o in map(normalizar_origen, candidatos) if o)


@lru_cache
def get_settings() -> Settings:
    return Settings()
