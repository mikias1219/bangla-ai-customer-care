from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from app.core.config import settings
from app.core.tenant import TenantContext

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,  # Set to True for debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TenantSession(Session):
    """Session that automatically filters by tenant_id"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def query(self, *entities, **kwargs):
        """Override query to automatically filter by tenant_id for tenant-aware models"""
        query = super().query(*entities, **kwargs)

        # If we have a tenant context, filter by tenant_id
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id and entities:
            # Check if the first entity has a tenant_id column
            first_entity = entities[0]
            if hasattr(first_entity, 'tenant_id'):
                query = query.filter(first_entity.tenant_id == tenant_id)

        return query


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = TenantSession(bind=engine)
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database operations"""
    db = TenantSession(bind=engine)
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


def get_admin_db() -> Generator[Session, None, None]:
    """Admin database session that bypasses tenant filtering"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
