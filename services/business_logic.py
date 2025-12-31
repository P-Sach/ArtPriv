from sqlalchemy.orm import Session
from typing import Optional
from models import Donor, Bank, DonorState, BankState
from fastapi import HTTPException, status


class DonorService:
    """Business logic for donor operations"""
    
    @staticmethod
    def validate_lead_creation(db: Session, email: str, bank_id: str) -> Bank:
        """Validate that a lead can be created"""
        # Check if email already exists
        existing = db.query(Donor).filter(Donor.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Donor with this email already exists"
            )
        
        # Verify bank is operational
        bank = db.query(Bank).filter(Bank.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank not found"
            )
        
        if not bank.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank is not verified"
            )
        
        if not bank.is_subscribed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank does not have an active subscription"
            )
        
        return bank
    
    @staticmethod
    def can_request_counseling(donor: Donor) -> bool:
        """Check if donor can request counseling"""
        return donor.state == DonorState.ACCOUNT_CREATED
    
    @staticmethod
    def can_sign_consent(donor: Donor) -> bool:
        """Check if donor can sign consents"""
        return donor.state in [
            DonorState.COUNSELING_REQUESTED,
            DonorState.CONSENT_PENDING
        ]
    
    @staticmethod
    def can_upload_tests(donor: Donor) -> bool:
        """Check if donor can upload test reports"""
        return donor.state in [
            DonorState.CONSENT_VERIFIED,
            DonorState.TESTS_PENDING
        ]
    
    @staticmethod
    def get_all_consents_count(db: Session, donor_id: str) -> tuple:
        """Get count of total and signed/verified consents"""
        from models import DonorConsent, ConsentStatus
        
        total = db.query(DonorConsent).filter(
            DonorConsent.donor_id == donor_id
        ).count()
        
        signed = db.query(DonorConsent).filter(
            DonorConsent.donor_id == donor_id,
            DonorConsent.status.in_([ConsentStatus.SIGNED, ConsentStatus.VERIFIED])
        ).count()
        
        verified = db.query(DonorConsent).filter(
            DonorConsent.donor_id == donor_id,
            DonorConsent.status == ConsentStatus.VERIFIED
        ).count()
        
        return total, signed, verified


class BankService:
    """Business logic for bank operations"""
    
    @staticmethod
    def can_manage_donors(bank: Bank) -> bool:
        """Check if bank can manage donors"""
        return bank.is_verified and bank.is_subscribed
    
    @staticmethod
    def validate_verification_ready(bank: Bank) -> bool:
        """Check if bank is ready for verification"""
        if not bank.certification_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certification documents required"
            )
        return True
    
    @staticmethod
    def validate_subscription_ready(bank: Bank) -> bool:
        """Check if bank can subscribe"""
        if not bank.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank must be verified before subscribing"
            )
        return True
    
    @staticmethod
    def can_verify_consent(bank: Bank, donor: Donor) -> bool:
        """Check if bank can verify donor's consent"""
        if donor.bank_id != bank.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Donor does not belong to this bank"
            )
        
        if not bank.is_subscribed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active subscription required"
            )
        
        return True
    
    @staticmethod
    def can_make_eligibility_decision(bank: Bank, donor: Donor) -> bool:
        """Check if bank can make eligibility decision"""
        if donor.bank_id != bank.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Donor does not belong to this bank"
            )
        
        if donor.state != DonorState.TESTS_PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Donor must complete testing before eligibility decision"
            )
        
        return True


class ConsentService:
    """Business logic for consent operations"""
    
    @staticmethod
    def validate_consent_template_count(db: Session, bank_id: str) -> bool:
        """Ensure bank has exactly 4 consent templates"""
        from models import ConsentTemplate
        
        count = db.query(ConsentTemplate).filter(
            ConsentTemplate.bank_id == bank_id,
            ConsentTemplate.is_active == True
        ).count()
        
        return count == 4
    
    @staticmethod
    def get_required_consents_for_donor(db: Session, bank_id: str) -> list:
        """Get all required consent templates for a bank"""
        from models import ConsentTemplate
        
        templates = db.query(ConsentTemplate).filter(
            ConsentTemplate.bank_id == bank_id,
            ConsentTemplate.is_active == True
        ).order_by(ConsentTemplate.order).all()
        
        if len(templates) != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank must have exactly 4 active consent templates"
            )
        
        return templates
    
    @staticmethod
    def all_consents_verified(db: Session, donor_id: str) -> bool:
        """Check if all 4 consents are verified"""
        from models import DonorConsent, ConsentStatus
        
        verified_count = db.query(DonorConsent).filter(
            DonorConsent.donor_id == donor_id,
            DonorConsent.status == ConsentStatus.VERIFIED
        ).count()
        
        return verified_count >= 4


class CounselingService:
    """Business logic for counseling operations"""
    
    @staticmethod
    def validate_counseling_method(bank: Bank, method: str) -> bool:
        """Check if counseling method is supported by bank"""
        if not bank.counseling_config:
            # If no config set, allow all methods
            return True
        
        allowed_methods = bank.counseling_config.get("methods", [])
        if not allowed_methods:
            return True
        
        if method not in allowed_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Counseling method '{method}' not supported by this bank"
            )
        
        return True
    
    @staticmethod
    def get_available_time_slots(bank: Bank) -> list:
        """Get available counseling time slots from bank config"""
        if not bank.counseling_config:
            return []
        
        return bank.counseling_config.get("time_slots", [])


class TestReportService:
    """Business logic for test report operations"""
    
    @staticmethod
    def can_donor_view_report(donor_id: str, report) -> bool:
        """Donors can always view their own reports regardless of source"""
        return report.donor_id == donor_id
    
    @staticmethod
    def can_bank_upload_report(bank: Bank, donor: Donor) -> bool:
        """Check if bank can upload reports for donor"""
        if donor.bank_id != bank.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Donor does not belong to this bank"
            )
        
        return True
    
    @staticmethod
    def get_all_reports_for_donor(db: Session, donor_id: str) -> list:
        """Get all test reports for a donor (both sources)"""
        from models import TestReport
        
        reports = db.query(TestReport).filter(
            TestReport.donor_id == donor_id
        ).order_by(TestReport.uploaded_at.desc()).all()
        
        return reports
