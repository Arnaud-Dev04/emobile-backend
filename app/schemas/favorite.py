from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FavoriteBase(BaseModel):
    product_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteWithProduct(FavoriteResponse):
    product_title: Optional[str] = None
    product_price: Optional[float] = None
    product_image: Optional[str] = None
