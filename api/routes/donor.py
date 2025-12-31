from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import (
    Donor, Bank, DonorConsent, ConsentTemplate, CounselingSession,
    TestReport, DonorState, ConsentStatus, CounselingStatus
)
from schemas import (
    DonorLeadCreate, DonorAccountCreate, DonorResponse, DonorDetailResponse,
    DonorConsentSign, DonorConsentResponse, CounselingSessionRequest,
    CounselingSessionResponse, TestReportResponse,
    ConsentTemplateResponse, StateHistoryResponse
)
from utils import (
    get_current_donor, hash_password, transition_donor_state
)

router = APIRouter()


@router.post("/lead", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: DonorLeadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a donor lead when they select a bank
    This is the first step in the donor journey
    """
    # Verify bank exists and is operational
    bank = db.query(Bank).filter(Bank.id == lead_data.bank_id).first()
    if not bank or not bank.is_verified or not bank.is_subscribed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive bank"
        )
    
    # Check if donor already has a lead with this email
    existing_donor = db.query(Donor).filter(Donor.email == lead_data.email).first()
    if existing_donor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create donor lead
    donor = Donor(
        email=lead_data.email,
        first_name=lead_data.first_name,
        last_name=lead_data.last_name,
        phone=lead_data.phone,
        medical_interest_info=lead_data.medical_interest_info,
        bank_id=bank.id,
        selected_at=datetime.utcnow(),
        state=DonorState.BANK_SELECTED,
        consent_pending=True,
        counseling_pending=True,
        tests_pending=True
    )
    
    db.add(donor)
    db.commit()
    db.refresh(donor)
    
    # Transition to lead created
    transition_donor_state(
        db, donor, DonorState.LEAD_CREATED,
        changed_by=donor.id,
        changed_by_role="donor",
        reason="Lead created with bank selection"
    )
    
    return donor


@router.post("/account", response_model=DonorResponse)
async def create_account(
    account_data: DonorAccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create account for an existing lead
    Donor sets password and uploads legal documents if required
    """
    # Find donor by email
    donor = db.query(Donor).filter(Donor.email == account_data.email).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found. Please create a lead first."
        )
    
    if donor.state != DonorState.LEAD_CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already created or invalid state"
        )
    
    # Set password
    donor.hashed_password = hash_password(account_data.password)
    
    # Save legal documents if provided
    if account_data.legal_documents:
        donor.legal_documents = account_data.legal_documents
    
    # Transition to account created
    transition_donor_state(
        db, donor, DonorState.ACCOUNT_CREATED,
        changed_by=donor.id,
        changed_by_role="donor",
        reason="Account created with credentials"
    )
    
    return donor


@router.get("/me", response_model=DonorDetailResponse)
async def get_my_profile(
    current_donor: Donor = Depends(get_current_donor)
):
    """Get current donor's profile"""
    return current_donor


@router.get("/consents", response_model=List[DonorConsentResponse])
async def get_my_consents(
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Get all consents for current donor with template details"""
    consents = db.query(DonorConsent).filter(
        DonorConsent.donor_id == current_donor.id
    ).all()
    
    # Load templates
    result = []
    for consent in consents:
        template = db.query(ConsentTemplate).filter(
            ConsentTemplate.id == consent.template_id
        ).first()
        
        consent_dict = DonorConsentResponse.from_orm(consent).dict()
        if template:
            consent_dict["template"] = ConsentTemplateResponse.from_orm(template)
        result.append(consent_dict)
    
    return result


@router.get("/consents/templates", response_model=List[ConsentTemplateResponse])
async def get_consent_templates(
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Get all consent templates from donor's bank"""
    if not current_donor.bank_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bank associated"
        )
    
    templates = db.query(ConsentTemplate).filter(
        ConsentTemplate.bank_id == current_donor.bank_id,
        ConsentTemplate.is_active == True
    ).order_by(ConsentTemplate.order).all()
    
    return templates


@router.post("/consents/sign", response_model=DonorConsentResponse, status_code=status.HTTP_201_CREATED)
async def sign_consent(
    consent_data: DonorConsentSign,
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Sign a consent form"""
    # STATE VALIDATION: Donor must be in CONSENT_PENDING or COUNSELING_REQUESTED state
    if current_donor.state not in [DonorState.CONSENT_PENDING, DonorState.COUNSELING_REQUESTED, DonorState.ACCOUNT_CREATED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot sign consents in current state: {current_donor.state.value}"
        )
    
    # Verify template exists and belongs to donor's bank
    template = db.query(ConsentTemplate).filter(
        ConsentTemplate.id == consent_data.template_id,
        ConsentTemplate.bank_id == current_donor.bank_id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent template not found"
        )
    
    # Check if already signed
    existing = db.query(DonorConsent).filter(
        DonorConsent.donor_id == current_donor.id,
        DonorConsent.template_id == consent_data.template_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent already signed"
        )
    
    # Create consent
    consent = DonorConsent(
        donor_id=current_donor.id,
        template_id=consent_data.template_id,
        status=ConsentStatus.SIGNED,
        signed_at=datetime.utcnow(),
        signature_data=consent_data.signature_data
    )
    
    db.add(consent)
    
    # Check if all 4 consents are signed
    total_consents = db.query(DonorConsent).filter(
        DonorConsent.donor_id == current_donor.id,
        DonorConsent.status == ConsentStatus.SIGNED
    ).count()
    
    # Update state if moving to consent pending for first time
    if current_donor.state == DonorState.COUNSELING_REQUESTED and total_consents == 0:
        transition_donor_state(
            db, current_donor, DonorState.CONSENT_PENDING,
            changed_by=current_donor.id,
            changed_by_role="donor",
            reason="Started signing consent forms"
        )
    
    db.commit()
    db.refresh(consent)
    
    return consent


@router.post("/counseling/request", response_model=CounselingSessionResponse, status_code=status.HTTP_201_CREATED)
async def request_counseling(
    request_data: CounselingSessionRequest,
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Request counseling session"""
    if current_donor.state != DonorState.ACCOUNT_CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state for counseling request"
        )
    
    if not current_donor.bank_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bank associated"
        )
    
    # Verify method is supported by bank
    bank = db.query(Bank).filter(Bank.id == current_donor.bank_id).first()
    if bank.counseling_config:
        allowed_methods = bank.counseling_config.get("methods", [])
        if request_data.method.value not in allowed_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Counseling method {request_data.method} not supported by bank"
            )
    
    # Create counseling session
    session = CounselingSession(
        donor_id=current_donor.id,
        bank_id=current_donor.bank_id,
        method=request_data.method,
        status=CounselingStatus.REQUESTED,
        notes=request_data.notes
    )
    
    db.add(session)
    
    # Transition donor state
    transition_donor_state(
        db, current_donor, DonorState.COUNSELING_REQUESTED,
        changed_by=current_donor.id,
        changed_by_role="donor",
        reason="Counseling requested"
    )
    
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/counseling", response_model=List[CounselingSessionResponse])
async def get_my_counseling_sessions(
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Get all counseling sessions for current donor"""
    sessions = db.query(CounselingSession).filter(
        CounselingSession.donor_id == current_donor.id
    ).all()
    
    return sessions


@router.get("/tests", response_model=List[TestReportResponse])
async def get_my_test_reports(
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Get all test reports for current donor (bank-conducted only)"""
    reports = db.query(TestReport).filter(
        TestReport.donor_id == current_donor.id
    ).all()
    
    return reports


@router.get("/state-history", response_model=List[StateHistoryResponse])
async def get_state_history(
    current_donor: Donor = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Get state transition history for current donor"""
    from models import DonorStateHistory
    
    history = db.query(DonorStateHistory).filter(
        DonorStateHistory.donor_id == current_donor.id
    ).order_by(DonorStateHistory.created_at.desc()).all()
    
    return history
