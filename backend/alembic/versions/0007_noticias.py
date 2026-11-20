"""Noticias (feature 007).

Revision ID: 0007_noticias
Revises: 0006_clasificaciones
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_noticias"
down_revision: str | Sequence[str] | None = "0006_clasificaciones"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "noticias",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("categoria", sa.String(length=60), server_default="", nullable=False),
        sa.Column("fecha", sa.Date(), nullable=True),
        sa.Column("imagen", sa.String(length=2200), server_default="", nullable=False),
        sa.Column("extracto", sa.String(length=500), server_default="", nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column("publicada", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "slug ~ '^[A-Za-z0-9_-]{1,100}$'", name=op.f("ck_noticias_slug_formato")
        ),
        sa.CheckConstraint("length(titulo) >= 1", name=op.f("ck_noticias_titulo_no_vacio")),
        sa.CheckConstraint(
            "length(cuerpo) BETWEEN 1 AND 50000", name=op.f("ck_noticias_cuerpo_longitud")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_noticias")),
        sa.UniqueConstraint("slug", name=op.f("uq_noticias_slug")),
    )


def downgrade() -> None:
    op.drop_table("noticias")
