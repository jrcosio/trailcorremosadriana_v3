"""Archivos subidos: referencia y metadatos (data-model.md de la feature 003)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

PATRON_CLAVE = r"^[0-9a-f]{32}\.(jpg|png|webp|pdf|gpx)$"
TIPOS = ("image/jpeg", "image/png", "image/webp", "application/pdf", "application/gpx+xml")


class Archivo(Base):
    __tablename__ = "archivos"
    __table_args__ = (
        CheckConstraint(f"clave ~ '{PATRON_CLAVE}'", name="clave_formato"),
        CheckConstraint(
            "tipo IN (" + ", ".join(f"'{t}'" for t in TIPOS) + ")", name="tipo_admitido"
        ),
        CheckConstraint("tamano > 0", name="tamano_positivo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    clave: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(64), nullable=False)
    tamano: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    nombre_original: Mapped[str | None] = mapped_column(String(255))
    subido_por: Mapped[int | None] = mapped_column(
        ForeignKey("administradores.id", ondelete="SET NULL")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
