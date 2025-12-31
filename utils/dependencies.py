from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Bank, Donor
from utils.auth import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    user_type: str = payload.get("type")
    
    if user_id is None or user_type is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user exists
    if user_type == "bank":
        user = db.query(Bank).filter(Bank.id == user_id).first()
    elif user_type == "donor":
        user = db.query(Donor).filter(Donor.id == user_id).first()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user type")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return {
        "id": user_id,
        "type": user_type,
        "user": user
    }


async def get_current_bank(
    current_user: dict = Depends(get_current_user)
) -> Bank:
    """Get current bank user"""
    if current_user["type"] != "bank":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bank access required"
        )
    return current_user["user"]


async def get_current_donor(
    current_user: dict = Depends(get_current_user)
) -> Donor:
    """Get current donor user"""
    if current_user["type"] != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Donor access required"
        )
    return current_user["user"]


async def get_verified_bank(
    bank: Bank = Depends(get_current_bank)
) -> Bank:
    """Get current bank and ensure it's verified"""
    if not bank.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bank verification required"
        )
    return bank


async def get_subscribed_bank(
    bank: Bank = Depends(get_verified_bank)
) -> Bank:
    """Get current bank and ensure it's subscribed"""
    if not bank.is_subscribed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required"
        )
    return bank
