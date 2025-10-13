from typing import Dict, Any, Callable
import os
import random
from datetime import datetime, timedelta
import httpx


class ResolverService:
    def __init__(self):
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "order_status": self._order_status,
            "return_request": self._return_request,
            "product_inquiry": self._product_inquiry,
            "delivery_tracking": self._delivery_tracking,
        }
        self.base_url = os.getenv("INTEGRATION_BASE_URL", "")
        self.api_key = os.getenv("INTEGRATION_API_KEY", "")

    async def resolve(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        handler = self.handlers.get(name)
        if handler:
            return handler(data)
        # Fallback to passthrough external API if configured
        if self.base_url:
            url = f"{self.base_url.rstrip('/')}/{name}"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=data, headers=headers, timeout=15)
                return r.json()
        return {"message": f"No resolver found for '{name}'", "input": data}

    # Mock handlers below
    def _order_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        order_id = data.get("order_id", "0000")
        statuses = ["Processing", "Packed", "In Transit", "Out for Delivery", "Delivered"]
        status = random.choice(statuses)
        eta = (datetime.utcnow() + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d")
        return {"order_id": order_id, "status": status, "eta": eta}

    def _return_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        order_id = data.get("order_id", "0000")
        return_id = f"R-{random.randint(1000,9999)}"
        refund_days = random.choice([3, 5, 7])
        return {"order_id": order_id, "return_id": return_id, "refund_days": refund_days}

    def _product_inquiry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        product_name = data.get("product_name", "Unknown Product")
        available = random.choice([True, False])
        price = random.choice([499, 699, 999, 1299])
        return {"product_name": product_name, "available": available, "price": price}

    def _delivery_tracking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        order_id = data.get("order_id", "0000")
        courier = random.choice(["Sundarban", "Pathao", "RedX", "Paperfly"]) 
        stage = random.choice(["At Hub", "In Transit", "Arrived at City", "Out for Delivery"]) 
        return {"order_id": order_id, "courier": courier, "stage": stage}


resolver_service = ResolverService()
