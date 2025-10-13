from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Intent, IntentStatus

router = APIRouter()


class IntentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: IntentStatus = IntentStatus.active


class IntentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IntentStatus] = None


class IntentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: IntentStatus
    version: int
    examples_count: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[IntentResponse])
def list_intents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    intents = db.query(Intent).offset(skip).limit(limit).all()
    return intents


@router.post("/", response_model=IntentResponse)
def create_intent(intent: IntentCreate, db: Session = Depends(get_db)):
    db_intent = Intent(**intent.dict())
    db.add(db_intent)
    db.commit()
    db.refresh(db_intent)
    return db_intent


@router.get("/{intent_id}", response_model=IntentResponse)
def get_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.id == intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent


@router.put("/{intent_id}", response_model=IntentResponse)
def update_intent(intent_id: int, intent_update: IntentUpdate, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.id == intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    for key, value in intent_update.dict(exclude_unset=True).items():
        setattr(intent, key, value)
    
    db.commit()
    db.refresh(intent)
    return intent


@router.delete("/{intent_id}")
def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.id == intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    db.delete(intent)
    db.commit()
    return {"message": "Intent deleted successfully"}

