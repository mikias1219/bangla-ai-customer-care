#!/usr/bin/env python3
"""
Initialize database with tables and seed data
Run this script to set up the database for the first time
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import Base, engine, SessionLocal
from app.db.models import Intent, Entity, Template, User, IntentStatus
from app.routers.auth import get_password_hash


def create_tables():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def seed_intents(db):
    """Seed initial intents"""
    print("Seeding intents...")
    intents = [
        Intent(
            name="order_status",
            description="Customer wants to check order status",
            status=IntentStatus.active,
            examples_count=0
        ),
        Intent(
            name="return_request",
            description="Customer wants to return a product",
            status=IntentStatus.active,
            examples_count=0
        ),
        Intent(
            name="product_inquiry",
            description="Customer asking about product availability",
            status=IntentStatus.active,
            examples_count=0
        ),
        Intent(
            name="payment_issue",
            description="Customer has payment-related issues",
            status=IntentStatus.active,
            examples_count=0
        ),
        Intent(
            name="delivery_tracking",
            description="Customer wants to track delivery",
            status=IntentStatus.active,
            examples_count=0
        ),
        Intent(
            name="complaint",
            description="Customer has a complaint",
            status=IntentStatus.active,
            examples_count=0
        ),
        Intent(
            name="fallback",
            description="Fallback intent when unclear",
            status=IntentStatus.active,
            examples_count=0
        ),
    ]
    
    for intent in intents:
        existing = db.query(Intent).filter(Intent.name == intent.name).first()
        if not existing:
            db.add(intent)
    
    db.commit()
    print(f"✓ Seeded {len(intents)} intents")


def seed_entities(db):
    """Seed initial entities"""
    print("Seeding entities...")
    entities = [
        Entity(
            name="order_id",
            entity_type="regex",
            pattern=r"(?:order|অর্ডার|#)\s*(\d+)",
            description="Order ID extraction"
        ),
        Entity(
            name="phone",
            entity_type="regex",
            pattern=r"(?:\+?88)?01[3-9]\d{8}",
            description="Bangladesh phone number"
        ),
        Entity(
            name="amount",
            entity_type="regex",
            pattern=r"(?:৳|টাকা|taka|tk)\s*(\d+)",
            description="Amount in Taka"
        ),
    ]
    
    for entity in entities:
        existing = db.query(Entity).filter(Entity.name == entity.name).first()
        if not existing:
            db.add(entity)
    
    db.commit()
    print(f"✓ Seeded {len(entities)} entities")


def seed_templates(db):
    """Seed initial Bangla templates"""
    print("Seeding templates...")
    templates = [
        Template(
            key="greeting",
            lang="bn-BD",
            body="Assalamu alaikum! Ami {bot_name}. Apnake ki bhabe shahajjo korte pari?",
            variables=["bot_name"]
        ),
        Template(
            key="order_status",
            lang="bn-BD",
            body="Apnar order #{order_id} er status: {status}. Expected delivery: {delivery_date}",
            variables=["order_id", "status", "delivery_date"]
        ),
        Template(
            key="order_in_transit",
            lang="bn-BD",
            body="Apnar order #{order_id} ekhon courier er kase ache. {courier_name} deliver korbe.",
            variables=["order_id", "courier_name"]
        ),
        Template(
            key="order_delivered",
            lang="bn-BD",
            body="Apnar order #{order_id} already deliver hoyeche {delivery_date} e.",
            variables=["order_id", "delivery_date"]
        ),
        Template(
            key="return_initiated",
            lang="bn-BD",
            body="Apnar return request #{return_id} accept kora hoyeche. {refund_days} diner moddhe refund paben.",
            variables=["return_id", "refund_days"]
        ),
        Template(
            key="product_available",
            lang="bn-BD",
            body="{product_name} ekhon stock e ache. Price: ৳{price}",
            variables=["product_name", "price"]
        ),
        Template(
            key="product_unavailable",
            lang="bn-BD",
            body="{product_name} ekhon stock e nai. {restock_date} e asbe.",
            variables=["product_name", "restock_date"]
        ),
        Template(
            key="handoff_agent",
            lang="bn-BD",
            body="Ami apnake amader agent er sathe connect korchi. Ektu oppokha korun please.",
            variables=[]
        ),
        Template(
            key="thank_you",
            lang="bn-BD",
            body="Dhonnobad! Aro kono shahajjo lagbe?",
            variables=[]
        ),
        Template(
            key="goodbye",
            lang="bn-BD",
            body="Dhonnobad apnar somoy dewar jonno. Bhalo thakben!",
            variables=[]
        ),
    ]
    
    for template in templates:
        existing = db.query(Template).filter(Template.key == template.key).first()
        if not existing:
            db.add(template)
    
    db.commit()
    print(f"✓ Seeded {len(templates)} templates")


def seed_admin_user(db):
    """Create default admin user"""
    print("Creating admin user...")

    existing = db.query(User).filter(User.username == "admin").first()
    if not existing:
        try:
            admin = User(
                username="admin",
                email="admin@bangla-ai.local",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✓ Admin user created (username: admin, password: admin123)")
        except Exception as e:
            print(f"⚠️  Could not create admin user with password: {e}")
            print("Creating admin user without password (set via dashboard later)")
            admin = User(
                username="admin",
                email="admin@bangla-ai.local",
                hashed_password="",  # Empty password
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✓ Admin user created (username: admin, no password set)")
    else:
        print("✓ Admin user already exists")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Bangla AI Platform - Database Initialization")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_intents(db)
        seed_entities(db)
        seed_templates(db)
        seed_admin_user(db)
        
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        print("\nYou can now start the backend server:")
        print("  uvicorn app.main:app --reload")
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  CHANGE THE ADMIN PASSWORD IN PRODUCTION!")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

