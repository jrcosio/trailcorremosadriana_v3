"""Clasificaciones, resultados e importaciones CSV pendientes (data-model.md de la feature 006)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.evento import CarreraEdicion


class Clasificacion(Base):
    __tablename__ = "clasificaciones"
    __table_args__ = (
        CheckConstraint("identificador ~ '^[A-Za-z0-9_-]{1,100}$'", name="identificador_formato"),
        CheckConstraint("length(titulo) >= 1", name="titulo_no_vacio"),
        CheckConstraint("archivo_origen ~* '\\.csv$'", name="archivo_csv"),
        CheckConstraint("participantes BETWEEN 1 AND 5000", name="participantes_rango"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    identificador: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    carrera_edicion_id: Mapped[int] = mapped_column(
        ForeignKey("carreras_edicion.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    publicada: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    archivo_origen: Mapped[str] = mapped_column(String(255), nullable=False)
    importada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    participantes: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    ficha: Mapped[CarreraEdicion] = relationship()
    resultados: Mapped[list["Resultado"]] = relationship(
        back_populates="clasificacion",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Resultado.orden",
    )


class Resultado(Base):
    __tablename__ = "resultados"
    __table_args__ = (
        CheckConstraint("posicion IS NULL OR posicion BETWEEN 1 AND 100000", name="posicion_rango"),
        CheckConstraint("posicion IS NULL OR length(dorsal) >= 1", name="dorsal_si_clasificado"),
        CheckConstraint("length(nombre) >= 1", name="nombre_no_vacio"),
        CheckConstraint("posicion IS NULL OR length(tiempo) >= 1", name="tiempo_si_clasificado"),
        CheckConstraint(
            "posicion IS NOT NULL OR length(estado) >= 1", name="estado_si_no_clasificado"
        ),
        Index(
            "uq_resultados_clasificacion_dorsal",
            "clasificacion_id",
            func.lower("dorsal"),
            unique=True,
            postgresql_where=text("dorsal <> ''"),
        ),
        Index("ix_resultados_clasificacion_orden", "clasificacion_id", "orden"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    clasificacion_id: Mapped[int] = mapped_column(
        ForeignKey("clasificaciones.id", ondelete="CASCADE"), nullable=False
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    posicion: Mapped[int | None] = mapped_column(Integer)
    dorsal: Mapped[str] = mapped_column(String(30), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tiempo: Mapped[str] = mapped_column(String(60), nullable=False, server_default="")
    categoria: Mapped[str] = mapped_column(String(150), nullable=False, server_default="")
    club: Mapped[str] = mapped_column(String(150), nullable=False, server_default="")
    sexo: Mapped[str] = mapped_column(String(60), nullable=False, server_default="")
    estado: Mapped[str] = mapped_column(String(60), nullable=False, server_default="")
    busqueda: Mapped[str] = mapped_column(Text, nullable=False)

    clasificacion: Mapped[Clasificacion] = relationship(back_populates="resultados")


class ImportacionCsv(Base):
    __tablename__ = "importaciones_csv"

    token: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    sesion_id: Mapped[int] = mapped_column(
        ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False
    )
    carrera_edicion_id: Mapped[int] = mapped_column(
        ForeignKey("carreras_edicion.id", ondelete="CASCADE"), nullable=False
    )
    archivo_origen: Mapped[str] = mapped_column(String(255), nullable=False)
    filas: Mapped[list] = mapped_column(JSONB, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
