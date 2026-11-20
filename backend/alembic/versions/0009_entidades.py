"""Patrocinadores y colaboradores (feature 009).

Revision ID: 0009_entidades
Revises: 0008_galeria
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_entidades"
down_revision: str | Sequence[str] | None = "0008_galeria"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "entidades",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("logo", sa.String(length=2200), nullable=False),
        sa.Column("web", sa.String(length=2200), server_default="", nullable=False),
        sa.Column("orden", sa.Integer(), server_default="0", nullable=False),
        sa.Column("publicada", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint(
            "tipo IN ('patrocinador', 'colaborador')", name=op.f("ck_entidades_tipo_valido")
        ),
        sa.CheckConstraint(
            "slug ~ '^[A-Za-z0-9_-]{1,100}$'", name=op.f("ck_entidades_slug_formato")
        ),
        sa.CheckConstraint("length(nombre) >= 1", name=op.f("ck_entidades_nombre_no_vacio")),
        sa.CheckConstraint("length(logo) >= 1", name=op.f("ck_entidades_logo_obligatorio")),
        sa.CheckConstraint("orden >= 0", name=op.f("ck_entidades_orden_no_negativo")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entidades")),
        sa.UniqueConstraint("tipo", "slug", name="uq_entidades_tipo_slug"),
    )


def downgrade() -> None:
    op.drop_table("entidades")
