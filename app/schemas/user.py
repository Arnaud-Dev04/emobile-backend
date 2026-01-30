from typing import Optional
from pydantic import BaseModel, EmailStr

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# User Shared
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_vendor: bool = False

# User Create
class UserCreate(UserBase):
    password: str

# User Update
class UserUpdate(UserBase):
    password: Optional[str] = None

# User In DB (Response)
class User(UserBase):
    id: int
    is_active: bool
    rating: float
    
    class Config:
        from_attributes = True
