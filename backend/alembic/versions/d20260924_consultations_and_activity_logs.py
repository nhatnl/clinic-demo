"""Create consultation and activity log tables.

Revision ID: d20260924
Revises: c7adbba40a58
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel.sql.sqltypes import AutoString

revision = "d20260924"
down_revision = "c7adbba40a58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consultations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("note", AutoString(), nullable=False),
    )
    op.create_index("ix_consultations_patient_id", "consultations", ["patient_id"])
    op.create_table(
        "consultation_diagnoses",
        sa.Column(
            "consultation_id", sa.Integer(), sa.ForeignKey("consultations.id"),
            primary_key=True,
        ),
        sa.Column(
            "diagnosis_code", AutoString(length=8), sa.ForeignKey("diagnoses.code"),
            primary_key=True,
        ),
    )
    op.create_index(
        "ix_consultation_diagnoses_diagnosis_code",
        "consultation_diagnoses",
        ["diagnosis_code"],
    )
    op.create_table(
        "activities_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("event", AutoString(length=50), nullable=False),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("activities_logs")
    op.drop_index("ix_consultation_diagnoses_diagnosis_code", "consultation_diagnoses")
    op.drop_table("consultation_diagnoses")
    op.drop_index("ix_consultations_patient_id", "consultations")
    op.drop_table("consultations")
