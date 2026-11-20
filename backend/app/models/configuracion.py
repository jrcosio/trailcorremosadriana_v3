"""Configuración general de fila única: contacto y redes (data-model.md de la feature 010)."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Configuracion(Base):
    __tablename__ = "configuracion"
    __table_args__ = (CheckConstraint("id = 1", name="fila_unica"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    correo: Mapped[str] = mapped_column(String(254), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    instagram: Mapped[str] = mapped_column(String(2200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
