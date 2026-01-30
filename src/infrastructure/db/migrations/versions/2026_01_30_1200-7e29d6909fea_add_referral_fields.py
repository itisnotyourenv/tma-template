"""add_referral_fields

Revision ID: 7e29d6909fea
Revises: 80231256407c
Create Date: 2026-01-30 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e29d6909fea"
down_revision: str | Sequence[str] | None = "80231256407c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("referred_by", sa.BIGINT(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "referral_count",
            sa.INTEGER(),
            server_default="0",
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_users_referred_by",
        "users",
        "users",
        ["referred_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_users_referred_by", "users", ["referred_by"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_users_referred_by", table_name="users")
    op.drop_constraint("fk_users_referred_by", "users", type_="foreignkey")
    op.drop_column("users", "referral_count")
    op.drop_column("users", "referred_by")
