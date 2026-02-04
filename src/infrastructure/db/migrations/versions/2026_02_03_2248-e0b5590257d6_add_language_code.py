"""add_language_code

Revision ID: e0b5590257d6
Revises: 7e29d6909fea
Create Date: 2026-02-03 22:48:05.118496

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e0b5590257d6"
down_revision: str | Sequence[str] | None = "7e29d6909fea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add language_code column to users table."""
    op.add_column(
        "users",
        sa.Column("language_code", sa.String(5), server_default="en", nullable=True),
    )


def downgrade() -> None:
    """Remove language_code column from users table."""
    op.drop_column("users", "language_code")
