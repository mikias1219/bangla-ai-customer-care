from fastapi import APIRouter, Response, Depends
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Gauge, Histogram
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db

router = APIRouter()

# Request metrics
requests_total = Counter('bangla_requests_total', 'Total HTTP requests', ['endpoint', 'method', 'status'])
request_duration = Histogram('bangla_request_duration_seconds', 'Request duration in seconds', ['endpoint'])

# AI metrics
nlu_requests = Counter('bangla_nlu_requests_total', 'NLU processing requests', ['intent', 'confidence'])
dm_decisions = Counter('bangla_dm_decisions_total', 'Dialogue manager decisions', ['intent', 'action'])

# Channel metrics
messages_received = Counter('bangla_messages_received_total', 'Messages received by channel', ['channel'])
messages_sent = Counter('bangla_messages_sent_total', 'Messages sent by channel', ['channel'])

# System health metrics
db_connections = Gauge('bangla_db_connections_active', 'Active database connections')
redis_connections = Gauge('bangla_redis_connections_active', 'Active Redis connections')

# Conversation metrics
active_conversations = Gauge('bangla_conversations_active', 'Currently active conversations')
total_conversations = Counter('bangla_conversations_total', 'Total conversations created')
conversation_duration = Histogram('bangla_conversation_duration_seconds', 'Conversation duration')


@router.get("/metrics")
def metrics() -> Response:
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/analytics/overview")
@router.get("/admin/analytics/overview")
async def analytics_overview(db: AsyncSession = Depends(get_db)):
    """Analytics overview for dashboard"""
    try:
        # This would typically query actual metrics from database
        # For now, return mock data structure
        return {
            "total_conversations": 1250,
            "active_conversations": 45,
            "messages_today": 320,
            "avg_response_time": 2.3,
            "nlu_accuracy": 0.87,
            "fallback_rate": 0.12,
            "channel_breakdown": {
                "whatsapp": 45,
                "messenger": 30,
                "instagram": 15,
                "voice": 8,
                "webchat": 2
            },
            "top_intents": [
                {"intent": "order_status", "count": 156},
                {"intent": "product_inquiry", "count": 98},
                {"intent": "complaint", "count": 67},
                {"intent": "refund_request", "count": 45}
            ],
            "system_health": {
                "cpu_usage": 65.2,
                "memory_usage": 72.8,
                "db_connections": 12,
                "uptime_hours": 168
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/analytics/conversations")
@router.get("/admin/analytics/conversations")
async def conversation_analytics(
    days: int = 7,
    channel: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Conversation analytics with filtering"""
    try:
        # Mock conversation analytics data
        return {
            "period_days": days,
            "total_conversations": 892,
            "avg_conversation_length": 4.2,
            "avg_resolution_time": 8.5,
            "satisfaction_score": 4.1,
            "channel_stats": [
                {
                    "channel": "whatsapp",
                    "conversations": 425,
                    "avg_response_time": 2.1,
                    "resolution_rate": 0.89
                },
                {
                    "channel": "messenger",
                    "conversations": 298,
                    "avg_response_time": 2.8,
                    "resolution_rate": 0.92
                },
                {
                    "channel": "instagram",
                    "conversations": 169,
                    "avg_response_time": 3.2,
                    "resolution_rate": 0.85
                }
            ],
            "daily_stats": [
                {"date": "2024-01-01", "conversations": 45, "messages": 180},
                {"date": "2024-01-02", "conversations": 52, "messages": 203},
                # ... more days
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/analytics/ai-performance")
@router.get("/admin/analytics/ai-performance")
async def ai_performance_analytics(db: AsyncSession = Depends(get_db)):
    """AI performance and accuracy metrics"""
    try:
        return {
            "nlu_performance": {
                "overall_accuracy": 0.87,
                "intent_accuracy": 0.91,
                "entity_accuracy": 0.82,
                "confidence_distribution": {
                    "high": 0.65,
                    "medium": 0.25,
                    "low": 0.10
                }
            },
            "dialogue_performance": {
                "successful_resolutions": 0.78,
                "fallback_rate": 0.12,
                "escalation_rate": 0.08,
                "avg_turns_per_conversation": 3.2
            },
            "model_metrics": {
                "total_predictions": 15420,
                "correct_predictions": 13380,
                "false_positives": 1240,
                "false_negatives": 800
            }
        }
    except Exception as e:
        return {"error": str(e)}
