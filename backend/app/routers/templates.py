from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Template

router = APIRouter()


class TemplateCreate(BaseModel):
    key: str
    lang: str = "bn-BD"
    body: str
    variables: Optional[List[str]] = None


class TemplateUpdate(BaseModel):
    key: Optional[str] = None
    lang: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[List[str]] = None


class TemplateResponse(BaseModel):
    id: int
    key: str
    lang: str
    body: str
    variables: Optional[Dict[str, Any]]
    version: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TemplateResponse])
def list_templates(skip: int = 0, limit: int = 100, lang: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Template)
    if lang:
        query = query.filter(Template.lang == lang)
    templates = query.offset(skip).limit(limit).all()
    return templates


@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    db_template = Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template_update: TemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in template_update.dict(exclude_unset=True).items():
        setattr(template, key, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}

