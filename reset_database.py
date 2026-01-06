"""
Complete database reset and seed script
This will:
1. Clear all existing data
2. Populate with realistic dummy data
"""
import sys
from clear_data import clear_database
from seed_data import seed_database

def reset_and_seed():
    """Clear database and seed with dummy data"""
    print("\n" + "="*80)
    print("🔄 DATABASE RESET AND SEED")
    print("="*80)
    print("\nThis will:")
    print("  1. Delete all existing data")
    print("  2. Create 8 dummy banks across India")
    print("  3. Create 15 dummy donors")
    print("  4. Create consent templates")
    print("\n" + "="*80)
    
    print("\n" + "="*80)
    print("STEP 1: Clearing existing data...")
    print("="*80)
    
    # Import and run clear
    from database import SessionLocal
    from models.models import (
        Bank, Donor, ConsentTemplate, DonorConsent, 
        CounselingSession, TestReport, DonorStateHistory, BankStateHistory
    )
    
    db = SessionLocal()
    try:
        tables = [
            (BankStateHistory, "Bank State History"),
            (DonorStateHistory, "Donor State History"),
            (TestReport, "Test Reports"),
            (CounselingSession, "Counseling Sessions"),
            (DonorConsent, "Donor Consents"),
            (ConsentTemplate, "Consent Templates"),
            (Donor, "Donors"),
            (Bank, "Banks")
        ]
        
        total_deleted = 0
        for model, name in tables:
            count = db.query(model).count()
            if count > 0:
                db.query(model).delete()
                print(f"  ✓ Deleted {count} {name}")
                total_deleted += count
        
        db.commit()
        print(f"\n✅ Successfully deleted {total_deleted} records\n")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing database: {e}")
        return
    finally:
        db.close()
    
    print("="*80)
    print("STEP 2: Seeding with dummy data...")
    print("="*80 + "\n")
    
    # Run seed
    seed_database()


if __name__ == "__main__":
    reset_and_seed()
