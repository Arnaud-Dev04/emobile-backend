from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base

class OrderStatus(str, enum.Enum):
    """Order status enum matching the escrow flow"""
    CREATED = "CREATED"  # Order created, awaiting payment
    PAID_ESCROW = "PAID_ESCROW"  # Payment received and locked in escrow
    SHIPPED = "SHIPPED"  # Vendor confirmed shipment
    DELIVERED = "DELIVERED"  # Buyer confirmed delivery
    COMPLETED = "COMPLETED"  # Funds released to vendor
    CANCELLED = "CANCELLED"  # Order cancelled
    DISPUTED = "DISPUTED"  # Dispute raised

class PaymentMethod(str, enum.Enum):
    """Supported payment methods"""
    TON = "TON"
    LUMICASH = "LUMICASH"

class WalletType(str, enum.Enum):
    """Wallet types for TON payments"""
    TONKEEPER = "TONKEEPER"
    SAFEPAL = "SAFEPAL"
    MYTONWALLET = "MYTONWALLET"
    OTHER = "OTHER"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Order details
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)  # Price in TON
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.TON, nullable=False)

    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.CREATED, nullable=False)

    # Payment details
    transaction_hash = Column(String, nullable=True)  # TON transaction hash
    escrow_address = Column(String, nullable=True)  # Escrow wallet address
    wallet_used = Column(SQLEnum(WalletType), nullable=True)  # Which wallet app was used

    # Delivery tracking
    shipping_address = Column(String, nullable=True)
    tracking_number = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    buyer = relationship("User", foreign_keys=[buyer_id], backref="purchases")
    seller = relationship("User", foreign_keys=[seller_id], backref="sales")
    product = relationship("Product", backref="orders")
    messages = relationship("Message", back_populates="order", cascade="all, delete-orphan")
