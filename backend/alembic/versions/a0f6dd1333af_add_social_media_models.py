"""add_social_media_models

Revision ID: a0f6dd1333af
Revises: bed8a6982bed
Create Date: 2025-10-17 07:31:48.825653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0f6dd1333af'
down_revision = 'bed8a6982bed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create social_media_accounts table
    op.create_table('social_media_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('account_id', sa.String(length=255), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_media_accounts_id'), 'social_media_accounts', ['id'], unique=False)

    # Create social_media_posts table
    op.create_table('social_media_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('media_urls', sa.JSON(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('engagement_count', sa.Integer(), nullable=True),
        sa.Column('reach_count', sa.Integer(), nullable=True),
        sa.Column('impression_count', sa.Integer(), nullable=True),
        sa.Column('platform_post_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['social_media_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_media_posts_id'), 'social_media_posts', ['id'], unique=False)

    # Create social_media_analytics table
    op.create_table('social_media_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('followers_count', sa.Integer(), nullable=True),
        sa.Column('following_count', sa.Integer(), nullable=True),
        sa.Column('posts_count', sa.Integer(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reach_total', sa.Integer(), nullable=True),
        sa.Column('impressions_total', sa.Integer(), nullable=True),
        sa.Column('likes_total', sa.Integer(), nullable=True),
        sa.Column('comments_total', sa.Integer(), nullable=True),
        sa.Column('shares_total', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['social_media_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_media_analytics_id'), 'social_media_analytics', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_social_media_analytics_id'), table_name='social_media_analytics')
    op.drop_table('social_media_analytics')
    op.drop_index(op.f('ix_social_media_posts_id'), table_name='social_media_posts')
    op.drop_table('social_media_posts')
    op.drop_index(op.f('ix_social_media_accounts_id'), table_name='social_media_accounts')
    op.drop_table('social_media_accounts')

