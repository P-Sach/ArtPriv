"""
Clear all data from the database
WARNING: This will delete all data!
"""
from database import SessionLocal
from models.models import (
    Bank, Donor, ConsentTemplate, DonorConsent, 
    CounselingSession, TestReport, DonorStateHistory, BankStateHistory
)

def clear_database():
    """Delete all data from database"""
    db = SessionLocal()
    
    try:
        print("\n⚠️  WARNING: This will delete ALL data from the database!")
        response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
        
        if response != "YES":
            print("❌ Operation cancelled.")
            return
        
        print("\n🗑️  Deleting data...")
        
        # Delete in correct order (respecting foreign keys)
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
        print(f"\n✅ Successfully deleted {total_deleted} records")
        print("🎯 Database is now empty and ready for seeding!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    clear_database()
