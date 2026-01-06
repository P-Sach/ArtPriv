"""Admin API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta

from database import get_db
from models import Bank, Donor, Admin, ActivityLog, DonorStateHistory
from schemas import (
    AdminLogin, AdminTokenResponse, AdminCreate, AdminResponse,
    DashboardStats, DashboardResponse, SubscriptionSummary,
    BankAdminView, BankListResponse, BankVerifyRequest, SubscriptionUpdateRequest,
    DonorAdminView, DonorListResponse, DonorDetailAdminView, StateHistoryItem,
    ActivityLogResponse, ActivityLogListResponse,
    SubscriptionAnalytics, MonthlySubscriptionTrend
)
from auth import hash_password, verify_password, create_access_token
from config import settings

router = APIRouter()


# ========== Auth Helpers ==========
def get_current_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    """Get the current authenticated admin from JWT token"""
    from jose import jwt, JWTError
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id = payload.get("sub")
        user_type = payload.get("type")
        
        if user_type != "admin" or not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found or inactive"
        )
    
    return admin


def require_role(required_roles: List[str]):
    """Dependency to require specific admin roles"""
    def check_role(admin: Admin = Depends(get_current_admin)):
        if admin.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return admin
    return check_role


def log_activity(db: Session, admin: Admin, action: str, entity_type: str, 
                 entity_id: str = None, details: dict = None, ip_address: str = None):
    """Helper to create activity log entries"""
    log = ActivityLog(
        admin_id=admin.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()


# ========== Authentication ==========
@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Authenticate admin and return JWT token"""
    admin = db.query(Admin).filter(Admin.email == credentials.email).first()
    
    if not admin or not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )
    
    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(admin.id), "type": "admin", "role": admin.role}
    )
    
    return AdminTokenResponse(
        access_token=access_token,
        admin_id=str(admin.id),
        role=admin.role,
        name=admin.name
    )


@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: AdminCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_role(["super_admin"]))
):
    """Create a new admin (super_admin only)"""
    existing = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    admin = Admin(
        email=admin_data.email,
        hashed_password=hash_password(admin_data.password),
        name=admin_data.name,
        role=admin_data.role
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    log_activity(db, current_admin, "admin_created", "admin", admin.id, 
                 {"name": admin.name, "role": admin.role})
    
    return admin


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_profile(current_admin: Admin = Depends(get_current_admin)):
    """Get current admin's profile"""
    return current_admin


# ========== Dashboard ==========
@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get dashboard statistics"""
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_future = now + timedelta(days=30)
    
    # Bank statistics
    total_banks = db.query(func.count(Bank.id)).scalar()
    verified_banks = db.query(func.count(Bank.id)).filter(Bank.is_verified == True).scalar()
    subscribed_banks = db.query(func.count(Bank.id)).filter(Bank.is_subscribed == True).scalar()
    operational_banks = db.query(func.count(Bank.id)).filter(Bank.state == "operational").scalar()
    pending_verifications = db.query(func.count(Bank.id)).filter(
        Bank.state == "verification_pending"
    ).scalar()
    
    # Subscription statistics
    expiring_subscriptions = db.query(func.count(Bank.id)).filter(
        and_(
            Bank.is_subscribed == True,
            Bank.subscription_expires_at <= thirty_days_future,
            Bank.subscription_expires_at > now
        )
    ).scalar()
    
    expired_subscriptions = db.query(func.count(Bank.id)).filter(
        and_(
            Bank.subscription_expires_at != None,
            Bank.subscription_expires_at < now
        )
    ).scalar()
    
    # Recent signups
    recent_signups = db.query(func.count(Bank.id)).filter(
        Bank.created_at >= seven_days_ago
    ).scalar()
    
    # Donor statistics
    total_donors = db.query(func.count(Donor.id)).scalar()
    onboarded_donors = db.query(func.count(Donor.id)).filter(
        Donor.state == "donor_onboarded"
    ).scalar()
    
    stats = DashboardStats(
        total_banks=total_banks or 0,
        verified_banks=verified_banks or 0,
        subscribed_banks=subscribed_banks or 0,
        operational_banks=operational_banks or 0,
        total_donors=total_donors or 0,
        onboarded_donors=onboarded_donors or 0,
        pending_verifications=pending_verifications or 0,
        expiring_subscriptions=expiring_subscriptions or 0,
        expired_subscriptions=expired_subscriptions or 0,
        recent_signups=recent_signups or 0
    )
    
    # Subscription tier breakdown
    tier_counts = db.query(
        Bank.subscription_tier,
        func.count(Bank.id)
    ).filter(Bank.is_subscribed == True).group_by(Bank.subscription_tier).all()
    
    tier_prices = {"Starter": 999, "Professional": 2499, "Enterprise": 4999}
    subscription_breakdown = [
        SubscriptionSummary(
            tier=tier or "Unknown",
            count=count,
            revenue_estimate=count * tier_prices.get(tier, 0)
        )
        for tier, count in tier_counts
    ]
    
    # Recent activity
    recent_logs = db.query(ActivityLog).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()
    
    recent_activity = []
    for log in recent_logs:
        admin = db.query(Admin).filter(Admin.id == log.admin_id).first()
        recent_activity.append(ActivityLogResponse(
            id=str(log.id),
            admin_id=str(log.admin_id),
            admin_name=admin.name if admin else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at
        ))
    
    return DashboardResponse(
        stats=stats,
        subscription_breakdown=subscription_breakdown,
        recent_activity=recent_activity
    )


# ========== Bank Management ==========
@router.get("/banks", response_model=BankListResponse)
async def list_banks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: Optional[str] = None,
    is_verified: Optional[bool] = None,
    is_subscribed: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """List all banks with filters and pagination"""
    query = db.query(Bank)
    
    if state:
        query = query.filter(Bank.state == state)
    if is_verified is not None:
        query = query.filter(Bank.is_verified == is_verified)
    if is_subscribed is not None:
        query = query.filter(Bank.is_subscribed == is_subscribed)
    if search:
        query = query.filter(
            or_(
                Bank.name.ilike(f"%{search}%"),
                Bank.email.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    offset = (page - 1) * page_size
    banks = query.order_by(Bank.created_at.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for bank in banks:
        donor_count = db.query(func.count(Donor.id)).filter(Donor.bank_id == bank.id).scalar()
        items.append(BankAdminView(
            id=str(bank.id),
            email=bank.email,
            name=bank.name,
            state=bank.state,
            phone=bank.phone,
            address=bank.address,
            website=bank.website,
            is_verified=bank.is_verified,
            verified_at=bank.verified_at,
            is_subscribed=bank.is_subscribed,
            subscription_tier=bank.subscription_tier,
            subscription_started_at=bank.subscription_started_at,
            subscription_expires_at=bank.subscription_expires_at,
            donor_count=donor_count or 0,
            created_at=bank.created_at
        ))
    
    return BankListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/banks/{bank_id}", response_model=BankAdminView)
async def get_bank_details(
    bank_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get bank details"""
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    donor_count = db.query(func.count(Donor.id)).filter(Donor.bank_id == bank.id).scalar()
    
    return BankAdminView(
        id=str(bank.id),
        email=bank.email,
        name=bank.name,
        state=bank.state,
        phone=bank.phone,
        address=bank.address,
        website=bank.website,
        is_verified=bank.is_verified,
        verified_at=bank.verified_at,
        is_subscribed=bank.is_subscribed,
        subscription_tier=bank.subscription_tier,
        subscription_started_at=bank.subscription_started_at,
        subscription_expires_at=bank.subscription_expires_at,
        donor_count=donor_count or 0,
        created_at=bank.created_at
    )


@router.put("/banks/{bank_id}/verify", response_model=BankAdminView)
async def verify_bank(
    bank_id: str,
    verify_data: BankVerifyRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_role(["super_admin", "support"]))
):
    """Verify a bank"""
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    if bank.is_verified:
        raise HTTPException(status_code=400, detail="Bank is already verified")
    
    bank.is_verified = True
    bank.verified_at = datetime.utcnow()
    bank.verified_by = verify_data.verified_by
    
    if bank.state == "verification_pending":
        bank.state = "verified"
    
    db.commit()
    db.refresh(bank)
    
    log_activity(
        db, current_admin, "bank_verified", "bank", bank.id,
        {"bank_name": bank.name, "notes": verify_data.notes},
        request.client.host if request.client else None
    )
    
    donor_count = db.query(func.count(Donor.id)).filter(Donor.bank_id == bank.id).scalar()
    
    return BankAdminView(
        id=str(bank.id),
        email=bank.email,
        name=bank.name,
        state=bank.state,
        phone=bank.phone,
        address=bank.address,
        website=bank.website,
        is_verified=bank.is_verified,
        verified_at=bank.verified_at,
        is_subscribed=bank.is_subscribed,
        subscription_tier=bank.subscription_tier,
        subscription_started_at=bank.subscription_started_at,
        subscription_expires_at=bank.subscription_expires_at,
        donor_count=donor_count or 0,
        created_at=bank.created_at
    )


@router.put("/banks/{bank_id}/subscription", response_model=BankAdminView)
async def update_bank_subscription(
    bank_id: str,
    subscription_data: SubscriptionUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_role(["super_admin", "support"]))
):
    """Update bank subscription"""
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    if not bank.is_verified:
        raise HTTPException(status_code=400, detail="Bank must be verified first")
    
    old_tier = bank.subscription_tier
    bank.is_subscribed = True
    bank.subscription_tier = subscription_data.subscription_tier
    bank.subscription_started_at = subscription_data.subscription_started_at
    bank.subscription_expires_at = subscription_data.subscription_expires_at
    
    if bank.state in ["verified", "subscription_pending"]:
        bank.state = "subscribed_onboarded"
    
    db.commit()
    db.refresh(bank)
    
    log_activity(
        db, current_admin, "subscription_updated", "bank", bank.id,
        {
            "bank_name": bank.name,
            "old_tier": old_tier,
            "new_tier": subscription_data.subscription_tier,
            "expires_at": subscription_data.subscription_expires_at.isoformat(),
            "notes": subscription_data.notes
        },
        request.client.host if request.client else None
    )
    
    donor_count = db.query(func.count(Donor.id)).filter(Donor.bank_id == bank.id).scalar()
    
    return BankAdminView(
        id=str(bank.id),
        email=bank.email,
        name=bank.name,
        state=bank.state,
        phone=bank.phone,
        address=bank.address,
        website=bank.website,
        is_verified=bank.is_verified,
        verified_at=bank.verified_at,
        is_subscribed=bank.is_subscribed,
        subscription_tier=bank.subscription_tier,
        subscription_started_at=bank.subscription_started_at,
        subscription_expires_at=bank.subscription_expires_at,
        donor_count=donor_count or 0,
        created_at=bank.created_at
    )


# ========== Donor Management ==========
@router.get("/donors", response_model=DonorListResponse)
async def list_donors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: Optional[str] = None,
    bank_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """List all donors with filters"""
    query = db.query(Donor)
    
    if state:
        query = query.filter(Donor.state == state)
    if bank_id:
        query = query.filter(Donor.bank_id == bank_id)
    if search:
        query = query.filter(
            or_(
                Donor.first_name.ilike(f"%{search}%"),
                Donor.last_name.ilike(f"%{search}%"),
                Donor.email.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    offset = (page - 1) * page_size
    donors = query.order_by(Donor.created_at.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for donor in donors:
        bank_name = None
        if donor.bank_id:
            bank = db.query(Bank).filter(Bank.id == donor.bank_id).first()
            bank_name = bank.name if bank else None
        
        items.append(DonorAdminView(
            id=str(donor.id),
            email=donor.email,
            first_name=donor.first_name,
            last_name=donor.last_name,
            phone=donor.phone,
            state=donor.state,
            bank_id=str(donor.bank_id) if donor.bank_id else None,
            bank_name=bank_name,
            eligibility_status=donor.eligibility_status or "pending",
            created_at=donor.created_at
        ))
    
    return DonorListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/donors/{donor_id}", response_model=DonorDetailAdminView)
async def get_donor_details(
    donor_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get donor details with state history"""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    bank_name = None
    if donor.bank_id:
        bank = db.query(Bank).filter(Bank.id == donor.bank_id).first()
        bank_name = bank.name if bank else None
    
    history = db.query(DonorStateHistory).filter(
        DonorStateHistory.donor_id == donor_id
    ).order_by(DonorStateHistory.created_at.desc()).all()
    
    state_history = [
        StateHistoryItem(
            id=str(h.id),
            from_state=h.from_state,
            to_state=h.to_state,
            changed_by=h.changed_by,
            changed_by_role=h.changed_by_role,
            reason=h.reason,
            created_at=h.created_at
        )
        for h in history
    ]
    
    return DonorDetailAdminView(
        id=str(donor.id),
        email=donor.email,
        first_name=donor.first_name,
        last_name=donor.last_name,
        phone=donor.phone,
        state=donor.state,
        bank_id=str(donor.bank_id) if donor.bank_id else None,
        bank_name=bank_name,
        eligibility_status=donor.eligibility_status or "pending",
        created_at=donor.created_at,
        address=donor.address,
        date_of_birth=donor.date_of_birth,
        medical_interest_info=donor.medical_interest_info,
        eligibility_notes=donor.eligibility_notes,
        selected_at=donor.selected_at,
        consent_pending=donor.consent_pending or False,
        counseling_pending=donor.counseling_pending or False,
        tests_pending=donor.tests_pending or False,
        state_history=state_history
    )


# ========== Activity Logs ==========
@router.get("/activity-logs", response_model=ActivityLogListResponse)
async def list_activity_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entity_type: Optional[str] = None,
    admin_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """List activity logs"""
    query = db.query(ActivityLog)
    
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if admin_id:
        query = query.filter(ActivityLog.admin_id == admin_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    logs = query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(page_size).all()
    
    items = []
    for log in logs:
        admin = db.query(Admin).filter(Admin.id == log.admin_id).first()
        items.append(ActivityLogResponse(
            id=str(log.id),
            admin_id=str(log.admin_id),
            admin_name=admin.name if admin else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at
        ))
    
    return ActivityLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ========== Subscription Analytics ==========
@router.get("/subscriptions/analytics", response_model=SubscriptionAnalytics)
async def get_subscription_analytics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get subscription analytics"""
    now = datetime.utcnow()
    thirty_days_future = now + timedelta(days=30)
    
    active_subscriptions = db.query(func.count(Bank.id)).filter(
        and_(
            Bank.is_subscribed == True,
            or_(
                Bank.subscription_expires_at == None,
                Bank.subscription_expires_at > now
            )
        )
    ).scalar()
    
    expiring_soon = db.query(func.count(Bank.id)).filter(
        and_(
            Bank.is_subscribed == True,
            Bank.subscription_expires_at <= thirty_days_future,
            Bank.subscription_expires_at > now
        )
    ).scalar()
    
    expired = db.query(func.count(Bank.id)).filter(
        and_(
            Bank.subscription_expires_at != None,
            Bank.subscription_expires_at < now
        )
    ).scalar()
    
    never_subscribed = db.query(func.count(Bank.id)).filter(
        Bank.subscription_started_at == None
    ).scalar()
    
    tier_prices = {"Starter": 999, "Professional": 2499, "Enterprise": 4999}
    tier_counts = db.query(
        Bank.subscription_tier,
        func.count(Bank.id)
    ).filter(Bank.is_subscribed == True).group_by(Bank.subscription_tier).all()
    
    tier_breakdown = []
    total_revenue = 0
    for tier, count in tier_counts:
        price = tier_prices.get(tier, 0)
        revenue = count * price
        total_revenue += revenue
        tier_breakdown.append(SubscriptionSummary(
            tier=tier or "Unknown",
            count=count,
            revenue_estimate=revenue
        ))
    
    monthly_trend = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        new_subs = db.query(func.count(Bank.id)).filter(
            and_(
                Bank.subscription_started_at >= month_start,
                Bank.subscription_started_at < month_end
            )
        ).scalar()
        
        monthly_trend.append(MonthlySubscriptionTrend(
            month=month_start.strftime("%Y-%m"),
            new_subscriptions=new_subs or 0,
            renewals=0,
            churned=0
        ))
    
    return SubscriptionAnalytics(
        active_subscriptions=active_subscriptions or 0,
        expiring_soon=expiring_soon or 0,
        expired=expired or 0,
        never_subscribed=never_subscribed or 0,
        total_revenue_estimate=total_revenue,
        tier_breakdown=tier_breakdown,
        monthly_trend=monthly_trend
    )
