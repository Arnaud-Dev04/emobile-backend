from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app import models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login/google", response_model=schemas.Token)
def login_google(
    db: Session = Depends(deps.get_db),
    token: str = Body(..., embed=True)
) -> Any:
    """
    Login with Google ID Token. (For Buyers only by default, or auto-detect)
    """
    try:
        # Verify Token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        
        # Get User Info
        email = idinfo['email']
        google_id = idinfo['sub']
        name = idinfo.get('name')
        
        # Check if user exists
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if user:
            # If user exists, check if google_id matches (optional security)
            if not user.google_id:
                # Link account if not linked yet? Or fail? 
                # For this app, simply updating it is better UX.
                user.google_id = google_id
                db.commit()
            if not user.is_active:
                 raise HTTPException(status_code=400, detail="Inactive user")
        else:
            # Create new Buyer User (default is_vendor=False)
            user = models.User(
                email=email,
                full_name=name,
                google_id=google_id,
                hashed_password=None, # No password
                is_vendor=False # Forces buyer role for Google Sign-in
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                subject=user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google Token")
