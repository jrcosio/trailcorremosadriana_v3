"""Reglamento por edición y configuración de contacto (feature 010).

Revision ID: 0010_reglamento_contacto
Revises: 0009_entidades
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010_reglamento_contacto"
down_revision: str | Sequence[str] | None = "0009_entidades"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ediciones", sa.Column("reglamento", sa.Text(), server_default="", nullable=False)
    )
    op.create_check_constraint(
        op.f("ck_ediciones_reglamento_longitud"), "ediciones", "length(reglamento) <= 200000"
    )
    op.create_table(
        "configuracion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("correo", sa.String(length=254), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=False),
        sa.Column("instagram", sa.String(length=2200), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name=op.f("ck_configuracion_fila_unica")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_configuracion")),
    )


def downgrade() -> None:
    op.drop_table("configuracion")
    op.drop_constraint(op.f("ck_ediciones_reglamento_longitud"), "ediciones", type_="check")
    op.drop_column("ediciones", "reglamento")
