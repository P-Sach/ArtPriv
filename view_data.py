"""
View existing data in the database
"""
from sqlalchemy.orm import Session
from database import SessionLocal
from models.models import Bank, Donor, BankState, DonorState

def view_data():
    """Display existing banks and donors"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("📊 EXISTING DATABASE DATA")
        print("="*80)
        
        # Get all banks
        banks = db.query(Bank).all()
        print(f"\n🏦 BANKS ({len(banks)} total):")
        print("-" * 80)
        
        for i, bank in enumerate(banks, 1):
            print(f"\n{i}. {bank.name}")
            print(f"   Email: {bank.email}")
            print(f"   Phone: {bank.phone}")
            print(f"   Address: {bank.address[:100] if bank.address else 'N/A'}...")
            print(f"   State: {bank.state.value}")
            print(f"   Verified: {'Yes' if bank.is_verified else 'No'}")
            print(f"   Subscribed: {'Yes' if bank.is_subscribed else 'No'} ({bank.subscription_tier or 'N/A'})")
            
            # Count donors for this bank
            donor_count = db.query(Donor).filter(Donor.bank_id == bank.id).count()
            print(f"   Donors: {donor_count}")
        
        # Get all donors
        donors = db.query(Donor).all()
        print(f"\n\n👥 DONORS ({len(donors)} total):")
        print("-" * 80)
        
        for i, donor in enumerate(donors, 1):
            bank_name = "No bank selected"
            if donor.bank_id:
                bank = db.query(Bank).filter(Bank.id == donor.bank_id).first()
                if bank:
                    bank_name = bank.name
            
            print(f"\n{i}. {donor.first_name} {donor.last_name}")
            print(f"   Email: {donor.email}")
            print(f"   Phone: {donor.phone}")
            print(f"   Address: {donor.address[:60] if donor.address else 'N/A'}...")
            print(f"   State: {donor.state.value}")
            print(f"   Bank: {bank_name}")
        
        print("\n" + "="*80)
        print("🔑 DEFAULT LOGIN CREDENTIALS:")
        print("="*80)
        print("Password for all accounts: password123")
        print("\nBank Login Examples:")
        if banks:
            for bank in banks[:3]:
                print(f"  • {bank.email}")
        print("\nDonor Login Examples:")
        if donors:
            for donor in donors[:3]:
                if donor.email:
                    print(f"  • {donor.email}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Error viewing data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    view_data()
