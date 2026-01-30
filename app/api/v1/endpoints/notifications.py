from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import models
from app.api import deps
from app.services.notification_service import NotificationService

router = APIRouter()


class FCMTokenUpdate(BaseModel):
    fcm_token: str


class TestNotification(BaseModel):
    title: str = "Test Notification"
    body: str = "This is a test notification from E-Mobile"


@router.put("/fcm-token")
async def update_fcm_token(
    token_data: FCMTokenUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Update the FCM token for the current user
    """
    current_user.fcm_token = token_data.fcm_token
    db.add(current_user)
    db.commit()
    return {"message": "FCM token updated successfully"}


@router.post("/test")
async def send_test_notification(
    notification: TestNotification,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Send a test notification to the current user
    """
    if not current_user.fcm_token:
        raise HTTPException(status_code=400, detail="No FCM token registered")
    
    success = await NotificationService.send_to_device(
        token=current_user.fcm_token,
        title=notification.title,
        body=notification.body,
        data={"type": "test"}
    )
    
    if success:
        return {"message": "Notification sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification")
