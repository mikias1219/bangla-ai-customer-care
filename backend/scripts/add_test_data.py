#!/usr/bin/env python3
"""
Add test data to the database for demonstration
Run this script after database initialization
"""
import sys
from pathlib import Path
import uuid
import bcrypt

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import get_db_context
from app.db.models import (
    Client, ClientUser, Subscription, SubscriptionPlan,
    ClientStatus, Product, Customer
)


def add_test_clients(db):
    """Add test clients"""
    print("Adding test clients...")

    # Test client 1 - Restaurant
    client1 = Client(
        tenant_id=str(uuid.uuid4()),
        business_name="Spice Garden Restaurant",
        business_email="contact@spicegarden.com",
        business_phone="+8801712345678",
        business_address="123 Gulshan Avenue, Dhaka",
        contact_person="Rahman Ahmed",
        contact_email="rahman@spicegarden.com",
        contact_phone="+8801712345678",
        business_type="restaurant",
        website_url="https://spicegarden.com",
        facebook_page_url="https://facebook.com/spicegarden",
        instagram_username="spicegarden_bd",
        subscription_plan=SubscriptionPlan.basic,
        monthly_customers_limit=500,
        current_month_customers=0,
        ai_reply_balance=500.0,
        language_preference="bn",
        status=ClientStatus.active
    )

    # Test client 2 - E-commerce
    client2 = Client(
        tenant_id=str(uuid.uuid4()),
        business_name="Fashion Hub BD",
        business_email="support@fashionhub.com",
        business_phone="+8801812345678",
        business_address="456 Dhanmondi, Dhaka",
        contact_person="Priya Sharma",
        contact_email="priya@fashionhub.com",
        contact_phone="+8801812345678",
        business_type="retail",
        website_url="https://fashionhub.com",
        facebook_page_url="https://facebook.com/fashionhubbd",
        instagram_username="fashionhub_bd",
        subscription_plan=SubscriptionPlan.standard,
        monthly_customers_limit=1000,
        current_month_customers=0,
        ai_reply_balance=1000.0,
        language_preference="en",
        status=ClientStatus.active
    )

    # Test client 3 - Trial
    client3 = Client(
        tenant_id=str(uuid.uuid4()),
        business_name="Green Valley Resort",
        business_email="info@greenvalley.com",
        business_phone="+8801912345678",
        business_address="789 Cox's Bazar Road",
        contact_person="Ahmed Hossain",
        contact_email="ahmed@greenvalley.com",
        contact_phone="+8801912345678",
        business_type="hotel",
        website_url="https://greenvalley.com",
        facebook_page_url="https://facebook.com/greenvalleybd",
        instagram_username="greenvalley_bd",
        subscription_plan=SubscriptionPlan.pay_as_you_go,
        monthly_customers_limit=100,
        current_month_customers=0,
        ai_reply_balance=500.0,
        language_preference="banglish",
        status=ClientStatus.trial
    )

    db.add(client1)
    db.add(client2)
    db.add(client3)
    db.flush()

    return [client1, client2, client3]


def add_test_users(db, clients):
    """Add test users for clients"""
    print("Adding test users...")

    users_data = [
        {
            "client": clients[0],
            "username": "rahman",
            "email": "rahman@spicegarden.com",
            "password": "admin123",
            "full_name": "Rahman Ahmed",
            "role": "admin"
        },
        {
            "client": clients[1],
            "username": "priya",
            "email": "priya@fashionhub.com",
            "password": "admin123",
            "full_name": "Priya Sharma",
            "role": "admin"
        },
        {
            "client": clients[2],
            "username": "ahmed",
            "email": "ahmed@greenvalley.com",
            "password": "admin123",
            "full_name": "Ahmed Hossain",
            "role": "admin"
        }
    ]

    users = []
    for user_data in users_data:
        hashed_password = bcrypt.hashpw(
            user_data["password"].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        user = ClientUser(
            client_id=user_data["client"].id,
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        db.add(user)
        users.append(user)

    return users


def add_test_products(db, clients):
    """Add test products for clients"""
    print("Adding test products...")

    products_data = [
        # Restaurant products
        {
            "client": clients[0],
            "products": [
                {
                    "name": "Chicken Biryani",
                    "description": "Traditional Bangladeshi chicken biryani with aromatic spices",
                    "sku": "CB001",
                    "price": 250.0,
                    "category": "Main Course",
                    "brand": "Spice Garden Special"
                },
                {
                    "name": "Beef Curry",
                    "description": "Slow-cooked beef curry with potatoes and spices",
                    "sku": "BC001",
                    "price": 300.0,
                    "category": "Main Course",
                    "brand": "Spice Garden Special"
                },
                {
                    "name": "Fish Curry",
                    "description": "Fresh river fish curry with mustard and coconut",
                    "sku": "FC001",
                    "price": 280.0,
                    "category": "Main Course",
                    "brand": "Spice Garden Special"
                }
            ]
        },
        # Fashion products
        {
            "client": clients[1],
            "products": [
                {
                    "name": "Cotton Salwar Kameez",
                    "description": "Comfortable cotton salwar kameez in traditional design",
                    "sku": "SK001",
                    "price": 1500.0,
                    "category": "Traditional Wear",
                    "brand": "Fashion Hub"
                },
                {
                    "name": "Designer Sharee",
                    "description": "Beautiful handloom sharee with golden border",
                    "sku": "SH001",
                    "price": 3500.0,
                    "category": "Traditional Wear",
                    "brand": "Fashion Hub"
                },
                {
                    "name": "Casual T-Shirt",
                    "description": "Comfortable cotton t-shirt for everyday wear",
                    "sku": "TS001",
                    "price": 800.0,
                    "category": "Casual Wear",
                    "brand": "Fashion Hub"
                }
            ]
        },
        # Hotel services
        {
            "client": clients[2],
            "products": [
                {
                    "name": "Deluxe Room (1 Night)",
                    "description": "Spacious deluxe room with sea view",
                    "sku": "DR001",
                    "price": 5000.0,
                    "category": "Accommodation",
                    "brand": "Green Valley Resort"
                },
                {
                    "name": "Seafood Platter",
                    "description": "Assortment of fresh seafood dishes",
                    "sku": "SP001",
                    "price": 1200.0,
                    "category": "Dining",
                    "brand": "Green Valley Resort"
                },
                {
                    "name": "Spa Treatment",
                    "description": "Relaxing full body spa treatment",
                    "sku": "ST001",
                    "price": 2500.0,
                    "category": "Wellness",
                    "brand": "Green Valley Resort"
                }
            ]
        }
    ]

    all_products = []
    for client_data in products_data:
        for product_data in client_data["products"]:
            product = Product(
                tenant_id=client_data["client"].tenant_id,
                name=product_data["name"],
                description=product_data["description"],
                sku=product_data["sku"],
                price=product_data["price"],
                currency="BDT",
                category=product_data["category"],
                brand=product_data["brand"],
                stock_quantity=50,
                is_active=True,
                is_featured=True
            )
            db.add(product)
            all_products.append(product)

    return all_products


def add_test_customers(db, clients):
    """Add test customers for clients"""
    print("Adding test customers...")

    customers_data = [
        # Restaurant customers
        {
            "client": clients[0],
            "customers": [
                {
                    "customer_id": "FB123456",
                    "name": "Karim Rahman",
                    "email": "karim@gmail.com",
                    "phone": "+8801711111111",
                    "channel": "messenger"
                },
                {
                    "customer_id": "WA987654",
                    "name": "Fatima Begum",
                    "email": "fatima@gmail.com",
                    "phone": "+8801722222222",
                    "channel": "whatsapp"
                }
            ]
        },
        # Fashion customers
        {
            "client": clients[1],
            "customers": [
                {
                    "customer_id": "IG111111",
                    "name": "Sara Ahmed",
                    "email": "sara@gmail.com",
                    "phone": "+8801733333333",
                    "channel": "instagram"
                },
                {
                    "customer_id": "FB222222",
                    "name": "Nadia Islam",
                    "email": "nadia@gmail.com",
                    "phone": "+8801744444444",
                    "channel": "messenger"
                }
            ]
        },
        # Hotel customers
        {
            "client": clients[2],
            "customers": [
                {
                    "customer_id": "FB333333",
                    "name": "Mohammed Ali",
                    "email": "ali@gmail.com",
                    "phone": "+8801755555555",
                    "channel": "messenger"
                }
            ]
        }
    ]

    all_customers = []
    for client_data in customers_data:
        for customer_data in client_data["customers"]:
            customer = Customer(
                tenant_id=client_data["client"].tenant_id,
                customer_id=customer_data["customer_id"],
                name=customer_data["name"],
                email=customer_data["email"],
                phone=customer_data["phone"],
                channel=customer_data["channel"],
                total_orders=0,
                total_spent=0.0
            )
            db.add(customer)
            all_customers.append(customer)

    return all_customers


def main():
    """Main function"""
    print("=" * 60)
    print("Bangla AI - Adding Test Data")
    print("=" * 60)

    with get_db_context() as db:
        try:
            # Add test data
            clients = add_test_clients(db)
            users = add_test_users(db, clients)
            products = add_test_products(db, clients)
            customers = add_test_customers(db, clients)

            print("\n" + "=" * 60)
            print("✓ Test data added successfully!")
            print("=" * 60)
            print(f"✓ Added {len(clients)} test clients")
            print(f"✓ Added {len(users)} test users")
            print(f"✓ Added {len(products)} test products")
            print(f"✓ Added {len(customers)} test customers")
            print("\nTest Client Credentials:")
            for i, client in enumerate(clients, 1):
                user = users[i-1]
                print(f"Client {i}: {client.business_name}")
                print(f"  Email: {user.email}")
                print(f"  Password: admin123")
                print(f"  Tenant ID: {client.tenant_id}")
                print()

        except Exception as e:
            print(f"❌ Error adding test data: {e}")
            db.rollback()
            raise


if __name__ == "__main__":
    main()
