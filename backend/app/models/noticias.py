"""Noticias (data-model.md de la feature 007)."""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Identity,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Noticia(Base):
    __tablename__ = "noticias"
    __table_args__ = (
        CheckConstraint("slug ~ '^[A-Za-z0-9_-]{1,100}$'", name="slug_formato"),
        CheckConstraint("length(titulo) >= 1", name="titulo_no_vacio"),
        CheckConstraint("length(cuerpo) BETWEEN 1 AND 50000", name="cuerpo_longitud"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False, server_default="")
    fecha: Mapped[date | None] = mapped_column(Date)
    imagen: Mapped[str] = mapped_column(String(2200), nullable=False, server_default="")
    extracto: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    publicada: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
