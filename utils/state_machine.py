from models.models import DonorState, BankState, DonorStateHistory, BankStateHistory
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime


# Donor state machine transitions
DONOR_STATE_TRANSITIONS = {
    DonorState.VISITOR: [DonorState.BANK_SELECTED],
    DonorState.BANK_SELECTED: [DonorState.LEAD_CREATED],
    DonorState.LEAD_CREATED: [DonorState.ACCOUNT_CREATED],
    DonorState.ACCOUNT_CREATED: [DonorState.COUNSELING_REQUESTED],
    DonorState.COUNSELING_REQUESTED: [DonorState.CONSENT_PENDING],
    DonorState.CONSENT_PENDING: [DonorState.CONSENT_VERIFIED],
    DonorState.CONSENT_VERIFIED: [DonorState.TESTS_PENDING],
    DonorState.TESTS_PENDING: [DonorState.ELIGIBILITY_DECISION],
    DonorState.ELIGIBILITY_DECISION: [DonorState.DONOR_ONBOARDED],
    DonorState.DONOR_ONBOARDED: [],  # Final state
}


# Bank state machine transitions
BANK_STATE_TRANSITIONS = {
    BankState.ACCOUNT_CREATED: [BankState.VERIFICATION_PENDING],
    BankState.VERIFICATION_PENDING: [BankState.VERIFIED],
    BankState.VERIFIED: [BankState.SUBSCRIPTION_PENDING],
    BankState.SUBSCRIPTION_PENDING: [BankState.SUBSCRIBED_ONBOARDED],
    BankState.SUBSCRIBED_ONBOARDED: [BankState.OPERATIONAL],
    BankState.OPERATIONAL: [],  # Final state
}


def can_transition_donor_state(current_state: DonorState, new_state: DonorState) -> bool:
    """Check if donor state transition is valid"""
    allowed_transitions = DONOR_STATE_TRANSITIONS.get(current_state, [])
    return new_state in allowed_transitions


def can_transition_bank_state(current_state: BankState, new_state: BankState) -> bool:
    """Check if bank state transition is valid"""
    allowed_transitions = BANK_STATE_TRANSITIONS.get(current_state, [])
    return new_state in allowed_transitions


def transition_donor_state(
    db: Session,
    donor,
    new_state: DonorState,
    changed_by: str,
    changed_by_role: str,
    reason: Optional[str] = None
):
    """Transition donor to a new state with history tracking"""
    if not can_transition_donor_state(donor.state, new_state):
        raise ValueError(f"Invalid state transition from {donor.state} to {new_state}")
    
    old_state = donor.state
    donor.state = new_state
    
    # Create history record
    history = DonorStateHistory(
        donor_id=donor.id,
        from_state=old_state,
        to_state=new_state,
        changed_by=changed_by,
        changed_by_role=changed_by_role,
        reason=reason
    )
    db.add(history)
    db.commit()
    db.refresh(donor)


def transition_bank_state(
    db: Session,
    bank,
    new_state: BankState,
    changed_by: str,
    reason: Optional[str] = None
):
    """Transition bank to a new state with history tracking"""
    if not can_transition_bank_state(bank.state, new_state):
        raise ValueError(f"Invalid state transition from {bank.state} to {new_state}")
    
    old_state = bank.state
    bank.state = new_state
    
    # Create history record
    history = BankStateHistory(
        bank_id=bank.id,
        from_state=old_state,
        to_state=new_state,
        changed_by=changed_by,
        reason=reason
    )
    db.add(history)
    db.commit()
    db.refresh(bank)
