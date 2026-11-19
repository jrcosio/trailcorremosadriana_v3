"""Revisión base del esquema (sin tablas de dominio).

Las tablas de cada recurso se añaden en las revisiones de sus features.

Revision ID: 0001_base
Revises:
Create Date: 2026-11-19
"""

from collections.abc import Sequence

revision: str = "0001_base"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
