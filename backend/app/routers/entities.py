from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Entity

router = APIRouter()


class EntityCreate(BaseModel):
    name: str
    entity_type: str
    pattern: Optional[str] = None
    description: Optional[str] = None


class EntityUpdate(BaseModel):
    name: Optional[str] = None
    entity_type: Optional[str] = None
    pattern: Optional[str] = None
    description: Optional[str] = None


class EntityResponse(BaseModel):
    id: int
    name: str
    entity_type: str
    pattern: Optional[str]
    description: Optional[str]
    version: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[EntityResponse])
def list_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entities = db.query(Entity).offset(skip).limit(limit).all()
    return entities


@router.post("/", response_model=EntityResponse)
def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    db_entity = Entity(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(entity_id: int, entity_update: EntityUpdate, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    for key, value in entity_update.dict(exclude_unset=True).items():
        setattr(entity, key, value)
    
    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/{entity_id}")
def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    db.delete(entity)
    db.commit()
    return {"message": "Entity deleted successfully"}

