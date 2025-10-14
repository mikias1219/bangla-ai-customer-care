from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.base import Base


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
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(IntentStatus), default=IntentStatus.active)
    version = Column(Integer, default=1)
    examples_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    utterances = relationship("Utterance", back_populates="intent", cascade="all, delete-orphan")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    entity_type = Column(String(50))  # regex, dictionary, ml
    pattern = Column(Text)  # regex pattern or JSON dictionary
    description = Column(Text)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Utterance(Base):
    __tablename__ = "utterances"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    intent_id = Column(Integer, ForeignKey("intents.id"), nullable=False)
    entities = Column(JSON)  # Store extracted entities as JSON
    split = Column(String(20), default="train")  # train, dev, test
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    intent = relationship("Intent", back_populates="utterances")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), unique=True, nullable=False, index=True)
    channel = Column(String(50))  # voice, whatsapp, messenger, web, mobile
    customer_id = Column(String(100), index=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.active)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    conversation_data = Column(JSON)  # Store channel-specific metadata

    # Relationships
    turns = relationship("Turn", back_populates="conversation", cascade="all, delete-orphan")


class Turn(Base):
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    turn_index = Column(Integer, nullable=False)
    speaker = Column(Enum(TurnSpeaker), nullable=False)
    text = Column(Text, nullable=False)
    intent = Column(String(100))
    entities = Column(JSON)
    asr_confidence = Column(Float)
    nlu_confidence = Column(Float)
    handoff_flag = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    turn_data = Column(JSON)

    # Relationships
    conversation = relationship("Conversation", back_populates="turns")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    lang = Column(String(10), default="bn-BD")
    body = Column(Text, nullable=False)
    variables = Column(JSON)  # List of variable names expected
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    system = Column(String(50))  # crm, erp, inventory, etc.
    auth_method = Column(String(50))  # api_key, oauth, basic, mtls
    base_url = Column(String(500))
    secrets_ref = Column(String(200))  # Reference to secrets manager
    enabled = Column(Boolean, default=True)
    config = Column(JSON)  # Additional configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="viewer")  # admin, manager, agent, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(50))  # nlu, asr, tts
    status = Column(String(50))  # pending, running, completed, failed
    model_version = Column(String(50))
    metrics = Column(JSON)  # Store training metrics
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
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


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(100), unique=True, nullable=False, index=True)  # External ID from channels
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


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
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


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
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


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
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

