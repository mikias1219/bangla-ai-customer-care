from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.dialogue_manager import dialogue_manager

router = APIRouter()


class DMDecideRequest(BaseModel):
    intent: str
    entities: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


class DMDecideResponse(BaseModel):
    action: str
    response_text_bn: str
    metadata: Dict[str, Any] = {}


@router.post("/decide", response_model=DMDecideResponse)
def decide(req: DMDecideRequest) -> DMDecideResponse:
    """Make dialogue decision using dialogue manager"""
    result = dialogue_manager.decide(
        intent=req.intent,
        entities=req.entities,
        context=req.context
    )
    
    return DMDecideResponse(
        action=result["action"],
        response_text_bn=result["response_text_bn"],
        metadata=result["metadata"]
    )
