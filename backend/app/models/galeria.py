"""Álbumes y fotografías (data-model.md de la feature 008)."""

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Album(Base):
    __tablename__ = "albumes"
    __table_args__ = (
        CheckConstraint("slug ~ '^[A-Za-z0-9_-]{1,100}$'", name="slug_formato"),
        CheckConstraint("length(titulo) >= 1", name="titulo_no_vacio"),
        CheckConstraint("anio BETWEEN 2000 AND 2099", name="anio_rango"),
        CheckConstraint("length(portada) >= 1", name="portada_obligatoria"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    portada: Mapped[str] = mapped_column(String(2200), nullable=False)
    url_externa: Mapped[str] = mapped_column(String(2200), nullable=False, server_default="")
    publicado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    fotografias: Mapped[list["Fotografia"]] = relationship(
        back_populates="album",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Fotografia.orden",
    )


class Fotografia(Base):
    __tablename__ = "fotografias"
    __table_args__ = (UniqueConstraint("album_id", "orden", name="uq_fotografias_album_orden"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    album_id: Mapped[int] = mapped_column(
        ForeignKey("albumes.id", ondelete="CASCADE"), nullable=False
    )
    imagen: Mapped[str] = mapped_column(String(2200), nullable=False)
    alt: Mapped[str] = mapped_column(String(250), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)

    album: Mapped[Album] = relationship(back_populates="fotografias")
