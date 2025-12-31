from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import (
    Bank, Donor, ConsentTemplate, DonorConsent, CounselingSession,
    TestReport, BankState, ConsentStatus, CounselingStatus,
    TestReportSource, EligibilityStatus, DonorState
)
from schemas import (
    BankResponse, BankUpdate, BankCounselingConfig, BankSubscriptionCreate,
    ConsentTemplateCreate, ConsentTemplateUpdate, ConsentTemplateResponse,
    DonorConsentVerify, CounselingSessionSchedule, CounselingSessionUpdate,
    CounselingSessionResponse, TestReportCreate, TestReportResponse, 
    EligibilityDecision, DonorResponse, DonorDetailResponse
)
from utils import (
    get_current_bank, get_verified_bank, get_subscribed_bank,
    transition_bank_state, transition_donor_state,
    save_upload_file, get_file_url
)

router = APIRouter()


# ========== Bank Profile & Settings ==========
@router.get("/me", response_model=BankResponse)
async def get_my_profile(
    current_bank: Bank = Depends(get_current_bank)
):
    """Get current bank's profile"""
    return current_bank


@router.put("/me", response_model=BankResponse)
async def update_profile(
    update_data: BankUpdate,
    current_bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db)
):
    """Update bank profile"""
    update_dict = update_data.dict(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(current_bank, key, value)
    
    db.commit()
    db.refresh(current_bank)
    
    return current_bank


@router.post("/certification/upload")
async def upload_certification(
    file: UploadFile = File(...),
    current_bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db)
):
    """Upload certification document (PDF only)"""
    # Upload PDF to Supabase Storage
    file_url = await save_upload_file(
        file=file,
        bucket="certification-documents",
        folder=f"bank_{current_bank.id}",
        validate_pdf=True
    )
    
    # Update bank's certification documents
    if current_bank.certification_documents is None:
        current_bank.certification_documents = []
    
    current_bank.certification_documents.append({
        "filename": file.filename,
        "url": file_url,
        "uploaded_at": datetime.utcnow().isoformat()
    })
    
    # Transition to verification pending if first document
    if current_bank.state == BankState.ACCOUNT_CREATED:
        transition_bank_state(
            db, current_bank, BankState.VERIFICATION_PENDING,
            changed_by=current_bank.id,
            reason="Certification documents uploaded"
        )
    
    db.commit()
    
    return {"message": "Certification uploaded successfully", "url": file_url}


@router.put("/counseling/config", response_model=BankResponse)
async def update_counseling_config(
    config: BankCounselingConfig,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Configure counseling settings"""
    current_bank.counseling_config = config.dict()
    db.commit()
    db.refresh(current_bank)
    
    return current_bank


@router.post("/subscription", response_model=BankResponse)
async def create_subscription(
    subscription_data: BankSubscriptionCreate,
    current_bank: Bank = Depends(get_verified_bank),
    db: Session = Depends(get_db)
):
    """Create subscription for verified bank"""
    if current_bank.state != BankState.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank must be verified first"
        )
    
    # In a real system, this would integrate with payment processor
    current_bank.subscription_tier = subscription_data.subscription_tier
    current_bank.billing_details = subscription_data.billing_details
    current_bank.is_subscribed = True
    current_bank.subscription_started_at = datetime.utcnow()
    
    # Transition to subscribed state
    transition_bank_state(
        db, current_bank, BankState.SUBSCRIPTION_PENDING,
        changed_by=current_bank.id,
        reason="Subscription initiated"
    )
    
    transition_bank_state(
        db, current_bank, BankState.SUBSCRIBED_ONBOARDED,
        changed_by=current_bank.id,
        reason="Subscription completed"
    )
    
    transition_bank_state(
        db, current_bank, BankState.OPERATIONAL,
        changed_by=current_bank.id,
        reason="Bank is now operational"
    )
    
    db.commit()
    db.refresh(current_bank)
    
    return current_bank


# ========== Donor Management ==========
@router.get("/donors", response_model=List[DonorResponse])
async def get_my_donors(
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Get all donors associated with this bank"""
    donors = db.query(Donor).filter(Donor.bank_id == current_bank.id).all()
    return donors


@router.get("/donors/{donor_id}", response_model=DonorDetailResponse)
async def get_donor_details(
    donor_id: str,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific donor"""
    donor = db.query(Donor).filter(
        Donor.id == donor_id,
        Donor.bank_id == current_bank.id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    
    return donor


# ========== Consent Management ==========
@router.post("/consents/templates/upload")
async def upload_consent_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    order: int = Form(...),
    version: str = Form("1.0"),
    current_bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db)
):
    """Upload a consent template PDF (banks can upload up to 4 consent forms)"""
    # Verify order is within 1-4 range
    if order < 1 or order > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent order must be between 1 and 4"
        )
    
    # Upload PDF to Supabase Storage
    file_url = await save_upload_file(
        file=file,
        bucket="consent-forms",
        folder=f"bank_{current_bank.id}",
        validate_pdf=True
    )
    
    # Create template record with file URL
    template = ConsentTemplate(
        bank_id=current_bank.id,
        title=title,
        content=file_url,  # Store file URL in content field
        order=order,
        version=version
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {
        "message": "Consent template uploaded successfully",
        "template_id": str(template.id),
        "title": template.title,
        "order": template.order,
        "file_url": file_url
    }


# TESTING ONLY: For automated tests - Production should use /upload endpoint above
@router.post("/consents/templates", status_code=status.HTTP_201_CREATED)
async def create_consent_template_test(
    template_data: ConsentTemplateCreate,
    current_bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db)
):
    """
    **FOR TESTING ONLY** - Create consent template with text content
    
    Production systems should use POST /consents/templates/upload with PDF files.
    This endpoint allows tests to run without file upload complexity.
    The 'content' field will store either text (testing) or PDF URL (production).
    """
    # Verify order is within 1-4 range
    if template_data.order < 1 or template_data.order > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent order must be between 1 and 4"
        )
    
    # Create template record
    template = ConsentTemplate(
        bank_id=current_bank.id,
        title=template_data.title,
        content=template_data.content,  # Text for testing, PDF URL for production
        order=template_data.order,
        version=template_data.version
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {
        "template_id": str(template.id),
        "title": template.title,
        "order": template.order,
        "version": template.version
    }


@router.get("/consents/templates")
async def get_my_consent_templates(
    current_bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db)
):
    """Get all consent templates for this bank"""
    templates = db.query(ConsentTemplate).filter(
        ConsentTemplate.bank_id == current_bank.id
    ).order_by(ConsentTemplate.order).all()
    
    return [
        {
            "id": str(template.id),
            "title": template.title,
            "order": template.order,
            "version": template.version,
            "file_url": template.content,  # Content field stores file URL
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat() if template.created_at else None
        }
        for template in templates
    ]


@router.put("/consents/templates/{template_id}")
async def update_consent_template(
    template_id: str,
    file: UploadFile = File(None),
    title: str = None,
    order: int = None,
    is_active: bool = None,
    current_bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db)
):
    """Update a consent template (can replace PDF file or update metadata)"""
    template = db.query(ConsentTemplate).filter(
        ConsentTemplate.id == template_id,
        ConsentTemplate.bank_id == current_bank.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent template not found"
        )
    
    # Update file if provided
    if file:
        file_url = await save_upload_file(
            file=file,
            bucket="consent-forms",
            folder=f"bank_{current_bank.id}",
            validate_pdf=True
        )
        template.content = file_url
    
    # Update other fields
    if title is not None:
        template.title = title
    if order is not None:
        if order < 1 or order > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consent order must be between 1 and 4"
            )
        template.order = order
    if is_active is not None:
        template.is_active = is_active
    
    db.commit()
    db.refresh(template)
    
    return {
        "message": "Consent template updated successfully",
        "template_id": str(template.id),
        "title": template.title,
        "order": template.order,
        "file_url": template.content
    }


@router.post("/consents/verify")
async def verify_consent(
    verify_data: DonorConsentVerify,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Verify a donor's consent"""
    consent = db.query(DonorConsent).filter(
        DonorConsent.id == verify_data.consent_id
    ).first()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found"
        )
    
    # Verify consent belongs to a donor of this bank
    donor = db.query(Donor).filter(
        Donor.id == consent.donor_id,
        Donor.bank_id == current_bank.id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this consent"
        )
    
    # Update consent
    consent.status = verify_data.status
    consent.verified_at = datetime.utcnow()
    consent.verified_by = current_bank.id
    consent.verification_notes = verify_data.verification_notes
    
    # Check if all consents are verified
    total_consents = db.query(DonorConsent).filter(
        DonorConsent.donor_id == donor.id
    ).count()
    
    verified_consents = db.query(DonorConsent).filter(
        DonorConsent.donor_id == donor.id,
        DonorConsent.status == ConsentStatus.VERIFIED
    ).count()
    
    # If all 4 consents verified, transition donor state
    if total_consents >= 4 and verified_consents >= 4:
        if donor.state == DonorState.CONSENT_PENDING:
            transition_donor_state(
                db, donor, DonorState.CONSENT_VERIFIED,
                changed_by=current_bank.id,
                changed_by_role="bank",
                reason="All consents verified by bank"
            )
    
    db.commit()
    
    return {"message": "Consent verified successfully"}


# ========== Counseling Management ==========
@router.get("/counseling/requests", response_model=List[CounselingSessionResponse])
async def get_counseling_requests(
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Get all counseling requests for this bank"""
    sessions = db.query(CounselingSession).filter(
        CounselingSession.bank_id == current_bank.id
    ).all()
    
    return sessions


@router.post("/counseling/schedule")
async def schedule_counseling(
    schedule_data: CounselingSessionSchedule,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Schedule a counseling session"""
    session = db.query(CounselingSession).filter(
        CounselingSession.id == schedule_data.session_id,
        CounselingSession.bank_id == current_bank.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling session not found"
        )
    
    session.status = CounselingStatus.SCHEDULED
    session.scheduled_at = schedule_data.scheduled_at
    session.meeting_link = schedule_data.meeting_link
    session.location = schedule_data.location
    
    db.commit()
    
    return {"message": "Counseling scheduled successfully"}


@router.put("/counseling/{session_id}")
async def update_counseling_session(
    session_id: str,
    update_data: CounselingSessionUpdate,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Update a counseling session"""
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id,
        CounselingSession.bank_id == current_bank.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling session not found"
        )
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(session, key, value)
    
    # If marking as completed, set completed_at
    if update_data.status == CounselingStatus.COMPLETED:
        session.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Counseling session updated successfully"}


# ========== Test Report Management ==========
@router.post("/tests/upload", response_model=TestReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_test_report(
    donor_id: str,
    test_type: str,
    test_name: str,
    file: UploadFile = File(...),
    test_date: datetime = None,
    lab_name: str = None,
    notes: str = None,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Upload test report for a donor (bank-conducted tests, PDF only)"""
    # Verify donor belongs to this bank
    donor = db.query(Donor).filter(
        Donor.id == donor_id,
        Donor.bank_id == current_bank.id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    
    # STATE VALIDATION: Donor should be in CONSENT_VERIFIED or TESTS_PENDING state
    if donor.state not in [DonorState.CONSENT_VERIFIED, DonorState.TESTS_PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload tests for donor in state: {donor.state.value}. Donor must have verified consents first."
        )
    
    # Upload PDF to Supabase Storage
    file_url = await save_upload_file(
        file=file,
        bucket="test-reports",
        folder=f"donor_{donor_id}/bank_conducted",
        validate_pdf=True
    )
    
    # Create test report
    report = TestReport(
        donor_id=donor.id,
        bank_id=current_bank.id,
        source=TestReportSource.BANK_CONDUCTED,
        test_type=test_type,
        test_name=test_name,
        file_url=file_url,
        file_name=file.filename,
        uploaded_by=current_bank.id,
        test_date=test_date,
        lab_name=lab_name,
        notes=notes
    )
    
    db.add(report)
    
    # Transition donor state if needed
    if donor.state == DonorState.CONSENT_VERIFIED:
        transition_donor_state(
            db, donor, DonorState.TESTS_PENDING,
            changed_by=current_bank.id,
            changed_by_role="bank",
            reason="Test report uploaded by bank"
        )
    
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/tests/donor/{donor_id}", response_model=List[TestReportResponse])
async def get_donor_test_reports(
    donor_id: str,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Get all test reports for a specific donor"""
    # Verify donor belongs to this bank
    donor = db.query(Donor).filter(
        Donor.id == donor_id,
        Donor.bank_id == current_bank.id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    
    reports = db.query(TestReport).filter(
        TestReport.donor_id == donor_id
    ).all()
    
    return reports


# ========== Eligibility Decision ==========
@router.post("/eligibility/decide")
async def make_eligibility_decision(
    decision: EligibilityDecision,
    current_bank: Bank = Depends(get_subscribed_bank),
    db: Session = Depends(get_db)
):
    """Make final eligibility decision for a donor (BANK AUTHORITY ONLY)"""
    # Verify donor belongs to this bank
    donor = db.query(Donor).filter(
        Donor.id == decision.donor_id,
        Donor.bank_id == current_bank.id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    
    if donor.state != DonorState.TESTS_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donor must be in tests_pending state"
        )
    
    # Update donor eligibility
    donor.eligibility_status = decision.status
    donor.eligibility_notes = decision.notes
    donor.eligibility_decided_at = datetime.utcnow()
    
    # Transition to eligibility decision state
    transition_donor_state(
        db, donor, DonorState.ELIGIBILITY_DECISION,
        changed_by=current_bank.id,
        changed_by_role="bank",
        reason=f"Eligibility decision: {decision.status.value}"
    )
    
    # If approved, transition to onboarded
    if decision.status == EligibilityStatus.APPROVED:
        transition_donor_state(
            db, donor, DonorState.DONOR_ONBOARDED,
            changed_by=current_bank.id,
            changed_by_role="bank",
            reason="Donor approved and onboarded"
        )
    
    db.commit()
    
    return {
        "message": "Eligibility decision recorded successfully",
        "status": decision.status.value
    }
