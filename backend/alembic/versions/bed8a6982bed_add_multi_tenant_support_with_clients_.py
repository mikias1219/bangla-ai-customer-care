"""Add multi-tenant support with clients, subscriptions, and tenant_id fields

Revision ID: bed8a6982bed
Revises: add_lang_support
Create Date: 2025-10-16 15:50:52.870868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bed8a6982bed'
down_revision = 'add_lang_support'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table('clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('business_email', sa.String(length=255), nullable=False),
        sa.Column('business_phone', sa.String(length=50), nullable=True),
        sa.Column('business_address', sa.Text(), nullable=True),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('business_type', sa.String(length=100), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('facebook_page_url', sa.String(length=500), nullable=True),
        sa.Column('instagram_username', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', 'trial', name='clientstatus'), nullable=True),
        sa.Column('subscription_plan', sa.Enum('basic', 'standard', 'premium', 'pay_as_you_go', name='subscriptionplan'), nullable=True),
        sa.Column('monthly_customers_limit', sa.Integer(), nullable=True),
        sa.Column('current_month_customers', sa.Integer(), nullable=True),
        sa.Column('ai_reply_balance', sa.Float(), nullable=True),
        sa.Column('ai_model_config', sa.JSON(), nullable=True),
        sa.Column('language_preference', sa.String(length=10), nullable=True),
        sa.Column('facebook_page_access_token', sa.Text(), nullable=True),
        sa.Column('instagram_access_token', sa.Text(), nullable=True),
        sa.Column('whatsapp_business_id', sa.String(length=100), nullable=True),
        sa.Column('whatsapp_access_token', sa.Text(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('bkash_wallet_number', sa.String(length=50), nullable=True),
        sa.Column('trial_started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('subscription_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subscription_renewal_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id'),
        sa.UniqueConstraint('business_email')
    )
    op.create_index(op.f('ix_clients_business_email'), 'clients', ['business_email'], unique=False)
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
    op.create_index(op.f('ix_clients_tenant_id'), 'clients', ['tenant_id'], unique=False)

    # Create client_users table
    op.create_table('client_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_client_users_id'), 'client_users', ['id'], unique=False)

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('plan', sa.Enum('basic', 'standard', 'premium', 'pay_as_you_go', name='subscriptionplan'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)

    # Create client_payments table
    op.create_table('client_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('payment_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('pending', 'paid', 'failed', 'refunded', name='paymentstatus'), nullable=True),
        sa.Column('gateway', sa.String(length=50), nullable=True),
        sa.Column('gateway_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('gateway_response', sa.JSON(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index(op.f('ix_client_payments_id'), 'client_payments', ['id'], unique=False)

    # Add tenant_id to existing tables
    tables_to_update = [
        'intents', 'entities', 'utterances', 'conversations', 'turns',
        'templates', 'integrations', 'users', 'training_jobs',
        'products', 'customers', 'orders', 'order_items', 'transactions'
    ]

    for table in tables_to_update:
        op.add_column(table, sa.Column('tenant_id', sa.String(length=36), nullable=True))
        op.create_index(f'ix_{table}_tenant_id', table, ['tenant_id'], unique=False)


def downgrade() -> None:
    # Drop new tables
    op.drop_table('client_payments')
    op.drop_table('subscriptions')
    op.drop_table('client_users')
    op.drop_table('clients')

    # Remove tenant_id from existing tables
    tables_to_update = [
        'intents', 'entities', 'utterances', 'conversations', 'turns',
        'templates', 'integrations', 'users', 'training_jobs',
        'products', 'customers', 'orders', 'order_items', 'transactions'
    ]

    for table in tables_to_update:
        op.drop_index(f'ix_{table}_tenant_id', table=table)
        op.drop_column(table, 'tenant_id')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS clientstatus')
    op.execute('DROP TYPE IF EXISTS subscriptionplan')
    op.execute('DROP TYPE IF EXISTS paymentstatus')

