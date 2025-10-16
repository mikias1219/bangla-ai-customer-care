#!/usr/bin/env python3
"""
Add sample conversations with real multilingual data for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.db.base import SessionLocal
from app.db.models import Conversation, Turn, ConversationStatus, TurnSpeaker
import random

def add_sample_conversations():
    """Add sample conversations for different channels and languages"""

    db = SessionLocal()

    try:
        # Sample conversation data
        conversations_data = [
            # WhatsApp - Bangla
            {
                "channel": "whatsapp",
                "customer_id": "+8801712345678",
                "customer_name": "রহিম আহমেদ",
                "customer_language": "bn",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "হ্যালো, আমি আপনার স্টোর থেকে একটা প্রোডাক্ট কিনেছি কিন্তু এটা ভাঙ্গা। রিটার্ন করতে চাই।",
                        "text_language": "bn",
                        "intent": "return_request",
                        "entities": {"order_id": "ORD-001"}
                    },
                    {
                        "speaker": "bot",
                        "text": "নমস্কার রহিম আহমেদ! রিটার্নের জন্য অনুগ্রহ করে অর্ডার নম্বর প্রদান করুন।",
                        "text_language": "bn",
                        "intent": "return_request"
                    },
                    {
                        "speaker": "user",
                        "text": "অর্ডার নম্বর ORD-001",
                        "text_language": "bn",
                        "intent": "return_request",
                        "entities": {"order_id": "ORD-001"}
                    },
                    {
                        "speaker": "bot",
                        "text": "ধন্যবাদ। আপনার রিটার্ন রিকোয়েস্ট প্রসেস করছি... দয়া করে ২-৩ কার্যদিবস অপেক্ষা করুন।",
                        "text_language": "bn",
                        "intent": "return_request"
                    }
                ]
            },
            # WhatsApp - English
            {
                "channel": "whatsapp",
                "customer_id": "+8801812345678",
                "customer_name": "Sarah Johnson",
                "customer_language": "en",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "Hi, I ordered a product yesterday but haven't received any update. Can you check the status?",
                        "text_language": "en",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-002"}
                    },
                    {
                        "speaker": "bot",
                        "text": "Hello Sarah! Please provide your order number to check the status.",
                        "text_language": "en",
                        "intent": "order_status"
                    },
                    {
                        "speaker": "user",
                        "text": "Order number is ORD-002",
                        "text_language": "en",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-002"}
                    },
                    {
                        "speaker": "bot",
                        "text": "Thank you. Checking your order status, please wait...",
                        "text_language": "en",
                        "intent": "order_status"
                    }
                ]
            },
            # Messenger - Hindi
            {
                "channel": "messenger",
                "customer_id": "fb_123456789",
                "customer_name": "अमित कुमार",
                "customer_language": "hi",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "नमस्ते, मैंने कल एक प्रोडक्ट ऑर्डर किया था। क्या आप बता सकते हैं कि यह कहाँ है?",
                        "text_language": "hi",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-003"}
                    },
                    {
                        "speaker": "bot",
                        "text": "नमस्ते अमित! अपना ऑर्डर नंबर प्रदान करें ताकि स्थिति जांच सके।",
                        "text_language": "hi",
                        "intent": "order_status"
                    },
                    {
                        "speaker": "user",
                        "text": "ऑर्डर नंबर ORD-003 है",
                        "text_language": "hi",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-003"}
                    },
                    {
                        "speaker": "bot",
                        "text": "आपका ऑर्डर स्टेटस चेक कर रहा हूं, कृपया प्रतीक्षा करें...",
                        "text_language": "hi",
                        "intent": "order_status"
                    }
                ]
            },
            # Instagram - Arabic
            {
                "channel": "instagram",
                "customer_id": "ig_987654321",
                "customer_name": "محمد أحمد",
                "customer_language": "ar",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "مرحبا، طلبت منتج أمس ولم أتلق أي تحديث. هل يمكنك التحقق من الحالة؟",
                        "text_language": "ar",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-004"}
                    },
                    {
                        "speaker": "bot",
                        "text": "مرحبا محمد! يرجى تقديم رقم الطلب للتحقق من الحالة.",
                        "text_language": "ar",
                        "intent": "order_status"
                    },
                    {
                        "speaker": "user",
                        "text": "رقم الطلب ORD-004",
                        "text_language": "ar",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-004"}
                    },
                    {
                        "speaker": "bot",
                        "text": "شكرا لك. جاري فحص حالة الطلب، يرجى الانتظار...",
                        "text_language": "ar",
                        "intent": "order_status"
                    }
                ]
            },
            # WhatsApp - Urdu
            {
                "channel": "whatsapp",
                "customer_id": "+8801912345678",
                "customer_name": "احمد خان",
                "customer_language": "ur",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "سلام، میں نے کل ایک پروڈکٹ آرڈر کیا تھا۔ کیا آپ بتا سکتے ہیں کہ یہ کہاں ہے؟",
                        "text_language": "ur",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-005"}
                    },
                    {
                        "speaker": "bot",
                        "text": "سلام احمد! اپنی آرڈر کی حیثیت چیک کرنے کے لیے آرڈر نمبر فراہم کریں۔",
                        "text_language": "ur",
                        "intent": "order_status"
                    },
                    {
                        "speaker": "user",
                        "text": "آرڈر نمبر ORD-005 ہے",
                        "text_language": "ur",
                        "intent": "order_status",
                        "entities": {"order_id": "ORD-005"}
                    },
                    {
                        "speaker": "bot",
                        "text": "آپ کی آرڈر کی حیثیت چیک کر رہا ہوں، براہ مہربانی انتظار کریں...",
                        "text_language": "ur",
                        "intent": "order_status"
                    }
                ]
            },
            # Product inquiries
            {
                "channel": "messenger",
                "customer_id": "fb_111111111",
                "customer_name": "Priya Sharma",
                "customer_language": "hi",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "iPhone 15 की कीमत क्या है?",
                        "text_language": "hi",
                        "intent": "price_inquiry",
                        "entities": {"product_name": "iPhone 15"}
                    },
                    {
                        "speaker": "bot",
                        "text": "iPhone 15 (128GB) की कीमत ₹89,900 है। क्या आप और कोई जानकारी चाहते हैं?",
                        "text_language": "hi",
                        "intent": "price_inquiry"
                    }
                ]
            },
            # Payment issues
            {
                "channel": "whatsapp",
                "customer_id": "+8801512345678",
                "customer_name": "Fatima Begum",
                "customer_language": "bn",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "পেমেন্ট করেছি কিন্তু কনফার্মেশন মেইল আসেনি। সমস্যা কি?",
                        "text_language": "bn",
                        "intent": "payment_issue"
                    },
                    {
                        "speaker": "bot",
                        "text": "পেমেন্ট সমস্যার জন্য আমি আপনাকে আমাদের পেমেন্ট টিমের সাথে কানেক্ট করছি। অনুগ্রহ করে অপেক্ষা করুন।",
                        "text_language": "bn",
                        "intent": "payment_issue"
                    }
                ]
            },
            # Delivery tracking
            {
                "channel": "instagram",
                "customer_id": "ig_222222222",
                "customer_name": "John Smith",
                "customer_language": "en",
                "turns": [
                    {
                        "speaker": "user",
                        "text": "My order ORD-006 was supposed to arrive today but I haven't received it yet.",
                        "text_language": "en",
                        "intent": "delivery_tracking",
                        "entities": {"order_id": "ORD-006"}
                    },
                    {
                        "speaker": "bot",
                        "text": "I'm sorry for the delay. Let me check the delivery status for ORD-006...",
                        "text_language": "en",
                        "intent": "delivery_tracking"
                    }
                ]
            }
        ]

        base_time = datetime.now() - timedelta(hours=24)

        for conv_data in conversations_data:
            # Create conversation
            conversation = Conversation(
                conversation_id=f"CONV-{random.randint(1000, 9999)}",
                channel=conv_data["channel"],
                customer_id=conv_data["customer_id"],
                customer_name=conv_data["customer_name"],
                customer_language=conv_data["customer_language"],
                status=ConversationStatus.active if len(conv_data["turns"]) % 2 == 0 else ConversationStatus.completed,
                last_message_at=base_time + timedelta(minutes=random.randint(0, 1440)),
                unread_count=random.randint(0, 3)
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            # Create turns
            turn_time = conversation.started_at
            for i, turn_data in enumerate(conv_data["turns"]):
                turn = Turn(
                    conversation_id=conversation.id,
                    turn_index=i,
                    speaker=TurnSpeaker.user if turn_data["speaker"] == "user" else TurnSpeaker.bot,
                    text=turn_data["text"],
                    text_language=turn_data["text_language"],
                    intent=turn_data.get("intent"),
                    entities=turn_data.get("entities", {}),
                    timestamp=turn_time
                )
                db.add(turn)
                turn_time += timedelta(minutes=random.randint(1, 5))

            db.commit()

        print(f"✅ Added {len(conversations_data)} sample conversations with real multilingual data")

    except Exception as e:
        print(f"❌ Error adding sample conversations: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_conversations()
