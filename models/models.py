from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


# Enums for state machines
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


class ConsentStatus(str, enum.Enum):
    PENDING = "pending"
    SIGNED = "signed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class CounselingMethod(str, enum.Enum):
    CALL = "call"
    VIDEO = "video"
    IN_PERSON = "in_person"
    EMAIL = "email"


class CounselingStatus(str, enum.Enum):
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestReportSource(str, enum.Enum):
    BANK_CONDUCTED = "bank_conducted"  # Only banks can upload test reports


class EligibilityStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Models
class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    state = Column(SQLEnum(BankState, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), default=BankState.ACCOUNT_CREATED, nullable=False)
    
    # Basic info
    address = Column(Text)
    phone = Column(String)
    website = Column(String)
    description = Column(Text)
    
    # Certification
    certification_documents = Column(JSON)  # List of document URLs
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    verified_by = Column(String)  # Admin ID
    
    # Subscription
    is_subscribed = Column(Boolean, default=False)
    subscription_tier = Column(String)
    subscription_started_at = Column(DateTime(timezone=True))
    subscription_expires_at = Column(DateTime(timezone=True))
    billing_details = Column(JSON)
    
    # Counseling configuration
    counseling_config = Column(JSON)  # {methods: [], time_slots: [], auto_approve: bool}
    
    # Branding
    logo_url = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    donors = relationship("Donor", back_populates="bank")
    consent_templates = relationship("ConsentTemplate", back_populates="bank")
    counseling_sessions = relationship("CounselingSession", back_populates="bank")
    test_reports = relationship("TestReport", back_populates="bank")


class Donor(Base):
    __tablename__ = "donors"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    state = Column(SQLEnum(DonorState, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), default=DonorState.VISITOR, nullable=False)
    
    # Personal info
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    date_of_birth = Column(DateTime(timezone=True))
    address = Column(Text)
    
    # Medical interest info (from lead creation)
    medical_interest_info = Column(JSON)
    
    # Bank association
    bank_id = Column(String, ForeignKey("banks.id"))
    selected_at = Column(DateTime(timezone=True))  # When bank was selected
    
    # Legal documents
    legal_documents = Column(JSON)  # Uploaded documents if required
    
    # Status flags
    consent_pending = Column(Boolean, default=False)
    counseling_pending = Column(Boolean, default=False)
    tests_pending = Column(Boolean, default=False)
    
    # Eligibility
    eligibility_status = Column(SQLEnum(EligibilityStatus, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), default=EligibilityStatus.PENDING)
    eligibility_notes = Column(Text)
    eligibility_decided_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bank = relationship("Bank", back_populates="donors")
    consents = relationship("DonorConsent", back_populates="donor")
    counseling_sessions = relationship("CounselingSession", back_populates="donor")
    test_reports = relationship("TestReport", back_populates="donor")
    state_history = relationship("DonorStateHistory", back_populates="donor")


class ConsentTemplate(Base):
    __tablename__ = "consent_templates"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    bank_id = Column(String, ForeignKey("banks.id"), nullable=False)
    
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String, default="1.0")
    order = Column(Integer, default=1)  # Order of display (1-4)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bank = relationship("Bank", back_populates="consent_templates")
    donor_consents = relationship("DonorConsent", back_populates="template")


class DonorConsent(Base):
    __tablename__ = "donor_consents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    donor_id = Column(String, ForeignKey("donors.id"), nullable=False)
    template_id = Column(String, ForeignKey("consent_templates.id"), nullable=False)
    
    status = Column(SQLEnum(ConsentStatus, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), default=ConsentStatus.PENDING, nullable=False)
    
    # Digital signature
    signed_at = Column(DateTime(timezone=True))
    signature_data = Column(JSON)  # Can store signature image URL, IP, etc.
    
    # Bank verification
    verified_at = Column(DateTime(timezone=True))
    verified_by = Column(String)  # Bank user ID
    verification_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    donor = relationship("Donor", back_populates="consents")
    template = relationship("ConsentTemplate", back_populates="donor_consents")


class CounselingSession(Base):
    __tablename__ = "counseling_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    donor_id = Column(String, ForeignKey("donors.id"), nullable=False)
    bank_id = Column(String, ForeignKey("banks.id"), nullable=False)
    
    status = Column(SQLEnum(CounselingStatus, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), default=CounselingStatus.REQUESTED, nullable=False)
    method = Column(SQLEnum(CounselingMethod, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False))
    
    # Scheduling
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Details
    meeting_link = Column(String)  # For video calls
    location = Column(String)  # For in-person
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    donor = relationship("Donor", back_populates="counseling_sessions")
    bank = relationship("Bank", back_populates="counseling_sessions")


class TestReport(Base):
    __tablename__ = "test_reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    donor_id = Column(String, ForeignKey("donors.id"), nullable=False)
    bank_id = Column(String, ForeignKey("banks.id"), nullable=False)
    
    source = Column(SQLEnum(TestReportSource, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), nullable=False)
    
    # Report details
    test_type = Column(String, nullable=False)
    test_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_name = Column(String)
    
    # Upload info
    uploaded_by = Column(String)  # User ID (bank or donor)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    test_date = Column(DateTime(timezone=True))
    lab_name = Column(String)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    donor = relationship("Donor", back_populates="test_reports")
    bank = relationship("Bank", back_populates="test_reports")


class DonorStateHistory(Base):
    __tablename__ = "donor_state_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    donor_id = Column(String, ForeignKey("donors.id"), nullable=False)
    
    from_state = Column(SQLEnum(DonorState, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False))
    to_state = Column(SQLEnum(DonorState, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), nullable=False)
    
    changed_by = Column(String)  # User ID (system, bank, or donor)
    changed_by_role = Column(String)  # 'system', 'bank', 'donor'
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    donor = relationship("Donor", back_populates="state_history")


class BankStateHistory(Base):
    __tablename__ = "bank_state_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    bank_id = Column(String, ForeignKey("banks.id"), nullable=False)
    
    from_state = Column(SQLEnum(BankState, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False))
    to_state = Column(SQLEnum(BankState, values_callable=lambda x: [e.value for e in x], native_enum=True, create_constraint=False), nullable=False)
    
    changed_by = Column(String)  # Admin ID
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
