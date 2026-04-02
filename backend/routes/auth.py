"""
Authentication routes
"""
import uuid
import random
import string
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, status

from models.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    TelegramSetup, ForgotPasswordRequest, ResetPasswordRequest
)
from services.auth_service import (
    hash_password, verify_password, create_token, get_current_user
)
from services.telegram_service import send_telegram_message, send_recovery_code
from config.database import db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate):
    """Register a new user"""
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": user.email,
        "password": hash_password(user.password),
        "name": user.name,
        "telegram_chat_id": None,
        "notifications_enabled": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_data)
    
    token = create_token(user_id)
    user_response = UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        created_at=user_data["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)


@router.post("/login")
async def login(user: UserLogin):
    """Login user and return JWT token"""
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(db_user["id"])
    
    return {
        "token": token,
        "user": {
            "id": db_user["id"],
            "email": db_user["email"],
            "name": db_user["name"],
            "telegram_chat_id": db_user.get("telegram_chat_id")
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(**current_user)


@router.post("/telegram/setup")
async def setup_telegram(data: TelegramSetup, current_user: dict = Depends(get_current_user)):
    """Setup Telegram notifications for user"""
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"telegram_chat_id": data.chat_id}}
    )
    
    # Send test message
    message = f"🎯 *SportsBetAI*\n\n✅ ¡Conexión exitosa!\n\nHola {current_user['name']}, las alertas de value bets llegarán a este chat."
    success = await send_telegram_message(data.chat_id, message)
    
    if not success:
        raise HTTPException(status_code=400, detail="Could not send test message to Telegram")
    
    return {"status": "success", "message": "Telegram connected successfully"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Request password recovery code"""
    user = await db.users.find_one({"email": request.email})
    if not user:
        # Don't reveal if email exists
        return {"status": "success", "message": "If the email exists, a recovery code will be sent"}
    
    if not user.get("telegram_chat_id"):
        raise HTTPException(
            status_code=400,
            detail="No Telegram configured. Please contact support."
        )
    
    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Store code with expiration
    await db.recovery_codes.delete_many({"email": request.email})
    await db.recovery_codes.insert_one({
        "email": request.email,
        "code": code,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Send code via Telegram
    success = await send_recovery_code(user["telegram_chat_id"], code)
    
    if not success:
        raise HTTPException(status_code=500, detail="Could not send recovery code")
    
    return {"status": "success", "message": "Recovery code sent to your Telegram"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using recovery code"""
    # Find valid code
    recovery = await db.recovery_codes.find_one({
        "email": request.email,
        "code": request.code
    })
    
    if not recovery:
        raise HTTPException(status_code=400, detail="Invalid recovery code")
    
    # Check expiration
    expires_at = recovery["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    
    if datetime.now(timezone.utc) > expires_at:
        await db.recovery_codes.delete_one({"_id": recovery["_id"]})
        raise HTTPException(status_code=400, detail="Recovery code expired")
    
    # Update password
    await db.users.update_one(
        {"email": request.email},
        {"$set": {"password": hash_password(request.new_password)}}
    )
    
    # Delete used code
    await db.recovery_codes.delete_one({"_id": recovery["_id"]})
    
    return {"status": "success", "message": "Password updated successfully"}
