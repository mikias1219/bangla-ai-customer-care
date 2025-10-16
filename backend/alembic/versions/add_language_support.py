"""Add language support and inbox separation

Revision ID: add_lang_support
Revises: add_ecommerce
Create Date: 2025-01-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_lang_support'
down_revision: Union[str, None] = 'add_ecommerce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to conversations table
    op.add_column('conversations', sa.Column('customer_name', sa.String(255), nullable=True))
    op.add_column('conversations', sa.Column('customer_language', sa.String(10), nullable=True, default='bn'))
    op.add_column('conversations', sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('(now() at time zone \'utc\')')))
    op.add_column('conversations', sa.Column('unread_count', sa.Integer(), nullable=True, default=0))

    # Add new column to turns table
    op.add_column('turns', sa.Column('text_language', sa.String(10), nullable=True))

    # Update existing records with default values
    op.execute("UPDATE conversations SET customer_language = 'bn' WHERE customer_language IS NULL")
    op.execute("UPDATE conversations SET unread_count = 0 WHERE unread_count IS NULL")
    op.execute("UPDATE conversations SET last_message_at = started_at WHERE last_message_at IS NULL")


def downgrade() -> None:
    # Remove added columns
    op.drop_column('turns', 'text_language')
    op.drop_column('conversations', 'unread_count')
    op.drop_column('conversations', 'last_message_at')
    op.drop_column('conversations', 'customer_language')
    op.drop_column('conversations', 'customer_name')
