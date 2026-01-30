from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Nullable pour Google User
    full_name = Column(String, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_vendor = Column(Boolean, default=False)
    
    # Reputation
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Push Notifications
    fcm_token = Column(String, nullable=True)  # Firebase Cloud Messaging token
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
