"""update_patient_table

Revision ID: 92e938ce14e5
Revises: d20260924
Create Date: 2026-09-24 14:24:07.196244

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "92e938ce14e5"
down_revision: Union[str, Sequence[str], None] = "d20260924"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "patients",
        sa.Column(
            "first_name", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True
        ),
    )
    op.add_column(
        "patients",
        sa.Column(
            "last_name", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True
        ),
    )

    gender_enum = postgresql.ENUM("MALE", "FEMALE", "NO_PROVIDED", name="genders")
    gender_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "patients",
        sa.Column(
            "gender",
            sa.Enum("MALE", "FEMALE", "NO_PROVIDED", name="genders", create_type=False),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE patients
            SET first_name = left(
                    coalesce(nullif(split_part(trim(name), ' ', 1), ''), 'Unknown'),
                    20
                ),
                last_name = left(
                    coalesce(
                        nullif(
                            trim(substr(trim(name), strpos(trim(name), ' ') + 1)),
                            ''
                        ),
                        nullif(split_part(trim(name), ' ', 1), ''),
                        'Unknown'
                    ),
                    20
                )
            """
        )
    )
    op.alter_column("patients", "first_name", nullable=False)
    op.alter_column("patients", "last_name", nullable=False)
    op.drop_column("patients", "name")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "patients",
        sa.Column("name", sa.VARCHAR(length=50), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE patients
            SET name = left(trim(first_name || ' ' || last_name), 50)
            """
        )
    )
    op.alter_column("patients", "name", nullable=False)
    op.drop_column("patients", "gender")
    op.drop_column("patients", "last_name")
    op.drop_column("patients", "first_name")
    postgresql.ENUM("MALE", "FEMALE", "NO_PROVIDED", name="genders").drop(
        op.get_bind(), checkfirst=True
    )
