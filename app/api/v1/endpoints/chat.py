from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.api import deps
from app.models.user import User
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageWithSender, MessageUpdate
from datetime import datetime
import json


router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(deps.get_db)
):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create message in database
            db_message = Message(
                sender_id=user_id,
                receiver_id=message_data["receiver_id"],
                order_id=message_data.get("order_id"),
                content=message_data["content"],
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            # Send message to receiver if online
            receiver_id = message_data["receiver_id"]
            await manager.send_personal_message(
                json.dumps({
                    "id": db_message.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "order_id": db_message.order_id,
                    "content": db_message.content,
                    "created_at": db_message.created_at.isoformat(),
                    "is_read": db_message.is_read
                }),
                receiver_id
            )
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)


@router.get("/conversations", response_model=List[MessageWithSender])
def get_conversations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get all conversations for the current user"""
    messages = db.query(Message).filter(
        (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()
    
    # Add sender/receiver names
    result = []
    for msg in messages:
        msg_dict = MessageWithSender.from_orm(msg).dict()
        msg_dict["sender_name"] = msg.sender.full_name if msg.sender else None
        msg_dict["receiver_name"] = msg.receiver.full_name if msg.receiver else None
        result.append(msg_dict)
    
    return result


@router.get("/order/{order_id}/messages", response_model=List[MessageWithSender])
def get_order_messages(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get all messages for a specific order"""
    messages = db.query(Message).filter(
        Message.order_id == order_id
    ).order_by(Message.created_at.asc()).all()
    
    # Add sender/receiver names
    result = []
    for msg in messages:
        msg_dict = MessageWithSender.from_orm(msg).dict()
        msg_dict["sender_name"] = msg.sender.full_name if msg.sender else None
        msg_dict["receiver_name"] = msg.receiver.full_name if msg.receiver else None
        result.append(msg_dict)
    
    return result


@router.post("/messages", response_model=MessageWithSender)
def create_message(
    message: MessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new message (REST fallback if WebSocket not available)"""
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        order_id=message.order_id,
        content=message.content,
        created_at=datetime.utcnow(),
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    msg_dict = MessageWithSender.from_orm(db_message).dict()
    msg_dict["sender_name"] = db_message.sender.full_name if db_message.sender else None
    msg_dict["receiver_name"] = db_message.receiver.full_name if db_message.receiver else None
    
    return msg_dict


@router.patch("/messages/{message_id}", response_model=MessageWithSender)
def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Mark message as read"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message_update.is_read is not None:
        db_message.is_read = message_update.is_read
    
    db.commit()
    db.refresh(db_message)
    
    msg_dict = MessageWithSender.from_orm(db_message).dict()
    msg_dict["sender_name"] = db_message.sender.full_name if db_message.sender else None
    msg_dict["receiver_name"] = db_message.receiver.full_name if db_message.receiver else None
    
    return msg_dict
