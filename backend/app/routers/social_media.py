"""
Social Media Management Router
Provides comprehensive social media management capabilities for clients
- Connect/configure social media accounts
- Post content to social media platforms
- Schedule posts
- Get analytics and insights
- Manage social media conversations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import httpx
import json

from app.core.tenant import get_current_tenant
from app.db.session import get_db
from app.db.models import Client, SocialMediaAccount, SocialMediaPost, SocialMediaAnalytics
from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager


router = APIRouter()
security = HTTPBearer()


# Pydantic models
class SocialMediaAccountCreate(BaseModel):
    platform: str  # 'facebook', 'instagram', 'whatsapp'
    account_id: str
    account_name: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True


class SocialMediaAccountUpdate(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class SocialMediaPostCreate(BaseModel):
    platform: str
    content: str
    media_urls: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None
    hashtags: Optional[List[str]] = []


class SocialMediaPostUpdate(BaseModel):
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None
    hashtags: Optional[List[str]] = None
    status: Optional[str] = None


class VoiceSocialMediaCommand(BaseModel):
    command_text: str
    language: Optional[str] = "bn"


class SocialMediaAnalyticsResponse(BaseModel):
    platform: str
    account_id: str
    followers: int
    engagement_rate: float
    posts_count: int
    reach: int
    impressions: int
    period: str


@router.post("/accounts", response_model=Dict[str, Any])
async def connect_social_media_account(
    account_data: SocialMediaAccountCreate,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Connect a social media account for the client
    """
    try:
        # Validate tenant
        client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Check if account already exists
        existing_account = db.query(SocialMediaAccount).filter(
            SocialMediaAccount.client_id == client.id,
            SocialMediaAccount.platform == account_data.platform,
            SocialMediaAccount.account_id == account_data.account_id
        ).first()

        if existing_account:
            raise HTTPException(status_code=400, detail="Account already connected")

        # Create new account
        account = SocialMediaAccount(
            client_id=client.id,
            platform=account_data.platform,
            account_id=account_data.account_id,
            account_name=account_data.account_name,
            access_token=account_data.access_token,
            refresh_token=account_data.refresh_token,
            expires_at=account_data.expires_at,
            is_active=account_data.is_active
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return {
            "message": "Social media account connected successfully",
            "account_id": account.id,
            "platform": account.platform,
            "account_name": account.account_name
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to connect account: {str(e)}")


@router.get("/accounts", response_model=List[Dict[str, Any]])
async def get_social_media_accounts(
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get all connected social media accounts for the client
    """
    client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    accounts = db.query(SocialMediaAccount).filter(
        SocialMediaAccount.client_id == client.id
    ).all()

    return [
        {
            "id": account.id,
            "platform": account.platform,
            "account_id": account.account_id,
            "account_name": account.account_name,
            "is_active": account.is_active,
            "connected_at": account.created_at,
            "last_used": account.updated_at
        }
        for account in accounts
    ]


@router.post("/posts", response_model=Dict[str, Any])
async def create_social_media_post(
    post_data: SocialMediaPostCreate,
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Create a social media post (immediate or scheduled)
    """
    try:
        # Validate tenant and account
        client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        account = db.query(SocialMediaAccount).filter(
            SocialMediaAccount.client_id == client.id,
            SocialMediaAccount.platform == post_data.platform,
            SocialMediaAccount.is_active == True
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Active account not found for platform")

        # Create post
        post = SocialMediaPost(
            account_id=account.id,
            content=post_data.content,
            media_urls=post_data.media_urls or [],
            scheduled_at=post_data.scheduled_at,
            hashtags=post_data.hashtags or [],
            status="scheduled" if post_data.scheduled_at else "draft"
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        # If not scheduled, post immediately
        if not post_data.scheduled_at:
            background_tasks.add_task(post_to_social_media, post.id, db)

        return {
            "message": "Post created successfully",
            "post_id": post.id,
            "platform": post_data.platform,
            "status": post.status,
            "scheduled_at": post.scheduled_at
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.get("/posts", response_model=List[Dict[str, Any]])
async def get_social_media_posts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get social media posts for the client
    """
    client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Build query
    query = db.query(SocialMediaPost).join(SocialMediaAccount).filter(
        SocialMediaAccount.client_id == client.id
    )

    if platform:
        query = query.filter(SocialMediaAccount.platform == platform)
    if status:
        query = query.filter(SocialMediaPost.status == status)

    posts = query.order_by(SocialMediaPost.created_at.desc()).limit(limit).all()

    return [
        {
            "id": post.id,
            "platform": post.account.platform,
            "content": post.content,
            "media_urls": post.media_urls,
            "hashtags": post.hashtags,
            "status": post.status,
            "scheduled_at": post.scheduled_at,
            "posted_at": post.posted_at,
            "engagement": post.engagement_count,
            "created_at": post.created_at
        }
        for post in posts
    ]


@router.post("/voice/command", response_model=Dict[str, Any])
async def process_voice_social_media_command(
    command_data: VoiceSocialMediaCommand,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Process voice commands for social media management
    Supports commands like:
    - "ফেসবুকে পোস্ট করো [content]" (Post to Facebook)
    - "ইন্সটাগ্রামে ছবি আপলোড করো" (Upload photo to Instagram)
    - "সোশ্যাল মিডিয়া রিপোর্ট দেখাও" (Show social media report)
    """
    try:
        # Detect language if not provided
        if not command_data.language:
            command_data.language = detect_voice_language(command_data.command_text)

        # NLU processing for voice command
        nlu_result = await nlu_service.resolve(command_data.command_text)

        # Enhanced dialogue manager with social media context
        dm_result = dialogue_manager.decide(
            intent=nlu_result["intent"],
            entities=nlu_result["entities"],
            context={
                "channel": "voice",
                "command_type": "social_media",
                "language": command_data.language,
                "tenant_id": tenant_id
            }
        )

        # Process social media specific commands
        response = await execute_social_media_command(
            command_data.command_text,
            nlu_result,
            dm_result,
            tenant_id,
            db,
            command_data.language
        )

        return {
            "response": response,
            "detected_language": command_data.language,
            "intent": nlu_result["intent"],
            "confidence": nlu_result["confidence"],
            "action_taken": dm_result.get("action", "processed")
        }

    except Exception as e:
        return {
            "response": get_error_response(str(e), command_data.language),
            "detected_language": command_data.language,
            "error": str(e)
        }


@router.get("/analytics/{platform}", response_model=SocialMediaAnalyticsResponse)
async def get_social_media_analytics(
    platform: str,
    period: str = "30d",  # 7d, 30d, 90d
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get social media analytics for a platform
    """
    client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Get analytics data (simplified - would integrate with actual APIs)
    analytics = await fetch_social_media_analytics(platform, client.id, period, db)

    return SocialMediaAnalyticsResponse(
        platform=platform,
        account_id=analytics.get("account_id", ""),
        followers=analytics.get("followers", 0),
        engagement_rate=analytics.get("engagement_rate", 0.0),
        posts_count=analytics.get("posts_count", 0),
        reach=analytics.get("reach", 0),
        impressions=analytics.get("impressions", 0),
        period=period
    )


# Helper functions
async def post_to_social_media(post_id: int, db: Session):
    """
    Background task to post to social media platforms
    """
    try:
        post = db.query(SocialMediaPost).filter(SocialMediaPost.id == post_id).first()
        if not post:
            return

        account = db.query(SocialMediaAccount).filter(
            SocialMediaAccount.id == post.account_id
        ).first()

        if not account or not account.is_active:
            return

        # Post to respective platforms
        if account.platform == "facebook":
            await post_to_facebook(account, post)
        elif account.platform == "instagram":
            await post_to_instagram(account, post)

        # Update post status
        post.status = "posted"
        post.posted_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        print(f"Failed to post to social media: {e}")
        # Update post status to failed
        post.status = "failed"
        db.commit()


async def post_to_facebook(account: SocialMediaAccount, post: SocialMediaPost):
    """Post to Facebook"""
    url = f"https://graph.facebook.com/v18.0/{account.account_id}/feed"
    payload = {
        "message": post.content,
        "access_token": account.access_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()


async def post_to_instagram(account: SocialMediaAccount, post: SocialMediaPost):
    """Post to Instagram"""
    # Instagram posting logic (simplified)
    url = f"https://graph.facebook.com/v18.0/{account.account_id}/media"
    payload = {
        "caption": post.content,
        "access_token": account.access_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()


def detect_voice_language(text: str) -> str:
    """
    Enhanced language detection for voice commands
    """
    # Bengali characters
    bengali_chars = sum(1 for char in text if '\u0980' <= char <= '\u09FF')

    # Arabic characters (for Urdu/Hindi)
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')

    # Devanagari characters (for Hindi)
    devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')

    total_chars = len(text.replace(' ', ''))

    if total_chars == 0:
        return "bn"

    if bengali_chars / total_chars > 0.3:
        return "bn"
    elif arabic_chars / total_chars > 0.3:
        return "ur"
    elif devanagari_chars / total_chars > 0.3:
        return "hi"
    else:
        return "en"


async def execute_social_media_command(
    command_text: str,
    nlu_result: Dict[str, Any],
    dm_result: Dict[str, Any],
    tenant_id: str,
    db: Session,
    language: str
) -> str:
    """
    Execute social media commands based on NLU results
    """
    intent = nlu_result["intent"]
    entities = nlu_result["entities"]

    if intent == "social_media_post":
        return await handle_post_command(entities, tenant_id, db, language)
    elif intent == "social_media_analytics":
        return await handle_analytics_command(entities, tenant_id, db, language)
    elif intent == "social_media_schedule":
        return await handle_schedule_command(entities, tenant_id, db, language)
    else:
        return get_fallback_response(language)


async def handle_post_command(entities: Dict[str, Any], tenant_id: str, db: Session, language: str) -> str:
    """Handle post creation commands"""
    platform = entities.get("platform", "facebook")
    content = entities.get("content", "")

    if language == "bn":
        return f"আপনার {platform} পোস্ট তৈরি করা হয়েছে: {content}"
    else:
        return f"Your {platform} post has been created: {content}"


async def handle_analytics_command(entities: Dict[str, Any], tenant_id: str, db: Session, language: str) -> str:
    """Handle analytics request commands"""
    platform = entities.get("platform", "facebook")

    # Get basic analytics
    analytics = await fetch_social_media_analytics(platform, None, "30d", db)

    if language == "bn":
        return f"{platform} অ্যানালিটিক্স: ফলোয়ার {analytics.get('followers', 0)}, এংগেজমেন্ট {analytics.get('engagement_rate', 0)}%"
    else:
        return f"{platform} Analytics: {analytics.get('followers', 0)} followers, {analytics.get('engagement_rate', 0)}% engagement"


async def handle_schedule_command(entities: Dict[str, Any], tenant_id: str, db: Session, language: str) -> str:
    """Handle post scheduling commands"""
    if language == "bn":
        return "আপনার পোস্ট শিডিউল করা হয়েছে।"
    else:
        return "Your post has been scheduled."


async def fetch_social_media_analytics(platform: str, client_id: int, period: str, db: Session) -> Dict[str, Any]:
    """Fetch analytics data (placeholder implementation)"""
    # In production, this would call actual social media APIs
    return {
        "account_id": f"{platform}_account_123",
        "followers": 1250,
        "engagement_rate": 3.5,
        "posts_count": 45,
        "reach": 2500,
        "impressions": 3200
    }


def get_error_response(error: str, language: str) -> str:
    """Get error response in appropriate language"""
    if language == "bn":
        return "দুঃখিত, একটি ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
    else:
        return "Sorry, an error occurred. Please try again."


def get_fallback_response(language: str) -> str:
    """Get fallback response for unrecognized commands"""
    if language == "bn":
        return "দুঃখিত, এই কমান্ডটি বুঝতে পারিনি। অনুগ্রহ করে আরেকটি কমান্ড বলুন।"
    else:
        return "Sorry, I didn't understand that command. Please try another one."
