"""
Product Inquiry Service - Handles customer queries about products, prices, and inventory
"""
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fuzzywuzzy import fuzz
from fuzzywuzzy.process import extractOne
import re

from app.db.base import get_db
from app.db.models import Product, Customer, Order
from app.services.openai_service import openai_service


class ProductInquiryService:
    def __init__(self):
        self.db: Session = next(get_db())

    def handle_product_query(self, query: str, entities: Dict[str, Any], customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle various product-related queries and return instant responses

        Args:
            query: The customer's message/query
            entities: Extracted entities from NLU
            customer_id: Customer identifier for personalization

        Returns:
            Dict with response text and metadata
        """
        query_lower = query.lower()

        # Price queries - highest priority
        if any(word in query_lower for word in ['price', 'dam', 'koto', 'rate', 'cost', 'মূল্য', 'দাম', 'কত']):
            return self._handle_price_query(query, entities)

        # Product availability/stock queries
        elif any(word in query_lower for word in ['available', 'stock', 'have', 'ache', 'available', 'স্টক', 'আছে']):
            return self._handle_availability_query(query, entities)

        # Product information queries
        elif any(word in query_lower for word in ['about', 'details', 'info', 'বর্ণনা', 'তথ্য']):
            return self._handle_product_info_query(query, entities)

        # Category queries
        elif any(word in query_lower for word in ['category', 'type', 'ধরন', 'ক্যাটাগরি']):
            return self._handle_category_query(query, entities)

        # Recommendation queries
        elif any(word in query_lower for word in ['recommend', 'suggest', 'ভালো', 'রেকমেন্ড']):
            return self._handle_recommendation_query(query, entities, customer_id)

        # Order/product status queries
        elif any(word in query_lower for word in ['order', 'buy', 'purchase', 'অর্ডার', 'কিনতে']):
            return self._handle_purchase_query(query, entities)

        # General product search
        else:
            return self._handle_general_product_query(query, entities)

    def _handle_price_query(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price-related queries"""
        product_name = self._extract_product_name(query, entities)

        if not product_name:
            return {
                "response_text": "কোন প্রোডাক্টের দাম জানতে চান? প্রোডাক্টের নাম বলুন।",
                "action": "clarify",
                "metadata": {"missing": "product_name"}
            }

        products = self._find_products(product_name)

        if not products:
            return {
                "response_text": f"'{product_name}' নামের কোন প্রোডাক্ট খুঁজে পেলাম না। অন্য নাম চেষ্টা করুন।",
                "action": "respond",
                "metadata": {"product_not_found": product_name}
            }

        product = products[0]  # Take the best match

        if not product.is_active:
            return {
                "response_text": f"'{product.name}' বর্তমানে স্টকে নেই।",
                "action": "respond",
                "metadata": {"product_inactive": product.name}
            }

        response = f"**{product.name}**\n"
        response += f"💰 দাম: {product.currency} {product.price:,.2f}\n"

        if product.category:
            response += f"📂 ক্যাটাগরি: {product.category}\n"

        if product.brand:
            response += f"🏷️ ব্র্যান্ড: {product.brand}\n"

        if product.stock_quantity > 0:
            stock_status = "✅ স্টকে আছে" if product.stock_quantity > product.min_stock_level else "⚠️ স্টকে কম"
            response += f"📦 {stock_status} ({product.stock_quantity} পিস)\n"
        else:
            response += "❌ স্টকে নেই\n"

        response += "\n\n💳 **ক্রয়ের জন্য:**\n"
        response += f"• ক্যাশ অন ডেলিভারি সুবিধা আছে\n"
        response += f"• বিকাশ/নগদ/রকেট পেমেন্ট অপশন\n"
        response += f"• ঢাকায় ফ্রি ডেলিভারি\n\n"
        response += f"অর্ডার করতে বলুন: 'আমি এই প্রোডাক্ট কিনতে চাই'"

        return {
            "response_text": response,
            "action": "respond",
            "metadata": {
                "product_found": product.name,
                "price": product.price,
                "currency": product.currency,
                "in_stock": product.stock_quantity > 0
            }
        }

    def _handle_availability_query(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product availability queries"""
        product_name = self._extract_product_name(query, entities)

        if not product_name:
            return {
                "response_text": "কোন প্রোডাক্টের availability জানতে চান?",
                "action": "clarify",
                "metadata": {"missing": "product_name"}
            }

        products = self._find_products(product_name)

        if not products:
            return {
                "response_text": f"'{product_name}' খুঁজে পেলাম না।",
                "action": "respond",
                "metadata": {"product_not_found": product_name}
            }

        product = products[0]

        if not product.is_active:
            return {
                "response_text": f"'{product.name}' বর্তমানে unavailable।",
                "action": "respond"
            }

        if product.stock_quantity > 0:
            response = f"✅ **{product.name}** স্টকে আছে!\n\n"
            response += f"📦 পরিমাণ: {product.stock_quantity} পিস\n"
            response += f"💰 দাম: {product.currency} {product.price:,.2f}\n\n"

            if product.stock_quantity > 10:
                response += "🟢 পর্যাপ্ত স্টক আছে\n"
            elif product.stock_quantity > 5:
                response += "🟡 স্টক সীমিত\n"
            else:
                response += "🟠 শেষ হয়ে যাচ্ছে - দ্রুত অর্ডার করুন!\n"

            response += f"\nঅর্ডার করতে বলুন: '{product.name} অর্ডার করব'"
        else:
            response = f"❌ **{product.name}** বর্তমানে স্টকে নেই।\n\n"
            response += "🔄 কখন আসবে: ৩-৫ কার্যদিবসের মধ্যে\n"
            response += "📧 নোটিফিকেশন চান? আপনাকে জানিয়ে দেব যখন স্টকে আসবে।\n\n"
            response += "এই প্রোডাক্টের সাথে মিলে যায় এমন অন্য প্রোডাক্ট দেখবেন?"

        return {
            "response_text": response,
            "action": "respond",
            "metadata": {
                "product": product.name,
                "available": product.stock_quantity > 0,
                "stock_quantity": product.stock_quantity
            }
        }

    def _handle_product_info_query(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product information queries"""
        product_name = self._extract_product_name(query, entities)

        if not product_name:
            return {
                "response_text": "কোন প্রোডাক্টের তথ্য চান?",
                "action": "clarify"
            }

        products = self._find_products(product_name)

        if not products:
            return {
                "response_text": f"'{product_name}' এর তথ্য খুঁজে পেলাম না।",
                "action": "respond"
            }

        product = products[0]

        response = f"📋 **{product.name}**\n\n"

        if product.description:
            response += f"📝 {product.description}\n\n"

        response += f"💰 দাম: {product.currency} {product.price:,.2f}\n"

        if product.category:
            response += f"📂 ক্যাটাগরি: {product.category}\n"

        if product.brand:
            response += f"🏷️ ব্র্যান্ড: {product.brand}\n"

        if product.stock_quantity > 0:
            response += f"📦 স্টক: {product.stock_quantity} পিস\n"
        else:
            response += "❌ স্টকে নেই\n"

        if product.tags:
            response += f"🏷️ ট্যাগ: {', '.join(product.tags)}\n"

        response += "\nকোন তথ্য আর চান?"

        return {
            "response_text": response,
            "action": "respond",
            "metadata": {"product_info": product.name}
        }

    def _handle_category_query(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle category-based queries"""
        # Extract category from query
        categories = self.db.query(Product.category).filter(
            and_(Product.category.isnot(None), Product.category != "", Product.is_active == True)
        ).distinct().all()

        category_names = [cat[0] for cat in categories]

        if not category_names:
            return {
                "response_text": "কোন ক্যাটাগরি খুঁজে পেলাম না।",
                "action": "respond"
            }

        response = "📂 আমাদের প্রোডাক্ট ক্যাটাগরি:\n\n"
        for i, category in enumerate(category_names[:10], 1):  # Show top 10
            response += f"{i}. {category}\n"

        if len(category_names) > 10:
            response += f"\nএবং আরও {len(category_names) - 10} টি ক্যাটাগরি..."

        response += "\n\nকোন ক্যাটাগরি দেখতে চান?"

        return {
            "response_text": response,
            "action": "respond",
            "metadata": {"categories_shown": len(category_names)}
        }

    def _handle_recommendation_query(self, query: str, entities: Dict[str, Any], customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle product recommendation queries"""
        # Get featured products or bestsellers
        featured_products = self.db.query(Product).filter(
            and_(Product.is_active == True, Product.is_featured == True)
        ).limit(5).all()

        if not featured_products:
            # Fallback to any active products
            featured_products = self.db.query(Product).filter(
                Product.is_active == True
            ).limit(5).all()

        if not featured_products:
            return {
                "response_text": "এখন কোন রেকমেন্ডেড প্রোডাক্ট নেই।",
                "action": "respond"
            }

        response = "🌟 **রেকমেন্ডেড প্রোডাক্টস:**\n\n"

        for product in featured_products:
            response += f"🛍️ **{product.name}**\n"
            response += f"💰 {product.currency} {product.price:,.2f}\n"
            if product.category:
                response += f"📂 {product.category}\n"
            response += "\n"

        response += "কোনটা কিনতে চান?"

        return {
            "response_text": response,
            "action": "respond",
            "metadata": {"recommendations_count": len(featured_products)}
        }

    def _handle_purchase_query(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle purchase/order intent"""
        product_name = self._extract_product_name(query, entities)

        response = "🛒 **অর্ডার করতে:**\n\n"

        if product_name:
            products = self._find_products(product_name)
            if products:
                product = products[0]
                response += f"প্রোডাক্ট: **{product.name}**\n"
                response += f"দাম: {product.currency} {product.price:,.2f}\n\n"

        response += "আপনার নাম, ঠিকানা, এবং পরিমাণ বলুন।\n"
        response += "আমি আপনার অর্ডার প্রসেস করব।"

        return {
            "response_text": response,
            "action": "collect_order_info",
            "metadata": {"intent": "purchase", "product": product_name}
        }

    def _handle_general_product_query(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general product search queries"""
        # Try to find products matching the query
        products = self._search_products(query)

        if not products:
            return {
                "response_text": f"'{query}' এর সাথে মিলে যায় এমন কোন প্রোডাক্ট খুঁজে পেলাম না। অন্যভাবে বলুন।",
                "action": "respond"
            }

        if len(products) == 1:
            product = products[0]
            response = f"**{product.name}** খুঁজে পেলাম!\n\n"
            response += f"💰 দাম: {product.currency} {product.price:,.2f}\n"

            if product.stock_quantity > 0:
                response += f"✅ স্টকে আছে ({product.stock_quantity} পিস)\n"
            else:
                response += "❌ স্টকে নেই\n"

            response += "\nআর কিছু জানতে চান?"
        else:
            response = f"{len(products)} টি প্রোডাক্ট খুঁজে পেলাম:\n\n"
            for i, product in enumerate(products[:5], 1):  # Show top 5
                response += f"{i}. **{product.name}** - {product.currency} {product.price:,.2f}\n"

            if len(products) > 5:
                response += f"\nএবং আরও {len(products) - 5} টি..."

            response += "\n\nকোনটা দেখতে চান?"

        return {
            "response_text": response,
            "action": "respond",
            "metadata": {"products_found": len(products)}
        }

    def _extract_product_name(self, query: str, entities: Dict[str, Any]) -> Optional[str]:
        """Extract product name from query and entities"""
        # Check entities first
        if 'product' in entities:
            return entities['product']

        # Try to extract from query using regex patterns
        patterns = [
            r'price of (.+)',
            r'dam (.+)',
            r'about (.+)',
            r'(.+) er dam',
            r'(.+) er price',
            r'(.+) এর দাম',
            r'(.+) এর মূল্য'
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                product_name = match.group(1).strip()
                # Remove common words
                product_name = re.sub(r'\b(of|er|the|a|an)\b', '', product_name, flags=re.IGNORECASE).strip()
                if product_name:
                    return product_name

        return None

    def _find_products(self, product_name: str, limit: int = 5) -> List[Product]:
        """Find products by name using fuzzy matching"""
        # Exact match first
        exact_matches = self.db.query(Product).filter(
            and_(Product.name.ilike(f"%{product_name}%"), Product.is_active == True)
        ).all()

        if exact_matches:
            return exact_matches[:limit]

        # Fuzzy matching on all active products
        all_products = self.db.query(Product).filter(Product.is_active == True).all()

        if not all_products:
            return []

        # Use fuzzywuzzy to find best matches
        product_names = [p.name for p in all_products]
        best_match, score = extractOne(product_name, product_names, scorer=fuzz.ratio)

        if score >= 60:  # Confidence threshold
            matching_products = [p for p in all_products if p.name == best_match]
            return matching_products[:limit]

        return []

    def _search_products(self, query: str, limit: int = 10) -> List[Product]:
        """Search products using various criteria"""
        search_term = f"%{query}%"

        products = self.db.query(Product).filter(
            and_(
                Product.is_active == True,
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.category.ilike(search_term),
                    Product.brand.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
        ).limit(limit).all()

        return products

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(
            and_(Product.id == product_id, Product.is_active == True)
        ).first()

    def get_products_by_category(self, category: str, limit: int = 20) -> List[Product]:
        """Get products by category"""
        return self.db.query(Product).filter(
            and_(Product.category.ilike(f"%{category}%"), Product.is_active == True)
        ).limit(limit).all()

    def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Get featured products"""
        return self.db.query(Product).filter(
            and_(Product.is_active == True, Product.is_featured == True)
        ).limit(limit).all()


# Singleton instance
product_inquiry_service = ProductInquiryService()
