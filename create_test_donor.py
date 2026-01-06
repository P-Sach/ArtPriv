"""Create test donor account for testing"""
from database import SessionLocal
from models import Donor, Bank, DonorState
from utils.auth import hash_password
from datetime import datetime

db = SessionLocal()

try:
    # Get first bank
    bank = db.query(Bank).first()
    if not bank:
        print("❌ No bank found! Please create a bank first.")
        exit(1)
    
    print(f"✅ Found bank: {bank.email}")
    
    # Check if donor already exists
    existing = db.query(Donor).filter(Donor.email == 'donor@test.com').first()
    if existing:
        print(f"⚠️  Donor already exists: donor@test.com")
        print(f"   Name: {existing.first_name} {existing.last_name}")
        print(f"   State: {existing.state}")
    else:
        # Create donor
        donor = Donor(
            email='donor@test.com',
            hashed_password=hash_password('test123'),
            first_name='Test',
            last_name='Donor',
            phone='1234567890',
            bank_id=bank.id,
            state=DonorState.DONOR_ONBOARDED,
            selected_at=datetime.utcnow(),
            consent_pending=False,
            counseling_pending=False,
            tests_pending=False
        )
        db.add(donor)
        db.commit()
        print(f"✅ Created test donor: donor@test.com")
        print(f"   Password: test123")
        print(f"   Name: Test Donor")
        print(f"   State: {donor.state}")
    
    print("\n📋 Test Credentials:")
    print("   Bank:  test@test.com / Test123456")
    print("   Donor: donor@test.com / test123")
    
finally:
    db.close()
