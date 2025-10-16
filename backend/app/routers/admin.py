from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.db.base import get_db
from app.db.models import (
    Conversation, Turn, Intent, Entity, Utterance,
    User, TrainingJob, Customer, Order, Product, Transaction
)

router = APIRouter()


@router.get("/config")
def get_config() -> Dict[str, Any]:
    """Get system configuration and capabilities"""
    return {
        "intents": [
            "order_status", "return_request", "product_inquiry",
            "payment_issue", "delivery_tracking", "complaint",
            "cancel_order", "modify_order", "refund_status", "customer_support", "fallback"
        ],
        "entities": [
            "order_id", "product_name", "phone", "amount",
            "email", "date", "address", "quantity", "payment_method"
        ],
        "supported_languages": ["en", "bn", "hi", "ar", "ur"],
        "ai_models": {
            "nlu": "gpt-4o-mini",
            "asr": "whisper-1",
            "tts": "openai-tts"
        },
        "version": "2.0.0",
        "features": [
            "multi_language_support", "voice_calls", "real_time_chat",
            "admin_dashboard", "analytics", "human_handoff"
        ]
    }


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get comprehensive system metrics and analytics"""

    # Time-based metrics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Conversation metrics
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    active_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status == "active"
    ).scalar()
    escalated_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status == "escalated"
    ).scalar()

    # Recent conversations (last 30 days)
    recent_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.started_at >= thirty_days_ago
    ).scalar()

    # Turn metrics
    total_turns = db.query(func.count(Turn.id)).scalar()
    avg_turns_per_conversation = total_turns / max(total_conversations, 1)

    # Intent distribution
    intent_counts = db.query(
        Turn.intent, func.count(Turn.id)
    ).filter(
        Turn.intent.isnot(None)
    ).group_by(Turn.intent).all()

    # Language distribution
    language_counts = db.query(
        Turn.turn_data['language'].astext, func.count(Turn.id)
    ).filter(
        Turn.turn_data.isnot(None)
    ).group_by(Turn.turn_data['language'].astext).all()

    # NLU confidence metrics
    avg_nlu_confidence = db.query(func.avg(Turn.nlu_confidence)).filter(
        Turn.nlu_confidence.isnot(None)
    ).scalar() or 0.0

    # Customer metrics
    total_customers = db.query(func.count(Customer.id)).scalar()
    new_customers_30d = db.query(func.count(Customer.id)).filter(
        Customer.created_at >= thirty_days_ago
    ).scalar()

    # Order metrics
    total_orders = db.query(func.count(Order.id)).scalar()
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == "pending"
    ).scalar()

    # Product metrics
    total_products = db.query(func.count(Product.id)).scalar()
    low_stock_products = db.query(func.count(Product.id)).filter(
        Product.stock_quantity <= Product.min_stock_level
    ).scalar()

    # Training metrics
    total_training_jobs = db.query(func.count(TrainingJob.id)).scalar()
    completed_training_jobs = db.query(func.count(TrainingJob.id)).filter(
        TrainingJob.status == "completed"
    ).scalar()

    return {
        "conversations": {
            "total": total_conversations,
            "active": active_conversations,
            "escalated": escalated_conversations,
            "recent_30d": recent_conversations,
            "avg_turns_per_conversation": round(avg_turns_per_conversation, 2)
        },
        "nlu_performance": {
            "avg_confidence": round(avg_nlu_confidence, 3),
            "intent_distribution": dict(intent_counts),
            "language_distribution": dict(language_counts)
        },
        "business_metrics": {
            "total_customers": total_customers,
            "new_customers_30d": new_customers_30d,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "total_products": total_products,
            "low_stock_products": low_stock_products
        },
        "system_health": {
            "training_jobs_total": total_training_jobs,
            "training_jobs_completed": completed_training_jobs,
            "fallback_rate": round(escalated_conversations / max(total_conversations, 1), 3)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/analytics/conversations")
def get_conversation_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed conversation analytics"""

    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily conversation counts
    daily_counts = db.query(
        func.date(Conversation.started_at), func.count(Conversation.id)
    ).filter(
        Conversation.started_at >= start_date
    ).group_by(
        func.date(Conversation.started_at)
    ).order_by(func.date(Conversation.started_at)).all()

    # Channel distribution
    channel_counts = db.query(
        Conversation.channel, func.count(Conversation.id)
    ).group_by(Conversation.channel).all()

    # Status distribution
    status_counts = db.query(
        Conversation.status, func.count(Conversation.id)
    ).group_by(Conversation.status).all()

    return {
        "daily_conversations": [{"date": str(date), "count": count} for date, count in daily_counts],
        "channel_distribution": dict(channel_counts),
        "status_distribution": dict(status_counts),
        "period_days": days
    }


@router.get("/analytics/intents")
def get_intent_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get intent recognition analytics"""

    start_date = datetime.utcnow() - timedelta(days=days)

    # Intent frequency over time
    intent_trends = db.query(
        func.date(Turn.timestamp), Turn.intent, func.count(Turn.id)
    ).filter(
        Turn.timestamp >= start_date,
        Turn.intent.isnot(None)
    ).group_by(
        func.date(Turn.timestamp), Turn.intent
    ).order_by(func.date(Turn.timestamp)).all()

    # Confidence distribution
    confidence_ranges = db.query(
        func.floor(Turn.nlu_confidence * 10) / 10, func.count(Turn.id)
    ).filter(
        Turn.nlu_confidence.isnot(None)
    ).group_by(func.floor(Turn.nlu_confidence * 10) / 10).all()

    return {
        "intent_trends": [
            {"date": str(date), "intent": intent, "count": count}
            for date, intent, count in intent_trends
        ],
        "confidence_distribution": {
            f"{round(conf * 10) / 10:.1f}": count
            for conf, count in confidence_ranges
        },
        "period_days": days
    }


@router.get("/system/status")
def get_system_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get system health and status information"""

    # Check database connectivity
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Recent training jobs
    recent_jobs = db.query(TrainingJob).order_by(
        desc(TrainingJob.created_at)
    ).limit(5).all()

    return {
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "recent_training_jobs": [
            {
                "id": job.id,
                "type": job.job_type,
                "status": job.status,
                "created_at": job.created_at.isoformat()
            }
            for job in recent_jobs
        ],
        "supported_features": [
            "multi_language_nlu", "voice_asr_tts", "real_time_chat",
            "admin_analytics", "human_handoff", "continuous_learning"
        ]
    }
