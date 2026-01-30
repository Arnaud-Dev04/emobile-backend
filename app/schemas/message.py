from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageBase(BaseModel):
    content: str
    receiver_id: int
    order_id: Optional[int] = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None


class MessageInDB(MessageBase):
    id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True


class Message(MessageInDB):
    pass


class MessageWithSender(Message):
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
