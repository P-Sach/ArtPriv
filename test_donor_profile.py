"""Test donor profile endpoint"""
from database import SessionLocal
from models import Donor
from schemas import DonorDetailResponse

db = SessionLocal()

try:
    donor = db.query(Donor).filter(Donor.email == 'donor@test.com').first()
    
    if donor:
        print("✅ Found donor:", donor.email)
        print("   ID:", donor.id)
        print("   State:", donor.state)
        print("   Eligibility:", donor.eligibility_status)
        print("   Bank ID:", donor.bank_id)
        
        # Try to convert to schema
        try:
            response = DonorDetailResponse.from_orm(donor)
            print("\n✅ Schema conversion successful!")
            print("   Response dict keys:", list(response.dict().keys()))
        except Exception as e:
            print(f"\n❌ Schema conversion failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Donor not found")
        
finally:
    db.close()
