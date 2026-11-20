"""Patrocinadores y colaboradores: mismo modelo, secciones distintas (feature 009)."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

TIPOS = ("patrocinador", "colaborador")


class Entidad(Base):
    __tablename__ = "entidades"
    __table_args__ = (
        CheckConstraint("tipo IN ('patrocinador', 'colaborador')", name="tipo_valido"),
        CheckConstraint("slug ~ '^[A-Za-z0-9_-]{1,100}$'", name="slug_formato"),
        CheckConstraint("length(nombre) >= 1", name="nombre_no_vacio"),
        CheckConstraint("length(logo) >= 1", name="logo_obligatorio"),
        CheckConstraint("orden >= 0", name="orden_no_negativo"),
        UniqueConstraint("tipo", "slug", name="uq_entidades_tipo_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    logo: Mapped[str] = mapped_column(String(2200), nullable=False)
    web: Mapped[str] = mapped_column(String(2200), nullable=False, server_default="")
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    publicada: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
