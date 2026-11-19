"""Archivos subidos (feature 003).

Revision ID: 0003_archivos
Revises: 0002_administracion
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_archivos"
down_revision: str | Sequence[str] | None = "0002_administracion"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TIPOS = "'image/jpeg', 'image/png', 'image/webp', 'application/pdf', 'application/gpx+xml'"


def upgrade() -> None:
    op.create_table(
        "archivos",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("clave", sa.String(length=64), nullable=False),
        sa.Column("tipo", sa.String(length=64), nullable=False),
        sa.Column("tamano", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("nombre_original", sa.String(length=255), nullable=True),
        sa.Column("subido_por", sa.Integer(), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint(
            "clave ~ '^[0-9a-f]{32}\\.(jpg|png|webp|pdf|gpx)$'",
            name=op.f("ck_archivos_clave_formato"),
        ),
        sa.CheckConstraint(f"tipo IN ({TIPOS})", name=op.f("ck_archivos_tipo_admitido")),
        sa.CheckConstraint("tamano > 0", name=op.f("ck_archivos_tamano_positivo")),
        sa.ForeignKeyConstraint(
            ["subido_por"],
            ["administradores.id"],
            name=op.f("fk_archivos_subido_por_administradores"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_archivos")),
        sa.UniqueConstraint("clave", name=op.f("uq_archivos_clave")),
    )


def downgrade() -> None:
    op.drop_table("archivos")
