from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

router = APIRouter()

# Example counter
requests_total = Counter('bangla_requests_total', 'Total HTTP requests', ['endpoint'])


@router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
