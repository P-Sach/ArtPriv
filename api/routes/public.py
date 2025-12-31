from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Bank
from schemas import BankListItem

router = APIRouter()


@router.get("/banks", response_model=List[BankListItem])
async def list_banks(
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Public endpoint to list verified and subscribed banks
    Donors can browse and select banks
    """
    query = db.query(Bank).filter(
        Bank.is_verified == True,
        Bank.is_subscribed == True
    )
    
    # Filter by location if provided
    if location:
        query = query.filter(Bank.address.ilike(f"%{location}%"))
    
    # Search by name or description
    if search:
        query = query.filter(
            (Bank.name.ilike(f"%{search}%")) |
            (Bank.description.ilike(f"%{search}%"))
        )
    
    banks = query.all()
    return banks


@router.get("/banks/{bank_id}", response_model=BankListItem)
async def get_bank_details(
    bank_id: str,
    db: Session = Depends(get_db)
):
    """Get public details of a specific bank"""
    bank = db.query(Bank).filter(
        Bank.id == bank_id,
        Bank.is_verified == True,
        Bank.is_subscribed == True
    ).first()
    
    if not bank:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    return bank
