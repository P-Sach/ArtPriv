from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid as uuid_module
from models.models import (
    DonorState,
    BankState,
    ConsentStatus,
    CounselingMethod,
    CounselingStatus,
    TestReportSource,
    EligibilityStatus
)


# ========== Base Schemas ==========
class UUIDMixin(BaseModel):
    """Mixin to handle UUID to string conversion for id fields"""
    @field_validator('id', 'bank_id', 'donor_id', 'template_id', 'consent_id', 'session_id', 'user_id', mode='before', check_fields=False)
    @classmethod
    def convert_uuid_to_str(cls, value):
        if isinstance(value, uuid_module.UUID):
            return str(value)
        return value


class TimestampMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Auth Schemas ==========
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str  # 'donor' or 'bank'
    user_id: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ========== Bank Schemas ==========
class BankRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class BankUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class BankCounselingConfig(BaseModel):
    methods: List[CounselingMethod] = Field(..., min_items=1)
    time_slots: List[Dict[str, Any]]  # [{day: 'Monday', start: '09:00', end: '17:00'}]
    auto_approve: bool = False


class BankSubscriptionCreate(BaseModel):
    subscription_tier: str
    billing_details: Dict[str, Any]


class BankResponse(UUIDMixin, TimestampMixin):
    id: str
    email: EmailStr
    name: str
    state: BankState
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_verified: bool
    is_subscribed: bool
    subscription_tier: Optional[str] = None
    logo_url: Optional[str] = None
    counseling_config: Optional[Dict[str, Any]] = None


class BankListItem(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# ========== Donor Schemas ==========
class DonorLeadCreate(BaseModel):
    """Initial lead creation when donor shows interest"""
    bank_id: str
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str
    medical_interest_info: Dict[str, Any]  # Free-form medical interest data


class DonorAccountCreate(BaseModel):
    """Account creation for existing lead"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    legal_documents: Optional[List[str]] = None  # Document URLs


class DonorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class DonorResponse(UUIDMixin, TimestampMixin):
    id: str
    email: Optional[EmailStr] = None
    state: DonorState
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bank_id: Optional[str] = None
    eligibility_status: EligibilityStatus
    consent_pending: bool
    counseling_pending: bool
    tests_pending: bool


class DonorDetailResponse(DonorResponse):
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    medical_interest_info: Optional[Dict[str, Any]] = None
    eligibility_notes: Optional[str] = None
    selected_at: Optional[datetime] = None


# ========== Consent Schemas ==========
class ConsentTemplateCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    order: int = Field(1, ge=1, le=4)
    version: str = "1.0"


class ConsentTemplateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = Field(None, ge=1, le=4)
    is_active: Optional[bool] = None


class ConsentTemplateResponse(UUIDMixin, TimestampMixin):
    id: str
    bank_id: str
    title: str
    content: str
    version: str
    order: int
    is_active: bool


class DonorConsentSign(BaseModel):
    template_id: str
    signature_data: Optional[Dict[str, Any]] = None  # Can include signature image URL, IP, etc.


class DonorConsentVerify(BaseModel):
    consent_id: str
    status: ConsentStatus  # 'verified' or 'rejected'
    verification_notes: Optional[str] = None


class DonorConsentResponse(UUIDMixin, TimestampMixin):
    id: str
    donor_id: str
    template_id: str
    status: ConsentStatus
    signed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    template: Optional[ConsentTemplateResponse] = None


# ========== Counseling Schemas ==========
class CounselingSessionRequest(BaseModel):
    method: CounselingMethod
    notes: Optional[str] = None


class CounselingSessionSchedule(BaseModel):
    session_id: str
    scheduled_at: datetime
    meeting_link: Optional[str] = None
    location: Optional[str] = None


class CounselingSessionUpdate(BaseModel):
    status: Optional[CounselingStatus] = None
    scheduled_at: Optional[datetime] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class CounselingSessionResponse(UUIDMixin, TimestampMixin):
    id: str
    donor_id: str
    bank_id: str
    status: CounselingStatus
    method: Optional[CounselingMethod] = None
    requested_at: datetime
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


# ========== Test Report Schemas ==========
class TestReportCreate(BaseModel):
    test_type: str
    test_name: str
    file_url: str
    file_name: Optional[str] = None
    test_date: Optional[datetime] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None


class TestReportResponse(UUIDMixin, TimestampMixin):
    id: str
    donor_id: str
    bank_id: str
    source: TestReportSource
    test_type: str
    test_name: str
    file_url: str
    file_name: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime
    test_date: Optional[datetime] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None


# ========== Eligibility Schemas ==========
class EligibilityDecision(BaseModel):
    donor_id: str
    status: EligibilityStatus  # 'approved' or 'rejected'
    notes: Optional[str] = None


# ========== State History Schemas ==========
class StateHistoryResponse(BaseModel):
    id: str
    from_state: Optional[str] = None
    to_state: str
    changed_by: Optional[str] = None
    changed_by_role: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Public Schemas ==========
class BankSearchParams(BaseModel):
    location: Optional[str] = None
    search: Optional[str] = None


# ========== Pagination ==========
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
