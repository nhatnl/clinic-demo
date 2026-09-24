"""Add the consultation creator.

Revision ID: b20260924
Revises: 92e938ce14e5
"""

import sqlalchemy as sa
from alembic import op

revision = "b20260924"
down_revision = "92e938ce14e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "consultations",
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_consultations_created_by_id_users",
        "consultations",
        "users",
        ["created_by_id"],
        ["id"],
    )
    op.execute(
        sa.text(
            """
            UPDATE consultations
            SET created_by_id = (
                SELECT id
                FROM users
                ORDER BY CASE WHEN role = 'ADMIN' THEN 0 ELSE 1 END, id
                LIMIT 1
            )
            WHERE created_by_id IS NULL
            """
        )
    )
    op.alter_column("consultations", "created_by_id", nullable=False)
    op.create_index(
        "ix_consultations_created_by_id",
        "consultations",
        ["created_by_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_consultations_created_by_id", table_name="consultations")
    op.drop_constraint(
        "fk_consultations_created_by_id_users",
        "consultations",
        type_="foreignkey",
    )
    op.drop_column("consultations", "created_by_id")
