"""Clasificaciones, resultados e importaciones CSV pendientes (feature 006).

Revision ID: 0006_clasificaciones
Revises: 0005_inscripciones
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006_clasificaciones"
down_revision: str | Sequence[str] | None = "0005_inscripciones"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clasificaciones",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("identificador", sa.String(length=100), nullable=False),
        sa.Column("carrera_edicion_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("publicada", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("archivo_origen", sa.String(length=255), nullable=False),
        sa.Column("importada_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("participantes", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint(
            "identificador ~ '^[A-Za-z0-9_-]{1,100}$'",
            name=op.f("ck_clasificaciones_identificador_formato"),
        ),
        sa.CheckConstraint("length(titulo) >= 1", name=op.f("ck_clasificaciones_titulo_no_vacio")),
        sa.CheckConstraint(
            "archivo_origen ~* '\\.csv$'", name=op.f("ck_clasificaciones_archivo_csv")
        ),
        sa.CheckConstraint(
            "participantes BETWEEN 1 AND 5000", name=op.f("ck_clasificaciones_participantes_rango")
        ),
        sa.ForeignKeyConstraint(
            ["carrera_edicion_id"],
            ["carreras_edicion.id"],
            name=op.f("fk_clasificaciones_carrera_edicion_id_carreras_edicion"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clasificaciones")),
        sa.UniqueConstraint("identificador", name=op.f("uq_clasificaciones_identificador")),
        sa.UniqueConstraint(
            "carrera_edicion_id", name=op.f("uq_clasificaciones_carrera_edicion_id")
        ),
    )
    op.create_table(
        "resultados",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("clasificacion_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("posicion", sa.Integer(), nullable=True),
        sa.Column("dorsal", sa.String(length=30), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("tiempo", sa.String(length=60), server_default="", nullable=False),
        sa.Column("categoria", sa.String(length=150), server_default="", nullable=False),
        sa.Column("club", sa.String(length=150), server_default="", nullable=False),
        sa.Column("sexo", sa.String(length=60), server_default="", nullable=False),
        sa.Column("estado", sa.String(length=60), server_default="", nullable=False),
        sa.Column("busqueda", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "posicion IS NULL OR posicion BETWEEN 1 AND 100000",
            name=op.f("ck_resultados_posicion_rango"),
        ),
        sa.CheckConstraint(
            "posicion IS NULL OR length(dorsal) >= 1",
            name=op.f("ck_resultados_dorsal_si_clasificado"),
        ),
        sa.CheckConstraint("length(nombre) >= 1", name=op.f("ck_resultados_nombre_no_vacio")),
        sa.CheckConstraint(
            "posicion IS NULL OR length(tiempo) >= 1",
            name=op.f("ck_resultados_tiempo_si_clasificado"),
        ),
        sa.CheckConstraint(
            "posicion IS NOT NULL OR length(estado) >= 1",
            name=op.f("ck_resultados_estado_si_no_clasificado"),
        ),
        sa.ForeignKeyConstraint(
            ["clasificacion_id"],
            ["clasificaciones.id"],
            name=op.f("fk_resultados_clasificacion_id_clasificaciones"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_resultados")),
    )
    op.create_index(
        "uq_resultados_clasificacion_dorsal",
        "resultados",
        ["clasificacion_id", sa.text("lower(dorsal)")],
        unique=True,
        postgresql_where=sa.text("dorsal <> ''"),
    )
    op.create_index(
        "ix_resultados_clasificacion_orden", "resultados", ["clasificacion_id", "orden"]
    )
    op.create_table(
        "importaciones_csv",
        sa.Column("token", sa.Uuid(), nullable=False),
        sa.Column("sesion_id", sa.BigInteger(), nullable=False),
        sa.Column("carrera_edicion_id", sa.Integer(), nullable=False),
        sa.Column("archivo_origen", sa.String(length=255), nullable=False),
        sa.Column("filas", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sesion_id"],
            ["sesiones.id"],
            name=op.f("fk_importaciones_csv_sesion_id_sesiones"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["carrera_edicion_id"],
            ["carreras_edicion.id"],
            name=op.f("fk_importaciones_csv_carrera_edicion_id_carreras_edicion"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token", name=op.f("pk_importaciones_csv")),
    )


def downgrade() -> None:
    op.drop_table("importaciones_csv")
    op.drop_index("ix_resultados_clasificacion_orden", table_name="resultados")
    op.drop_index("uq_resultados_clasificacion_dorsal", table_name="resultados")
    op.drop_table("resultados")
    op.drop_table("clasificaciones")
