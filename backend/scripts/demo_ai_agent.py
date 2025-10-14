"""
Demo script showing AI Agent responding instantly to customer messages
Just like a real agent would - checking database and responding immediately
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.product_inquiry_service import product_inquiry_service
from app.services.dialogue_manager import dialogue_manager

def demo_ai_agent():
    """Demonstrate AI agent responding to various customer queries"""

    print("🤖 AI Customer Service Agent Demo")
    print("=" * 60)
    print("The AI agent instantly checks the database and responds like a human agent!")
    print()

    # Sample customer conversations
    conversations = [
        {
            "customer": "John from WhatsApp",
            "query": "iPhone 15 Pro er dam koto?",
            "entities": {"product": "iPhone 15 Pro"}
        },
        {
            "customer": "Sarah from Messenger",
            "query": "এয়ারপডস প্রো স্টকে আছে?",
            "entities": {"product": "AirPods Pro"}
        },
        {
            "customer": "Mike from Instagram",
            "query": "best laptop under 1500?",
            "entities": {}
        },
        {
            "customer": "Lisa from Web Chat",
            "query": "Sony headphones price?",
            "entities": {"product": "Sony WH-1000XM5"}
        },
        {
            "customer": "Ahmed from WhatsApp",
            "query": "আপনাদের কি কি smartphone আছে?",
            "entities": {"category": "Smartphones"}
        },
        {
            "customer": "Priya from Messenger",
            "query": "MacBook Pro কত টাকা?",
            "entities": {"product": "MacBook Pro"}
        },
        {
            "customer": "David from Instagram",
            "query": "recommend a good smartwatch",
            "entities": {}
        },
        {
            "customer": "Maria from WhatsApp",
            "query": "iPad Air details please",
            "entities": {"product": "iPad Air"}
        }
    ]

    for i, conv in enumerate(conversations, 1):
        print(f"{i}. 💬 {conv['customer']}:")
        print(f"   '{conv['query']}'")

        # Get instant AI response
        result = product_inquiry_service.handle_product_query(
            conv['query'], conv['entities']
        )

        print("   🤖 AI Agent (instant response):")
        print(f"   {result['response_text']}")
        print()

    print("🎯 Key Features Demonstrated:")
    print("✅ Instant database queries (no delays)")
    print("✅ Multi-language support (Bangla & English)")
    print("✅ Smart product matching with fuzzy search")
    print("✅ Stock availability checking")
    print("✅ Price information retrieval")
    print("✅ Product recommendations")
    print("✅ Category browsing")
    print("✅ Professional agent-like responses")
    print()
    print("🚀 The AI agent works 24/7, handles thousands of queries instantly,")
    print("   and provides personalized responses just like a human agent!")

if __name__ == "__main__":
    demo_ai_agent()
