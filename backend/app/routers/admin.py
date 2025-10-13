from typing import Any, Dict
from fastapi import APIRouter

router = APIRouter()


@router.get("/config")
def get_config() -> Dict[str, Any]:
    return {
        "intents": ["order_status", "return_request", "fallback"],
        "entities": ["order_id", "date"],
        "version": 1,
    }


@router.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    return {
        "requests_total": 0,
        "nlu_accuracy": 0.0,
        "fallback_rate": 0.0,
    }
