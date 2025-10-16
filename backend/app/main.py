from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers import health, nlu, dm, resolver, admin, intents, entities, conversations, templates, auth, products, orders, customers
from app.channels import whatsapp, webchat
from app.channels import meta as meta_channel
from app.channels import voice_twilio, voice_voip
from app.routers import metrics as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.api_version}")
    print(f"📊 Dashboard: http://localhost:5173")
    print(f"📚 API Docs: http://localhost:8000/docs")
    yield
    # Shutdown
    print("👋 Shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        lifespan=lifespan,
        description="Full-scale Bangla AI customer care platform with NLU, ASR, TTS, and multi-channel support"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core routers
    app.include_router(health.router, tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    # Metrics (expose both plain and /admin/* for dashboard compatibility)
    app.include_router(metrics_router.router, tags=["metrics"])  # /metrics, /analytics/*
    app.include_router(metrics_router.router, prefix="/admin", tags=["metrics"])  # /admin/analytics/*
    
    # AI routers
    app.include_router(nlu.router, prefix="/nlu", tags=["nlu"])
    app.include_router(dm.router, prefix="/dm", tags=["dialogue"])
    app.include_router(resolver.router, prefix="/resolver", tags=["resolver"])
    
    # Admin routers
    app.include_router(admin.router, prefix="/admin", tags=["admin"])
    app.include_router(intents.router, prefix="/admin/intents", tags=["intents"])
    app.include_router(entities.router, prefix="/admin/entities", tags=["entities"])
    app.include_router(conversations.router, prefix="/admin/conversations", tags=["conversations"])
    app.include_router(templates.router, prefix="/admin/templates", tags=["templates"])

    # E-commerce routers (routers already have /products, /orders, /customers prefixes)
    app.include_router(products.router, tags=["products"])
    app.include_router(orders.router, tags=["orders"])
    app.include_router(customers.router, tags=["customers"])
    
    # Channel adapters
    app.include_router(whatsapp.router, prefix="/channels/whatsapp", tags=["channels"])
    app.include_router(webchat.router, prefix="/channels/webchat", tags=["channels"])
    app.include_router(meta_channel.router, prefix="/channels/meta", tags=["channels"])  # Messenger & Instagram
    app.include_router(voice_twilio.router, prefix="/channels/voice/twilio", tags=["channels"])  # Twilio voice
    app.include_router(voice_voip.router, prefix="/channels/voice/voip", tags=["channels"])  # Asterisk/FreeSWITCH

    return app


app = create_app()
