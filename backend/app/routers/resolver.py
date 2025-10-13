from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.resolver_service import resolver_service

router = APIRouter()


class ResolverRequest(BaseModel):
    data: Dict[str, Any]


class ResolverResponse(BaseModel):
    data: Dict[str, Any]
    message: str


@router.post("/{name}", response_model=ResolverResponse)
async def run_resolver(name: str, req: ResolverRequest) -> ResolverResponse:
    result = await resolver_service.resolve(name, req.data)
    return ResolverResponse(
        data={"resolver": name, "result": result},
        message="Resolver executed",
    )
