"""Configuración de la API a partir de variables de entorno (ver `.env.example`)."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://trail:trail_dev@db:5432/trail"
    public_origin: str = "http://localhost:8080"
    entorno: Literal["desarrollo", "produccion"] = "desarrollo"
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    # Tiempo máximo de conexión a PostgreSQL (segundos); acota /api/ready con la base caída.
    db_connect_timeout: int = 3

    @property
    def es_desarrollo(self) -> bool:
        return self.entorno == "desarrollo"


@lru_cache
def get_settings() -> Settings:
    return Settings()
