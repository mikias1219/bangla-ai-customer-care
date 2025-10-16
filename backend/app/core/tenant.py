from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.db.models import Client, ClientUser


class TenantContext:
    """Context manager for tenant information"""
    _current_tenant_id: Optional[str] = None
    _current_client_id: Optional[int] = None
    _current_user_id: Optional[int] = None

    @classmethod
    def set_tenant(cls, tenant_id: str, client_id: Optional[int] = None, user_id: Optional[int] = None):
        cls._current_tenant_id = tenant_id
        cls._current_client_id = client_id
        cls._current_user_id = user_id

    @classmethod
    def get_tenant_id(cls) -> Optional[str]:
        return cls._current_tenant_id

    @classmethod
    def get_client_id(cls) -> Optional[int]:
        return cls._current_client_id

    @classmethod
    def get_user_id(cls) -> Optional[int]:
        return cls._current_user_id

    @classmethod
    def clear(cls):
        cls._current_tenant_id = None
        cls._current_client_id = None
        cls._current_user_id = None


def get_tenant_from_subdomain(request: Request) -> Optional[str]:
    """Extract tenant ID from subdomain (e.g., client1.app.com -> client1)"""
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        # Skip common subdomains
        if subdomain not in ["www", "api", "admin", "app"]:
            return subdomain
    return None


def get_tenant_from_header(request: Request) -> Optional[str]:
    """Extract tenant ID from X-Tenant-ID header"""
    return request.headers.get("X-Tenant-ID")


def get_tenant_from_jwt(token: str) -> Optional[str]:
    """Extract tenant ID from JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("tenant_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_tenant(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> str:
    """
    Get current tenant ID from various sources:
    1. JWT token (for authenticated users)
    2. X-Tenant-ID header (for API clients)
    3. Subdomain (for web clients)
    """
    tenant_id = None

    # Try JWT token first
    if credentials:
        tenant_id = get_tenant_from_jwt(credentials.credentials)

    # Try header
    if not tenant_id:
        tenant_id = get_tenant_from_header(request)

    # Try subdomain
    if not tenant_id:
        tenant_id = get_tenant_from_subdomain(request)

    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant not specified")

    # Import here to avoid circular imports
    from app.db.session import get_admin_db_context

    # Validate tenant exists
    with get_admin_db_context() as db:
        client = db.query(Client).filter(Client.tenant_id == tenant_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Set tenant context
        TenantContext.set_tenant(tenant_id, client.id)

    return tenant_id


async def get_current_client_user(
    tenant_id: str = Depends(get_current_tenant),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> ClientUser:
    """Get current authenticated client user"""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Import here to avoid circular imports
        from app.db.session import get_admin_db_context

        with get_admin_db_context() as db:
            user = db.query(ClientUser).filter(
                ClientUser.id == int(user_id),
                ClientUser.is_active == True
            ).first()

            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            # Verify user belongs to current tenant
            if str(user.client_id) != str(TenantContext.get_client_id()):
                raise HTTPException(status_code=403, detail="Access denied")

            TenantContext.set_tenant(tenant_id, user.client_id, user.id)
            return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_tenant_token(client_id: int, user_id: int, tenant_id: str) -> str:
    """Create JWT token with tenant information"""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {
        "sub": str(user_id),
        "client_id": client_id,
        "tenant_id": tenant_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


class TenantMiddleware:
    """Middleware to handle tenant context"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Clear tenant context at the start of each request
            TenantContext.clear()

        await self.app(scope, receive, send)
