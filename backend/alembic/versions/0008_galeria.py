"""Álbumes y fotografías (feature 008).

Revision ID: 0008_galeria
Revises: 0007_noticias
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_galeria"
down_revision: str | Sequence[str] | None = "0007_noticias"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "albumes",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("portada", sa.String(length=2200), nullable=False),
        sa.Column("url_externa", sa.String(length=2200), server_default="", nullable=False),
        sa.Column("publicado", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("orden", sa.Integer(), server_default="0", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.CheckConstraint("slug ~ '^[A-Za-z0-9_-]{1,100}$'", name=op.f("ck_albumes_slug_formato")),
        sa.CheckConstraint("length(titulo) >= 1", name=op.f("ck_albumes_titulo_no_vacio")),
        sa.CheckConstraint("anio BETWEEN 2000 AND 2099", name=op.f("ck_albumes_anio_rango")),
        sa.CheckConstraint("length(portada) >= 1", name=op.f("ck_albumes_portada_obligatoria")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_albumes")),
        sa.UniqueConstraint("slug", name=op.f("uq_albumes_slug")),
    )
    op.create_table(
        "fotografias",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("album_id", sa.Integer(), nullable=False),
        sa.Column("imagen", sa.String(length=2200), nullable=False),
        sa.Column("alt", sa.String(length=250), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["albumes.id"],
            name=op.f("fk_fotografias_album_id_albumes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fotografias")),
        sa.UniqueConstraint("album_id", "orden", name="uq_fotografias_album_orden"),
    )


def downgrade() -> None:
    op.drop_table("fotografias")
    op.drop_table("albumes")
