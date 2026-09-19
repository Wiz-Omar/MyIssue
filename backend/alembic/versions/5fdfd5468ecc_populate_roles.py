"""populate roles

Revision ID: 5fdfd5468ecc
Revises: d4557c79c377
Create Date: 2026-09-19 20:22:13.237903

"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '5fdfd5468ecc'
down_revision: str | Sequence[str] | None = 'd4557c79c377'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    roles_table = sa.table(
        "roles",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("role_name", sa.String),
    )
    op.bulk_insert(
        roles_table,
        [
            {"id": uuid.uuid4(), "role_name": "admin"},
            {"id": uuid.uuid4(), "role_name": "developer"}
        ],
    )    


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM roles WHERE role_name IN ('admin', 'member', 'viewer')")
