from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.db.models_base import Base


# Multi-tenant models
class ClientStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    trial = "trial"


class SubscriptionPlan(str, enum.Enum):
    basic = "basic"      # 500 customers/month, Tk 3999
    standard = "standard"  # 1000 customers/month, Tk 7499
    premium = "premium"    # 2500 customers/month, Tk 17999
    pay_as_you_go = "pay_as_you_go"  # Tk 0.75 per reply


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    business_name = Column(String(255), nullable=False)
    business_email = Column(String(255), unique=True, nullable=False, index=True)
    business_phone = Column(String(50))
    business_address = Column(Text)
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))

    # Business details
    business_type = Column(String(100))  # restaurant, hotel, e-commerce, etc.
    website_url = Column(String(500))
    facebook_page_url = Column(String(500))
    instagram_username = Column(String(255))

    # Status and subscription
    status = Column(Enum(ClientStatus), default=ClientStatus.trial)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.pay_as_you_go)
    monthly_customers_limit = Column(Integer, default=100)  # Based on plan
    current_month_customers = Column(Integer, default=0)
    ai_reply_balance = Column(Float, default=500.0)  # For pay-as-you-go

    # AI Configuration
    ai_model_config = Column(JSON)  # Custom AI settings per client
    language_preference = Column(String(10), default="bn")  # bn, en, banglish, all

    # Social Media Tokens (encrypted)
    facebook_page_access_token = Column(Text)  # Encrypted
    instagram_access_token = Column(Text)  # Encrypted
    whatsapp_business_id = Column(String(100))
    whatsapp_access_token = Column(Text)  # Encrypted

    # Payment info
    stripe_customer_id = Column(String(100))
    bkash_wallet_number = Column(String(50))

    # Dates
    trial_started_at = Column(DateTime(timezone=True), server_default=func.now())
    subscription_started_at = Column(DateTime(timezone=True))
    subscription_renewal_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("ClientUser", back_populates="client", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="client", cascade="all, delete-orphan")
    payments = relationship("ClientPayment", back_populates="client", cascade="all, delete-orphan")


class ClientUser(Base):
    __tablename__ = "client_users"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="admin")  # admin, manager, agent
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="users")

    __table_args__ = (
        {"schema": None},  # No schema for client users
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="BDT")
    status = Column(String(50), default="active")  # active, cancelled, expired
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    auto_renew = Column(Boolean, default=True)
    stripe_subscription_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    client = relationship("Client", back_populates="subscriptions")


class ClientPayment(Base):
    __tablename__ = "client_payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    transaction_id = Column(String(100), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="BDT")
    payment_type = Column(String(50))  # subscription, topup, refund
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    gateway = Column(String(50))  # stripe, bkash, bank
    gateway_transaction_id = Column(String(100))
    gateway_response = Column(JSON)
    description = Column(String(500))
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    client = relationship("Client", back_populates="payments")


class IntentStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    draft = "draft"


class ConversationStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    escalated = "escalated"


class TurnSpeaker(str, enum.Enum):
    user = "user"
    bot = "bot"
    agent = "agent"


class Intent(Base):
    __tablename__ = "intents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(IntentStatus), default=IntentStatus.active)
    version = Column(Integer, default=1)
    examples_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    utterances = relationship("Utterance", back_populates="intent", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None},
    )


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    name = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50))  # regex, dictionary, ml
    pattern = Column(Text)  # regex pattern or JSON dictionary
    description = Column(Text)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        {"schema": None},
    )


class Utterance(Base):
    __tablename__ = "utterances"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    text = Column(Text, nullable=False)
    intent_id = Column(Integer, ForeignKey("intents.id"), nullable=False)
    entities = Column(JSON)  # Store extracted entities as JSON
    split = Column(String(20), default="train")  # train, dev, test
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    intent = relationship("Intent", back_populates="utterances")

    __table_args__ = (
        {"schema": None},
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    conversation_id = Column(String(100), nullable=False, index=True)
    channel = Column(String(50))  # whatsapp, messenger, instagram, voice, web, mobile
    customer_id = Column(String(100), index=True)
    customer_name = Column(String(255))
    customer_language = Column(String(10), default="bn")  # Detected language: bn, en, hi, ar, ur, etc.
    status = Column(Enum(ConversationStatus), default=ConversationStatus.active)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    unread_count = Column(Integer, default=0)
    conversation_data = Column(JSON)  # Store channel-specific metadata

    # Relationships
    turns = relationship("Turn", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None},
    )


class Turn(Base):
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    turn_index = Column(Integer, nullable=False)
    speaker = Column(Enum(TurnSpeaker), nullable=False)
    text = Column(Text, nullable=False)
    text_language = Column(String(10))  # Language of the text: bn, en, hi, ar, ur, etc.
    intent = Column(String(100))
    entities = Column(JSON)
    asr_confidence = Column(Float)
    nlu_confidence = Column(Float)
    handoff_flag = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    turn_data = Column(JSON)

    # Relationships
    conversation = relationship("Conversation", back_populates="turns")

    __table_args__ = (
        {"schema": None},
    )


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    key = Column(String(100), nullable=False, index=True)
    lang = Column(String(10), default="bn-BD")
    body = Column(Text, nullable=False)
    variables = Column(JSON)  # List of variable names expected
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        {"schema": None},
    )


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    name = Column(String(100), nullable=False, index=True)
    system = Column(String(50))  # crm, erp, inventory, etc.
    auth_method = Column(String(50))  # api_key, oauth, basic, mtls
    base_url = Column(String(500))
    secrets_ref = Column(String(200))  # Reference to secrets manager
    enabled = Column(Boolean, default=True)
    config = Column(JSON)  # Additional configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        {"schema": None},
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=True, index=True)  # Optional for backward compatibility, will be required for new clients
    username = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="viewer")  # admin, manager, agent, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        {"schema": None},
    )


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    job_type = Column(String(50))  # nlu, asr, tts
    status = Column(String(50))  # pending, running, completed, failed
    model_version = Column(String(50))
    metrics = Column(JSON)  # Store training metrics
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {"schema": None},
    )


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="BDT")
    category = Column(String(100))
    brand = Column(String(100))
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    weight = Column(Float)  # in kg
    dimensions = Column(JSON)  # {"length": 10, "width": 5, "height": 2}
    images = Column(JSON)  # Array of image URLs
    tags = Column(JSON)  # Array of tags
    product_metadata = Column(JSON)  # Additional product data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")

    __table_args__ = (
        {"schema": None},
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    customer_id = Column(String(100), nullable=False, index=True)  # External ID from channels
    name = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    channel = Column(String(50))  # whatsapp, messenger, instagram, etc.
    channel_user_id = Column(String(100))  # User ID from the channel
    profile_data = Column(JSON)  # Channel-specific profile information
    preferences = Column(JSON)  # Customer preferences
    tags = Column(JSON)  # Customer tags
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_order_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="customer")

    __table_args__ = (
        {"schema": None},
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    order_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    # Order details
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    currency = Column(String(10), default="BDT")

    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)

    # Shipping
    shipping_address = Column(JSON)
    shipping_method = Column(String(100))
    tracking_number = Column(String(100))

    # Payment
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    payment_gateway = Column(String(50))

    # Dates
    ordered_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))

    # Additional data
    notes = Column(Text)
    order_metadata = Column(JSON)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    conversation = relationship("Conversation", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None},
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Item details
    product_name = Column(String(255), nullable=False)  # Snapshot of product name
    product_sku = Column(String(100), nullable=False)   # Snapshot of product SKU
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Additional data
    product_options = Column(JSON)  # Size, color, etc.
    notes = Column(Text)
    item_metadata = Column(JSON)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    __table_args__ = (
        {"schema": None},
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)  # Multi-tenant support
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="BDT")
    transaction_type = Column(String(50))  # payment, refund, chargeback
    status = Column(String(50))  # pending, completed, failed, cancelled
    gateway = Column(String(50))  # stripe, paypal, bKash, etc.
    gateway_transaction_id = Column(String(100))
    gateway_response = Column(JSON)

    # Dates
    initiated_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))

    # Additional data
    notes = Column(Text)
    transaction_metadata = Column(JSON)

    # Relationships
    order = relationship("Order", backref="transactions")

    __table_args__ = (
        {"schema": None},
    )


# Social Media Management Models
class SocialMediaAccount(Base):
    __tablename__ = "social_media_accounts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    # Platform details
    platform = Column(String(50), nullable=False)  # 'facebook', 'instagram', 'whatsapp'
    account_id = Column(String(255), nullable=False)  # Platform-specific account ID
    account_name = Column(String(255), nullable=False)  # Display name

    # Authentication
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", backref="social_media_accounts")
    posts = relationship("SocialMediaPost", back_populates="account")

    __table_args__ = (
        {"schema": None},
    )


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("social_media_accounts.id"), nullable=False)

    # Content
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)  # List of media URLs
    hashtags = Column(JSON, default=list)  # List of hashtags

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True))

    # Status and metrics
    status = Column(String(50), default="draft")  # draft, scheduled, posted, failed
    engagement_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    impression_count = Column(Integer, default=0)

    # Platform-specific post ID
    platform_post_id = Column(String(255))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("SocialMediaAccount", back_populates="posts")

    __table_args__ = (
        {"schema": None},
    )


class SocialMediaAnalytics(Base):
    __tablename__ = "social_media_analytics"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("social_media_accounts.id"), nullable=False)

    # Analytics data
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Detailed metrics
    reach_total = Column(Integer, default=0)
    impressions_total = Column(Integer, default=0)
    likes_total = Column(Integer, default=0)
    comments_total = Column(Integer, default=0)
    shares_total = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("SocialMediaAccount", backref="analytics")

    __table_args__ = (
        {"schema": None},
    )

