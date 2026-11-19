"""Ediciones, pruebas y datos de prueba por edición (feature 004).

Revision ID: 0004_evento_carreras
Revises: 0003_archivos
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_evento_carreras"
down_revision: str | Sequence[str] | None = "0003_archivos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AHORA = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "ediciones",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mostrar_contador", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("es_actual", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False
        ),
        sa.CheckConstraint("anio BETWEEN 2000 AND 2099", name=op.f("ck_ediciones_anio_rango")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ediciones")),
        sa.UniqueConstraint("anio", name=op.f("uq_ediciones_anio")),
    )
    op.create_index(
        "uq_ediciones_actual",
        "ediciones",
        ["es_actual"],
        unique=True,
        postgresql_where=sa.text("es_actual"),
    )
    op.create_table(
        "carreras",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("etiqueta", sa.String(length=60), server_default="", nullable=False),
        sa.Column("color", sa.String(length=7), server_default="", nullable=False),
        sa.Column("orden", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint(
            "slug ~ '^[A-Za-z0-9_-]{1,100}$'", name=op.f("ck_carreras_slug_formato")
        ),
        sa.CheckConstraint("length(nombre) >= 1", name=op.f("ck_carreras_nombre_no_vacio")),
        sa.CheckConstraint(
            "color = '' OR color ~ '^#[0-9A-Fa-f]{6}$'", name=op.f("ck_carreras_color_formato")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carreras")),
        sa.UniqueConstraint("slug", name=op.f("uq_carreras_slug")),
    )
    op.create_table(
        "carreras_edicion",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("carrera_id", sa.Integer(), nullable=False),
        sa.Column("edicion_id", sa.Integer(), nullable=False),
        sa.Column("km", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("desnivel", sa.Integer(), nullable=False),
        sa.Column("precio", sa.String(length=40), nullable=False),
        sa.Column("hora_salida", sa.String(length=5), server_default="", nullable=False),
        sa.Column("terreno", sa.String(length=150), server_default="", nullable=False),
        sa.Column("descripcion", sa.Text(), server_default="", nullable=False),
        sa.Column("avituallamientos", sa.String(length=1000), server_default="", nullable=False),
        sa.Column("imagen", sa.String(length=2200), nullable=False),
        sa.Column("ruta", sa.String(length=2200), server_default="", nullable=False),
        sa.Column("wikiloc", sa.String(length=20), server_default="", nullable=False),
        sa.Column("gpx", sa.String(length=2200), server_default="", nullable=False),
        sa.Column("url_inscripcion", sa.String(length=2200), server_default="", nullable=False),
        sa.Column("publicada", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False
        ),
        sa.CheckConstraint("km >= 0", name=op.f("ck_carreras_edicion_km_no_negativo")),
        sa.CheckConstraint("desnivel >= 0", name=op.f("ck_carreras_edicion_desnivel_no_negativo")),
        sa.CheckConstraint("length(precio) >= 1", name=op.f("ck_carreras_edicion_precio_no_vacio")),
        sa.CheckConstraint(
            "hora_salida = '' OR hora_salida ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'",
            name=op.f("ck_carreras_edicion_hora_formato"),
        ),
        sa.CheckConstraint(
            "wikiloc ~ '^[0-9]{0,20}$'", name=op.f("ck_carreras_edicion_wikiloc_formato")
        ),
        sa.CheckConstraint(
            "length(descripcion) <= 5000", name=op.f("ck_carreras_edicion_descripcion_longitud")
        ),
        sa.CheckConstraint(
            "length(imagen) >= 1", name=op.f("ck_carreras_edicion_imagen_obligatoria")
        ),
        sa.ForeignKeyConstraint(
            ["carrera_id"],
            ["carreras.id"],
            name=op.f("fk_carreras_edicion_carrera_id_carreras"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["edicion_id"],
            ["ediciones.id"],
            name=op.f("fk_carreras_edicion_edicion_id_ediciones"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carreras_edicion")),
        sa.UniqueConstraint("carrera_id", "edicion_id", name="uq_carreras_edicion_carrera_edicion"),
    )


def downgrade() -> None:
    op.drop_table("carreras_edicion")
    op.drop_table("carreras")
    op.drop_index("uq_ediciones_actual", table_name="ediciones")
    op.drop_table("ediciones")
