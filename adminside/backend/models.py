"""
Models for Admin Portal
Reflects existing ArtPriv tables in Supabase (PostgreSQL with native UUIDs)
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from database import Base


# ========== Enums ==========
class DonorState(str, enum.Enum):
    VISITOR = "visitor"
    BANK_SELECTED = "bank_selected"
    LEAD_CREATED = "lead_created"
    ACCOUNT_CREATED = "account_created"
    COUNSELING_REQUESTED = "counseling_requested"
    CONSENT_PENDING = "consent_pending"
    CONSENT_VERIFIED = "consent_verified"
    TESTS_PENDING = "tests_pending"
    ELIGIBILITY_DECISION = "eligibility_decision"
    DONOR_ONBOARDED = "donor_onboarded"


class BankState(str, enum.Enum):
    UNREGISTERED = "unregistered"
    ACCOUNT_CREATED = "account_created"
    VERIFICATION_PENDING = "verification_pending"
    VERIFIED = "verified"
    SUBSCRIPTION_PENDING = "subscription_pending"
    SUBSCRIBED_ONBOARDED = "subscribed_onboarded"
    OPERATIONAL = "operational"


class EligibilityStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SUPPORT = "support"
    VIEWER = "viewer"


# ========== Models (reflect existing ArtPriv tables with native UUID) ==========
class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    state = Column(String, default="account_created", nullable=False)
    
    address = Column(Text)
    phone = Column(String)
    website = Column(String)
    description = Column(Text)
    
    certification_documents = Column(JSON)
    
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    verified_by = Column(String)
    
    is_subscribed = Column(Boolean, default=False)
    subscription_tier = Column(String)
    subscription_started_at = Column(DateTime(timezone=True))
    subscription_expires_at = Column(DateTime(timezone=True))
    billing_details = Column(JSON)
    
    counseling_config = Column(JSON)
    logo_url = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Donor(Base):
    __tablename__ = "donors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    state = Column(String, default="visitor", nullable=False)
    
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    date_of_birth = Column(DateTime(timezone=True))
    address = Column(Text)
    
    medical_interest_info = Column(JSON)
    
    bank_id = Column(UUID(as_uuid=True), ForeignKey("banks.id"))
    selected_at = Column(DateTime(timezone=True))
    
    legal_documents = Column(JSON)
    
    consent_pending = Column(Boolean, default=False)
    counseling_pending = Column(Boolean, default=False)
    tests_pending = Column(Boolean, default=False)
    
    eligibility_status = Column(String, default="pending")
    eligibility_notes = Column(Text)
    eligibility_decided_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DonorStateHistory(Base):
    __tablename__ = "donor_state_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("donors.id"), nullable=False)
    
    from_state = Column(String)
    to_state = Column(String, nullable=False)
    
    changed_by = Column(String)
    changed_by_role = Column(String)
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BankStateHistory(Base):
    __tablename__ = "bank_state_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_id = Column(UUID(as_uuid=True), ForeignKey("banks.id"), nullable=False)
    
    from_state = Column(String)
    to_state = Column(String, nullable=False)
    
    changed_by = Column(String)
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ========== Admin-specific models ==========
class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="viewer", nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=False)
    
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String)  # Keep as string since it can reference different tables
    
    details = Column(JSON)
    ip_address = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
