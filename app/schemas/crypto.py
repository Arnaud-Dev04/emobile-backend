from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ============ WALLET SCHEMAS ============

class WalletBase(BaseModel):
    wallet_address: str
    wallet_type: str = "safepal"
    network: str = "bsc"


class WalletCreate(WalletBase):
    pass


class WalletResponse(WalletBase):
    id: int
    user_id: int
    is_primary: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ TRANSACTION SCHEMAS ============

class TransactionBase(BaseModel):
    amount: float
    currency: str = "USDT"
    network: str = "bsc"


class TransactionCreate(TransactionBase):
    order_id: int
    to_address: str  # Seller's wallet address


class TransactionVerify(BaseModel):
    tx_hash: str


class TransactionResponse(TransactionBase):
    id: int
    order_id: int
    from_address: Optional[str] = None
    to_address: str
    tx_hash: Optional[str] = None
    status: str
    confirmations: int
    created_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ PAYMENT INIT ============

class PaymentInitRequest(BaseModel):
    order_id: int


class PaymentInitResponse(BaseModel):
    transaction_id: int
    seller_wallet: str
    amount: float
    currency: str
    network: str
    deep_link: str  # safepal://... or trust://...
