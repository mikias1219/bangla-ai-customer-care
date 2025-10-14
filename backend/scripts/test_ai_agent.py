"""
Test script to demonstrate AI agent responding to customer queries
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.product_inquiry_service import product_inquiry_service
from app.services.dialogue_manager import dialogue_manager

def test_ai_responses():
    """Test various customer queries and show AI responses"""

    test_queries = [
        # Price queries
        ("iPhone 15 Pro er dam koto?", {"product": "iPhone 15 Pro"}),
        ("Samsung Galaxy S24 price?", {"product": "Samsung Galaxy S24"}),
        ("MacBook Pro koto?", {"product": "MacBook Pro"}),

        # Availability queries
        ("AirPods Pro ache?", {"product": "AirPods Pro"}),
        ("Sony headphones available?", {"product": "Sony WH-1000XM5"}),
        ("iPad stock koto?", {"product": "iPad Air"}),

        # Product information
        ("Dell XPS 13 ke bare bolo", {"product": "Dell XPS 13"}),
        ("Apple Watch Series 9 er features ki?", {"product": "Apple Watch Series 9"}),

        # Recommendations
        ("Best smartphone suggest koren", {}),
        ("Akon ki recommend korben?", {}),

        # Categories
        ("Laptop category te ki ache?", {"category": "Laptops"}),
        ("Headphones er type ki?", {}),

        # General searches
        ("wireless headphones", {}),
        ("apple products", {"brand": "Apple"}),
    ]

    print("🤖 AI Agent Response Demonstration")
    print("=" * 50)

    for i, (query, entities) in enumerate(test_queries, 1):
        print(f"\n🗣️ Customer Query #{i}: '{query}'")

        # Test direct product inquiry service
        direct_result = product_inquiry_service.handle_product_query(query, entities)
        print("💡 Direct Response:"        print(direct_result["response_text"])

        # Test through dialogue manager
        dm_result = dialogue_manager.decide(
            intent="product_inquiry",  # Default intent for testing
            entities=entities,
            context={"message": query, "customer_id": "test_customer"}
        )
        print("🎯 Dialogue Manager Response:"        print(dm_result["response_text_bn"])
        print("-" * 30)

if __name__ == "__main__":
    test_ai_responses()
