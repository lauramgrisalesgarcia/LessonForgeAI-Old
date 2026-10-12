"""users and tutor_students; enable pgvector

Revision ID: 0001
Revises:
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role = sa.Enum("teacher", "student", name="user_role")


def upgrade() -> None:
    # pgvector se habilita desde el inicio (ADR-004); las tablas vectoriales llegan después
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("email = lower(email)", name=op.f("ck_users_email_lowercase")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )

    op.create_table(
        "tutor_students",
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
            name=op.f("fk_tutor_students_teacher_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_tutor_students_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("teacher_id", "student_id", name=op.f("pk_tutor_students")),
    )
    op.create_index(
        op.f("ix_tutor_students_student_id"), "tutor_students", ["student_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tutor_students_student_id"), table_name="tutor_students")
    op.drop_table("tutor_students")
    op.drop_table("users")
    user_role.drop(op.get_bind(), checkfirst=True)
    # La extensión vector se conserva: puede estar en uso por otros objetos
