from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.base import get_db
from app.db.models import Conversation, Turn, ConversationStatus, TurnSpeaker

router = APIRouter()


class TurnResponse(BaseModel):
    id: int
    turn_index: int
    speaker: TurnSpeaker
    text: str
    intent: Optional[str]
    entities: Optional[Dict[str, Any]]
    asr_confidence: Optional[float]
    nlu_confidence: Optional[float]
    handoff_flag: bool
    timestamp: datetime
    turn_metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    conversation_id: str
    channel: str
    customer_id: Optional[str]
    status: ConversationStatus
    started_at: datetime
    ended_at: Optional[datetime]
    conversation_metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    turns: List[TurnResponse]


@router.get("/", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    channel: Optional[str] = None,
    status: Optional[ConversationStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Conversation)
    
    if channel:
        query = query.filter(Conversation.channel == channel)
    if status:
        query = query.filter(Conversation.status == status)
    
    conversations = query.order_by(Conversation.started_at.desc()).offset(skip).limit(limit).all()
    return conversations


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}/turns", response_model=List[TurnResponse])
def get_conversation_turns(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    turns = db.query(Turn).filter(Turn.conversation_id == conversation_id).order_by(Turn.turn_index).all()
    return turns

