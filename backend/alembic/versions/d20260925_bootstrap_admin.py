"""Bootstrap or rotate the admin without a repository password.

Revision ID: d20260925
Revises: b20260924
"""

import os
import secrets
import sys

import sqlalchemy as sa
from alembic import op
from pydantic import ValidationError
from pwdlib import PasswordHash

from src.auth.schemas import SignIn

revision = "d20260925"
down_revision = "b20260924"
branch_labels = None
depends_on = None

ADMIN_EMAIL = "admin@kyanon.digital"


def upgrade() -> None:
    configured = os.getenv("ADMIN_PASSWORD")
    password = configured or f"Aa1!{secrets.token_urlsafe(18)}"
    try:
        SignIn(email=ADMIN_EMAIL, password=password)
    except ValidationError:
        raise ValueError(
            "ADMIN_PASSWORD must be at least 6 characters and contain "
            "uppercase, lowercase, number, and special characters without spaces"
        ) from None
    password_hash = PasswordHash.recommended().hash(password)

    op.execute(
        sa.text("UPDATE users SET password_hash = :hash WHERE email = :email").bindparams(
            hash=password_hash, email=ADMIN_EMAIL
        )
    )
    op.execute(
        sa.text(
            """INSERT INTO users (created_at, updated_at, email, status, role, password_hash)
            SELECT CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :email, 'ACTIVE', 'ADMIN', :hash
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = :email)"""
        ).bindparams(hash=password_hash, email=ADMIN_EMAIL)
    )

    if not configured:
        print(
            f"Generated admin password for {ADMIN_EMAIL}: {password}",
            file=sys.stderr,
            flush=True,
        )


def downgrade() -> None:
    # Retain the admin account and its password on schema rollback.
    pass
