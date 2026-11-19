"""Inscripciones y Dorsal Solidario por edición (feature 005).

Revision ID: 0005_inscripciones
Revises: 0004_evento_carreras
Create Date: 2026-11-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_inscripciones"
down_revision: str | Sequence[str] | None = "0004_evento_carreras"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ediciones",
        sa.Column("inscripciones_abiertas", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "ediciones",
        sa.Column("mensaje_inscripciones", sa.Text(), server_default="", nullable=False),
    )
    op.add_column(
        "ediciones",
        sa.Column(
            "url_dorsal_solidario", sa.String(length=2200), server_default="", nullable=False
        ),
    )
    op.create_check_constraint(
        op.f("ck_ediciones_mensaje_longitud"), "ediciones", "length(mensaje_inscripciones) <= 2000"
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_ediciones_mensaje_longitud"), "ediciones", type_="check")
    op.drop_column("ediciones", "url_dorsal_solidario")
    op.drop_column("ediciones", "mensaje_inscripciones")
    op.drop_column("ediciones", "inscripciones_abiertas")
