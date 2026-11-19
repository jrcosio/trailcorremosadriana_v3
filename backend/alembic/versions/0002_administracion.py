"""Administradores, sesiones y límites de acceso (feature 002).

Revision ID: 0002_administracion
Revises: 0001_base
Create Date: 2026-11-19
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_administracion"
down_revision: str | Sequence[str] | None = "0001_base"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AHORA = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "administradores",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("usuario", sa.String(length=64), nullable=False),
        sa.Column("hash_password", sa.String(length=255), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False
        ),
        sa.Column("ultimo_acceso_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "password_cambiada_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False
        ),
        sa.CheckConstraint(
            "usuario = lower(usuario)", name=op.f("ck_administradores_usuario_minusculas")
        ),
        sa.CheckConstraint(
            "usuario ~ '^[a-z0-9][a-z0-9._-]{2,63}$'",
            name=op.f("ck_administradores_usuario_formato"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_administradores")),
        sa.UniqueConstraint("usuario", name=op.f("uq_administradores_usuario")),
    )
    op.create_table(
        "sesiones",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("administrador_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("csrf_hash", sa.String(length=64), nullable=False),
        sa.Column("creada_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "ultimo_uso_en", sa.DateTime(timezone=True), server_default=AHORA, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["administrador_id"],
            ["administradores.id"],
            name=op.f("fk_sesiones_administrador_id_administradores"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sesiones")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sesiones_token_hash")),
    )
    op.create_index(op.f("ix_sesiones_administrador_id"), "sesiones", ["administrador_id"])
    op.create_index(op.f("ix_sesiones_expira_en"), "sesiones", ["expira_en"])
    op.create_table(
        "limites_login",
        sa.Column("clave", sa.String(length=64), nullable=False),
        sa.Column("intentos", sa.Integer(), nullable=False),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("intentos >= 0", name=op.f("ck_limites_login_intentos_no_negativos")),
        sa.PrimaryKeyConstraint("clave", name=op.f("pk_limites_login")),
    )


def downgrade() -> None:
    op.drop_table("limites_login")
    op.drop_index(op.f("ix_sesiones_expira_en"), table_name="sesiones")
    op.drop_index(op.f("ix_sesiones_administrador_id"), table_name="sesiones")
    op.drop_table("sesiones")
    op.drop_table("administradores")
