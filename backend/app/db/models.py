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
    conversation_metadata = Column(JSON)  # Store channel-specific metadata

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
    turn_metadata = Column(JSON)

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

