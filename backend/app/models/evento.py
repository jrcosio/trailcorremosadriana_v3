"""Ediciones, pruebas y datos de prueba por edición (data-model.md de la feature 004)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

AHORA = func.now()


class Edicion(Base):
    __tablename__ = "ediciones"
    __table_args__ = (
        CheckConstraint("anio BETWEEN 2000 AND 2099", name="anio_rango"),
        CheckConstraint("length(mensaje_inscripciones) <= 2000", name="mensaje_longitud"),
        CheckConstraint("length(reglamento) <= 200000", name="reglamento_longitud"),
        Index("uq_ediciones_actual", "es_actual", unique=True, postgresql_where=text("es_actual")),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    anio: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    fecha_hora: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    mostrar_contador: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    es_actual: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Inscripciones y Dorsal Solidario (feature 005)
    inscripciones_abiertas: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    mensaje_inscripciones: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    url_dorsal_solidario: Mapped[str] = mapped_column(
        String(2200), nullable=False, server_default=""
    )
    # Reglamento de la edición (feature 010); vacío = sin reglamento propio.
    reglamento: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA, onupdate=AHORA
    )


class Carrera(Base):
    __tablename__ = "carreras"
    __table_args__ = (
        CheckConstraint("slug ~ '^[A-Za-z0-9_-]{1,100}$'", name="slug_formato"),
        CheckConstraint("length(nombre) >= 1", name="nombre_no_vacio"),
        CheckConstraint("color = '' OR color ~ '^#[0-9A-Fa-f]{6}$'", name="color_formato"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    etiqueta: Mapped[str] = mapped_column(String(60), nullable=False, server_default="")
    color: Mapped[str] = mapped_column(String(7), nullable=False, server_default="")
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    fichas: Mapped[list["CarreraEdicion"]] = relationship(
        back_populates="carrera", cascade="all, delete-orphan", passive_deletes=True
    )


class CarreraEdicion(Base):
    __tablename__ = "carreras_edicion"
    __table_args__ = (
        UniqueConstraint("carrera_id", "edicion_id", name="uq_carreras_edicion_carrera_edicion"),
        CheckConstraint("km >= 0", name="km_no_negativo"),
        CheckConstraint("desnivel >= 0", name="desnivel_no_negativo"),
        CheckConstraint("length(precio) >= 1", name="precio_no_vacio"),
        CheckConstraint(
            "hora_salida = '' OR hora_salida ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'",
            name="hora_formato",
        ),
        CheckConstraint("wikiloc ~ '^[0-9]{0,20}$'", name="wikiloc_formato"),
        CheckConstraint("length(descripcion) <= 5000", name="descripcion_longitud"),
        CheckConstraint("length(imagen) >= 1", name="imagen_obligatoria"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    carrera_id: Mapped[int] = mapped_column(
        ForeignKey("carreras.id", ondelete="CASCADE"), nullable=False
    )
    edicion_id: Mapped[int] = mapped_column(
        ForeignKey("ediciones.id", ondelete="RESTRICT"), nullable=False
    )
    km: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    desnivel: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[str] = mapped_column(String(40), nullable=False)
    hora_salida: Mapped[str] = mapped_column(String(5), nullable=False, server_default="")
    terreno: Mapped[str] = mapped_column(String(150), nullable=False, server_default="")
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    avituallamientos: Mapped[str] = mapped_column(String(1000), nullable=False, server_default="")
    imagen: Mapped[str] = mapped_column(String(2200), nullable=False)
    ruta: Mapped[str] = mapped_column(String(2200), nullable=False, server_default="")
    wikiloc: Mapped[str] = mapped_column(String(20), nullable=False, server_default="")
    gpx: Mapped[str] = mapped_column(String(2200), nullable=False, server_default="")
    url_inscripcion: Mapped[str] = mapped_column(String(2200), nullable=False, server_default="")
    publicada: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=AHORA, onupdate=AHORA
    )

    carrera: Mapped[Carrera] = relationship(back_populates="fichas")
    edicion: Mapped[Edicion] = relationship()
