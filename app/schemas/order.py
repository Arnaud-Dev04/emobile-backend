from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.order import OrderStatus, PaymentMethod, WalletType

class OrderBase(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)
    shipping_address: Optional[str] = None
    payment_method: PaymentMethod = Field(default=PaymentMethod.TON, description="Payment method")

# Order Create
class OrderCreate(OrderBase):
    pass

# Order Update (for status changes)
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None
    transaction_hash: Optional[str] = None
    wallet_used: Optional[WalletType] = None

# Order Response
class Order(OrderBase):
    id: int
    buyer_id: int
    seller_id: int
    total_price: float
    transaction_hash: Optional[str] = None
    escrow_address: Optional[str] = None
    tracking_number: Optional[str] = None
    wallet_used: Optional[WalletType] = None
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Order with Product details (for list views)
class OrderWithDetails(Order):
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
