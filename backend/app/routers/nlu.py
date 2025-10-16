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
    language: str
    model_used: Optional[str] = None


@router.post("/resolve", response_model=NLUResolveResponse)
async def resolve(req: NLUResolveRequest) -> NLUResolveResponse:
    """Resolve intent and entities from Bangla text using OpenAI-powered NLU service"""
    result = await nlu_service.resolve(req.text, req.context)

    return NLUResolveResponse(
        intent=result["intent"],
        entities=result["entities"],
        confidence=result["confidence"],
        language=result.get("language", "unknown"),
        model_used=result.get("model_used")
    )
