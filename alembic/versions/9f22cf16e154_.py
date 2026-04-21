"""change outbox.id from VARCHAR to UUID

Revision ID: 9f22cf16e154
Revises: 7c178fb5854e
Create Date: 2026-04-21 20:09:49.501819
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f22cf16e154"
down_revision: Union[str, Sequence[str], None] = "7c178fb5854e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("outbox", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.VARCHAR(),
            type_=sa.UUID(),
            existing_nullable=False,
            postgresql_using="id::uuid",  # ← это главное исправление
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("outbox", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.UUID(),
            type_=sa.VARCHAR(),
            existing_nullable=False,
            # для downgrade USING обычно не нужен
        )
