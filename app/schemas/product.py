from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from .user import User as UserSchema

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    currency: str = "TON"
    category: Optional[str] = None
    images: List[str] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    title: Optional[str] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None

class Product(ProductBase):
    id: int
    seller_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optionnel: inclure les infos du vendeur
    # seller: UserSchema 

    class Config:
        from_attributes = True
