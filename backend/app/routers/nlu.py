from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu_service import nlu_service

router = APIRouter()


class NLUResolveRequest(BaseModel):
    text: str
    lang: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class NLUResolveResponse(BaseModel):
    intent: str
    entities: Dict[str, Any]
    confidence: float


@router.post("/resolve", response_model=NLUResolveResponse)
def resolve(req: NLUResolveRequest) -> NLUResolveResponse:
    """Resolve intent and entities from Bangla text using NLU service"""
    result = nlu_service.resolve(req.text, req.context)
    
    return NLUResolveResponse(
        intent=result["intent"],
        entities=result["entities"],
        confidence=result["confidence"]
    )
