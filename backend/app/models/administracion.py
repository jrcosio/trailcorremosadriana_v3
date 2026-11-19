"""Administradores, sesiones y límites de acceso (data-model.md de la feature 002)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

AHORA = func.now()


class Administrador(Base):
    __tablename__ = "administradores"
    __table_args__ = (
        CheckConstraint("usuario = lower(usuario)", name="usuario_minusculas"),
        CheckConstraint("usuario ~ '^[a-z0-9][a-z0-9._-]{2,63}$'", name="usuario_formato"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    usuario: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA, onupdate=AHORA
    )
    ultimo_acceso_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    password_cambiada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA
    )

    sesiones: Mapped[list["Sesion"]] = relationship(
        back_populates="administrador", passive_deletes=True
    )


class Sesion(Base):
    __tablename__ = "sesiones"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    administrador_id: Mapped[int] = mapped_column(
        ForeignKey("administradores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    csrf_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA
    )
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revocada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ultimo_uso_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA
    )

    administrador: Mapped[Administrador] = relationship(back_populates="sesiones")


class LimiteLogin(Base):
    __tablename__ = "limites_login"
    __table_args__ = (CheckConstraint("intentos >= 0", name="intentos_no_negativos"),)

    clave: Mapped[str] = mapped_column(String(64), primary_key=True)
    intentos: Mapped[int] = mapped_column(Integer, nullable=False)
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
