from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.session import Base


class CryptoWallet(Base):
    """Model for storing user cryptocurrency wallet addresses"""
    __tablename__ = "crypto_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    wallet_address = Column(String(100), nullable=False, index=True)
    wallet_type = Column(String(50), default="safepal")  # safepal, metamask, trust_wallet
    network = Column(String(50), default="bsc")  # bsc, eth, polygon
    
    is_primary = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CryptoTransaction(Base):
    """Model for tracking cryptocurrency transactions"""
    __tablename__ = "crypto_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    # Addresses
    from_address = Column(String(100), nullable=False)
    to_address = Column(String(100), nullable=False)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(20), nullable=False)  # USDT, BNB, ETH
    network = Column(String(50), default="bsc")  # bsc, eth, polygon
    
    # Blockchain verification
    tx_hash = Column(String(100), unique=True, index=True, nullable=True)
    block_number = Column(Integer, nullable=True)
    confirmations = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirming, confirmed, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
