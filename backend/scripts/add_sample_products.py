"""
Add sample products for testing the AI product inquiry system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import get_db
from app.db.models import Product

def add_sample_products():
    db = next(get_db())

    # Sample products for testing
    sample_products = [
        {
            "name": "iPhone 15 Pro",
            "sku": "IPH15P-128",
            "price": 1299.99,
            "currency": "BDT",
            "category": "Smartphones",
            "brand": "Apple",
            "description": "Latest iPhone with advanced camera system and A17 Pro chip",
            "stock_quantity": 25,
            "min_stock_level": 5,
            "is_active": True,
            "is_featured": True,
            "weight": 0.2,
            "tags": ["smartphone", "apple", "premium", "camera"]
        },
        {
            "name": "Samsung Galaxy S24",
            "sku": "SGS24-256",
            "price": 899.99,
            "currency": "BDT",
            "category": "Smartphones",
            "brand": "Samsung",
            "description": "Samsung's flagship smartphone with AI features",
            "stock_quantity": 30,
            "min_stock_level": 8,
            "is_active": True,
            "is_featured": True,
            "weight": 0.18,
            "tags": ["smartphone", "samsung", "ai", "android"]
        },
        {
            "name": "MacBook Pro 16-inch",
            "sku": "MBP16-M3",
            "price": 2499.99,
            "currency": "BDT",
            "category": "Laptops",
            "brand": "Apple",
            "description": "Professional laptop with M3 chip and stunning display",
            "stock_quantity": 12,
            "min_stock_level": 3,
            "is_active": True,
            "is_featured": True,
            "weight": 2.1,
            "tags": ["laptop", "apple", "professional", "m3"]
        },
        {
            "name": "Dell XPS 13",
            "sku": "DXPS13-9320",
            "price": 1299.99,
            "currency": "BDT",
            "category": "Laptops",
            "brand": "Dell",
            "description": "Ultra-portable laptop with premium build quality",
            "stock_quantity": 18,
            "min_stock_level": 5,
            "is_active": True,
            "is_featured": False,
            "weight": 1.2,
            "tags": ["laptop", "dell", "ultrabook", "portable"]
        },
        {
            "name": "Sony WH-1000XM5",
            "sku": "WH1000XM5-BLK",
            "price": 349.99,
            "currency": "BDT",
            "category": "Headphones",
            "brand": "Sony",
            "description": "Premium noise-canceling wireless headphones",
            "stock_quantity": 45,
            "min_stock_level": 10,
            "is_active": True,
            "is_featured": True,
            "weight": 0.25,
            "tags": ["headphones", "sony", "noise-canceling", "wireless"]
        },
        {
            "name": "AirPods Pro 2nd Gen",
            "sku": "APP2-WHT",
            "price": 249.99,
            "currency": "BDT",
            "category": "Headphones",
            "brand": "Apple",
            "description": "Apple's premium wireless earbuds with active noise cancellation",
            "stock_quantity": 0,  # Out of stock for testing
            "min_stock_level": 15,
            "is_active": True,
            "is_featured": True,
            "weight": 0.05,
            "tags": ["earbuds", "apple", "wireless", "noise-canceling"]
        },
        {
            "name": "iPad Air 5th Gen",
            "sku": "IPA5-64",
            "price": 599.99,
            "currency": "BDT",
            "category": "Tablets",
            "brand": "Apple",
            "description": "Versatile tablet perfect for work and creativity",
            "stock_quantity": 22,
            "min_stock_level": 6,
            "is_active": True,
            "is_featured": False,
            "weight": 0.46,
            "tags": ["tablet", "apple", "ipad", "creative"]
        },
        {
            "name": "Samsung Galaxy Tab S9",
            "sku": "SGTS9-128",
            "price": 799.99,
            "currency": "BDT",
            "category": "Tablets",
            "brand": "Samsung",
            "description": "Android tablet with S Pen and premium display",
            "stock_quantity": 8,
            "min_stock_level": 4,
            "is_active": True,
            "is_featured": False,
            "weight": 0.5,
            "tags": ["tablet", "samsung", "android", "s-pen"]
        },
        {
            "name": "Apple Watch Series 9",
            "sku": "AWS9-45",
            "price": 399.99,
            "currency": "BDT",
            "category": "Wearables",
            "brand": "Apple",
            "description": "Latest Apple Watch with advanced health features",
            "stock_quantity": 16,
            "min_stock_level": 4,
            "is_active": True,
            "is_featured": True,
            "weight": 0.04,
            "tags": ["smartwatch", "apple", "health", "fitness"]
        },
        {
            "name": "Garmin Forerunner 265",
            "sku": "GFR265-BLK",
            "price": 449.99,
            "currency": "BDT",
            "category": "Wearables",
            "brand": "Garmin",
            "description": "Advanced running watch with GPS and health monitoring",
            "stock_quantity": 11,
            "min_stock_level": 3,
            "is_active": True,
            "is_featured": False,
            "weight": 0.05,
            "tags": ["smartwatch", "garmin", "running", "gps"]
        }
    ]

    print("Adding sample products to database...")

    for product_data in sample_products:
        # Check if product already exists
        existing = db.query(Product).filter(Product.sku == product_data["sku"]).first()
        if existing:
            print(f"Product {product_data['sku']} already exists, skipping...")
            continue

        product = Product(**product_data)
        db.add(product)
        print(f"Added product: {product.name} ({product.sku})")

    db.commit()
    print("All sample products added successfully!")

    # Print summary
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    featured_products = db.query(Product).filter(Product.is_featured == True).count()

    print(f"\nSummary:")
    print(f"Total products: {total_products}")
    print(f"Active products: {active_products}")
    print(f"Featured products: {featured_products}")

if __name__ == "__main__":
    add_sample_products()
