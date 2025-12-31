from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Bank, Donor
from schemas import UserLogin, TokenResponse
from utils import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/donor/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_donor(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Register a new donor (creates lead only at this stage)"""
    # Check if donor already exists
    existing_donor = db.query(Donor).filter(Donor.email == email).first()
    if existing_donor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # This is a simplified version - in reality, lead creation happens first
    # This endpoint would be used after lead creation for account setup
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please create a lead first by selecting a bank"
    )


@router.post("/donor/login", response_model=TokenResponse)
async def login_donor(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login donor"""
    donor = db.query(Donor).filter(Donor.email == credentials.email).first()
    
    if not donor or not donor.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(credentials.password, donor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(donor.id), "type": "donor"}
    )
    
    return TokenResponse(
        access_token=access_token,
        user_type="donor",
        user_id=str(donor.id)
    )


@router.post("/bank/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_bank(
    email: str,
    password: str,
    name: str,
    db: Session = Depends(get_db)
):
    """Register a new bank"""
    from models import BankState
    
    # Check if bank already exists
    existing_bank = db.query(Bank).filter(Bank.email == email).first()
    if existing_bank:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create bank
    bank = Bank(
        email=email,
        hashed_password=hash_password(password),
        name=name,
        state=BankState.ACCOUNT_CREATED
    )
    
    db.add(bank)
    db.commit()
    db.refresh(bank)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(bank.id), "type": "bank"}
    )
    
    return TokenResponse(
        access_token=access_token,
        user_type="bank",
        user_id=str(bank.id)
    )


@router.post("/bank/login", response_model=TokenResponse)
async def login_bank(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login bank"""
    bank = db.query(Bank).filter(Bank.email == credentials.email).first()
    
    if not bank or not verify_password(credentials.password, bank.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(bank.id), "type": "bank"}
    )
    
    return TokenResponse(
        access_token=access_token,
        user_type="bank",
        user_id=str(bank.id)
    )
