"""
Notification Service for E-Mobile
Handles Firebase Cloud Messaging (FCM) push notifications
"""
import os
from typing import Optional, List
import httpx

# For production, use firebase-admin SDK
# from firebase_admin import credentials, messaging, initialize_app

# FCM Server Key (set in environment)
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")
FCM_API_URL = "https://fcm.googleapis.com/fcm/send"


class NotificationService:
    """Service for sending push notifications via FCM"""
    
    @staticmethod
    async def send_to_device(
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """
        Send a notification to a specific device
        
        Args:
            token: FCM device token
            title: Notification title
            body: Notification body text
            data: Optional data payload
            
        Returns:
            bool: Success status
        """
        if not FCM_SERVER_KEY:
            print("Warning: FCM_SERVER_KEY not configured")
            return False
            
        headers = {
            "Authorization": f"key={FCM_SERVER_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default",
                "click_action": "OPEN_APP"
            }
        }
        
        if data:
            payload["data"] = data
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    FCM_API_URL,
                    headers=headers,
                    json=payload
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    @staticmethod
    async def send_to_multiple(
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> dict:
        """
        Send notification to multiple devices
        
        Returns:
            dict: Results with success/failure counts
        """
        if not tokens:
            return {"success": 0, "failure": 0}
            
        results = {"success": 0, "failure": 0}
        
        for token in tokens:
            success = await NotificationService.send_to_device(token, title, body, data)
            if success:
                results["success"] += 1
            else:
                results["failure"] += 1
                
        return results


# Predefined notification types
class NotificationTypes:
    """Predefined notification templates"""
    
    @staticmethod
    def order_created(order_id: int, product_name: str) -> dict:
        return {
            "title": "New Order! 🛒",
            "body": f"Someone ordered your {product_name}",
            "data": {"type": "order", "order_id": str(order_id)}
        }
    
    @staticmethod
    def order_paid(order_id: int) -> dict:
        return {
            "title": "Payment Received! 💰",
            "body": f"Order #{order_id} has been paid",
            "data": {"type": "order", "order_id": str(order_id)}
        }
    
    @staticmethod
    def order_shipped(order_id: int, tracking: str) -> dict:
        return {
            "title": "Order Shipped! 📦",
            "body": f"Your order #{order_id} is on its way",
            "data": {"type": "order", "order_id": str(order_id), "tracking": tracking}
        }
    
    @staticmethod
    def order_delivered(order_id: int) -> dict:
        return {
            "title": "Delivered! ✅",
            "body": f"Order #{order_id} has been delivered",
            "data": {"type": "order", "order_id": str(order_id)}
        }
    
    @staticmethod
    def new_message(sender_name: str, order_id: int) -> dict:
        return {
            "title": f"Message from {sender_name} 💬",
            "body": "You have a new message",
            "data": {"type": "chat", "order_id": str(order_id)}
        }
