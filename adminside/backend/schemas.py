"""Admin-specific Pydantic schemas"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========== Admin Auth Schemas ==========
class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    role: str
    name: str


class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    role: str = "viewer"


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: EmailStr
    name: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime


# ========== Dashboard Schemas ==========
class DashboardStats(BaseModel):
    total_banks: int
    verified_banks: int
    subscribed_banks: int
    operational_banks: int
    total_donors: int
    onboarded_donors: int
    pending_verifications: int
    expiring_subscriptions: int
    expired_subscriptions: int
    recent_signups: int


class SubscriptionSummary(BaseModel):
    tier: str
    count: int
    revenue_estimate: float


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    admin_id: str
    admin_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime


class DashboardResponse(BaseModel):
    stats: DashboardStats
    subscription_breakdown: List[SubscriptionSummary]
    recent_activity: List[ActivityLogResponse]


# ========== Bank Management Schemas ==========
class BankAdminView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    name: str
    state: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_verified: bool
    verified_at: Optional[datetime] = None
    is_subscribed: bool
    subscription_tier: Optional[str] = None
    subscription_started_at: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None
    donor_count: int = 0
    created_at: datetime


class BankListResponse(BaseModel):
    items: List[BankAdminView]
    total: int
    page: int
    page_size: int
    total_pages: int


class BankVerifyRequest(BaseModel):
    verified_by: str
    notes: Optional[str] = None


class SubscriptionUpdateRequest(BaseModel):
    subscription_tier: str
    subscription_started_at: datetime
    subscription_expires_at: datetime
    notes: Optional[str] = None


# ========== Donor Management Schemas ==========
class DonorAdminView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    state: str
    bank_id: Optional[str] = None
    bank_name: Optional[str] = None
    eligibility_status: str
    created_at: datetime


class DonorListResponse(BaseModel):
    items: List[DonorAdminView]
    total: int
    page: int
    page_size: int
    total_pages: int


class StateHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    from_state: Optional[str] = None
    to_state: str
    changed_by: Optional[str] = None
    changed_by_role: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime


class DonorDetailAdminView(DonorAdminView):
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    medical_interest_info: Optional[Dict[str, Any]] = None
    eligibility_notes: Optional[str] = None
    selected_at: Optional[datetime] = None
    consent_pending: bool = False
    counseling_pending: bool = False
    tests_pending: bool = False
    state_history: List[StateHistoryItem] = []


# ========== Activity Log Schemas ==========
class ActivityLogListResponse(BaseModel):
    items: List[ActivityLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== Subscription Analytics ==========
class MonthlySubscriptionTrend(BaseModel):
    month: str
    new_subscriptions: int
    renewals: int
    churned: int


class SubscriptionAnalytics(BaseModel):
    active_subscriptions: int
    expiring_soon: int
    expired: int
    never_subscribed: int
    total_revenue_estimate: float
    tier_breakdown: List[SubscriptionSummary]
    monthly_trend: List[MonthlySubscriptionTrend]
