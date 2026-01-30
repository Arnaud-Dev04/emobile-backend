from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String, default="TON") # TON, USD, etc.
    
    # Stockage des URLs d'images sous forme de liste JSON
    images = Column(JSON, default=[]) 
    
    category = Column(String, index=True)
    
    seller_id = Column(Integer, ForeignKey("users.id"))
    seller = relationship("User", backref="products")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
