"""add server_default to stock

Revision ID: 0ff37c5aee19
Revises: ace5ef00cc7c
Create Date: 2026-07-12 16:10:41.252667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ff37c5aee19'
down_revision: Union[str, None] = 'ace5ef00cc7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('stock', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('stock', 'updated_at',
                    server_default=sa.text('now()'),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('stock', 'updated_at',
                    server_default=None,
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=False)
    op.drop_column('stock', 'created_at')
