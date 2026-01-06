"""
Seed script to populate the database with dummy banks and donors
Run this file to add test data to the database
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.models import Base, Bank, Donor, BankState, DonorState, ConsentTemplate
from utils.auth import hash_password


# Indian cities for bank locations
CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "address": "Andheri West, Mumbai, Maharashtra 400053"},
    {"city": "Delhi", "state": "Delhi", "address": "Connaught Place, New Delhi, Delhi 110001"},
    {"city": "Bangalore", "state": "Karnataka", "address": "Indiranagar, Bangalore, Karnataka 560038"},
    {"city": "Hyderabad", "state": "Telangana", "address": "Banjara Hills, Hyderabad, Telangana 500034"},
    {"city": "Chennai", "state": "Tamil Nadu", "address": "T Nagar, Chennai, Tamil Nadu 600017"},
    {"city": "Pune", "state": "Maharashtra", "address": "Koregaon Park, Pune, Maharashtra 411001"},
    {"city": "Ahmedabad", "state": "Gujarat", "address": "Navrangpura, Ahmedabad, Gujarat 380009"},
    {"city": "Kolkata", "state": "West Bengal", "address": "Park Street, Kolkata, West Bengal 700016"},
    {"city": "Jaipur", "state": "Rajasthan", "address": "C-Scheme, Jaipur, Rajasthan 302001"},
    {"city": "Lucknow", "state": "Uttar Pradesh", "address": "Gomti Nagar, Lucknow, Uttar Pradesh 226010"}
]

# Dummy bank data
BANKS = [
    {
        "name": "LifeSpring Fertility Bank",
        "email": "contact@lifespring.in",
        "phone": "+91-22-4567-8901",
        "website": "https://lifespring.in",
        "description": "Leading fertility bank in Mumbai with over 15 years of experience in assisted reproductive technology. Specializing in comprehensive donor screening and management.",
        "location": CITIES[0],  # Mumbai
        "state": BankState.OPERATIONAL,
        "is_verified": True,
        "is_subscribed": True,
        "subscription_tier": "Professional"
    },
    {
        "name": "Nova Reproductive Health Center",
        "email": "info@nova-fertility.com",
        "phone": "+91-11-2345-6789",
        "website": "https://nova-fertility.com",
        "description": "State-of-the-art fertility bank in Delhi offering world-class donor management services. ICMR certified with advanced cryopreservation facilities.",
        "location": CITIES[1],  # Delhi
        "state": BankState.OPERATIONAL,
        "is_verified": True,
        "is_subscribed": True,
        "subscription_tier": "Enterprise"
    },
    {
        "name": "Genesis Fertility Solutions",
        "email": "hello@genesis-fertility.in",
        "phone": "+91-80-9876-5432",
        "website": "https://genesis-fertility.in",
        "description": "Premier fertility bank in Bangalore with cutting-edge technology and compassionate care. Trusted by over 200 clinics nationwide.",
        "location": CITIES[2],  # Bangalore
        "state": BankState.OPERATIONAL,
        "is_verified": True,
        "is_subscribed": True,
        "subscription_tier": "Professional"
    },
    {
        "name": "Bloom Fertility Bank",
        "email": "support@bloomfertility.com",
        "phone": "+91-40-1234-5678",
        "website": "https://bloomfertility.com",
        "description": "Comprehensive fertility bank in Hyderabad providing personalized donor coordination services. Known for excellent success rates and ethical practices.",
        "location": CITIES[3],  # Hyderabad
        "state": BankState.OPERATIONAL,
        "is_verified": True,
        "is_subscribed": True,
        "subscription_tier": "Starter"
    },
    {
        "name": "Radiance Reproductive Bank",
        "email": "info@radiancebank.in",
        "phone": "+91-44-8765-4321",
        "website": "https://radiancebank.in",
        "description": "Trusted fertility bank in Chennai with a decade of excellence in donor management and reproductive health services.",
        "location": CITIES[4],  # Chennai
        "state": BankState.OPERATIONAL,
        "is_verified": True,
        "is_subscribed": True,
        "subscription_tier": "Professional"
    },
    {
        "name": "Hope Fertility Center",
        "email": "contact@hopefertility.in",
        "phone": "+91-20-5555-1234",
        "website": "https://hopefertility.in",
        "description": "Modern fertility bank in Pune offering comprehensive donor screening and personalized support throughout the donation process.",
        "location": CITIES[5],  # Pune
        "state": BankState.VERIFIED,
        "is_verified": True,
        "is_subscribed": False,
        "subscription_tier": None
    },
    {
        "name": "Serenity Reproductive Solutions",
        "email": "info@serenity-fertility.com",
        "phone": "+91-79-7777-8888",
        "website": "https://serenity-fertility.com",
        "description": "Leading fertility bank in Ahmedabad committed to helping families through advanced reproductive technologies and ethical donor programs.",
        "location": CITIES[6],  # Ahmedabad
        "state": BankState.OPERATIONAL,
        "is_verified": True,
        "is_subscribed": True,
        "subscription_tier": "Starter"
    },
    {
        "name": "Zenith Fertility Bank",
        "email": "hello@zenithfertility.in",
        "phone": "+91-33-9999-0000",
        "website": "https://zenithfertility.in",
        "description": "Established fertility bank in Kolkata providing comprehensive donor management with a focus on transparency and compliance.",
        "location": CITIES[7],  # Kolkata
        "state": BankState.VERIFICATION_PENDING,
        "is_verified": False,
        "is_subscribed": False,
        "subscription_tier": None
    }
]

# Dummy donor data
DONORS = [
    {
        "first_name": "Priya",
        "last_name": "Sharma",
        "email": "priya.sharma@example.com",
        "phone": "+91-98765-43210",
        "date_of_birth": datetime(1995, 3, 15),
        "address": "Malad West, Mumbai, Maharashtra 400064",
        "state": DonorState.DONOR_ONBOARDED,
        "bank_index": 0  # LifeSpring
    },
    {
        "first_name": "Anjali",
        "last_name": "Reddy",
        "email": "anjali.reddy@example.com",
        "phone": "+91-98765-43211",
        "date_of_birth": datetime(1997, 7, 22),
        "address": "Bandra East, Mumbai, Maharashtra 400051",
        "state": DonorState.CONSENT_VERIFIED,
        "bank_index": 0  # LifeSpring
    },
    {
        "first_name": "Kavya",
        "last_name": "Patel",
        "email": "kavya.patel@example.com",
        "phone": "+91-98765-43212",
        "date_of_birth": datetime(1996, 11, 8),
        "address": "Dwarka, New Delhi, Delhi 110075",
        "state": DonorState.DONOR_ONBOARDED,
        "bank_index": 1  # Nova
    },
    {
        "first_name": "Sneha",
        "last_name": "Kumar",
        "email": "sneha.kumar@example.com",
        "phone": "+91-98765-43213",
        "date_of_birth": datetime(1994, 5, 30),
        "address": "Rohini, New Delhi, Delhi 110085",
        "state": DonorState.TESTS_PENDING,
        "bank_index": 1  # Nova
    },
    {
        "first_name": "Divya",
        "last_name": "Nair",
        "email": "divya.nair@example.com",
        "phone": "+91-98765-43214",
        "date_of_birth": datetime(1998, 1, 19),
        "address": "Koramangala, Bangalore, Karnataka 560034",
        "state": DonorState.DONOR_ONBOARDED,
        "bank_index": 2  # Genesis
    },
    {
        "first_name": "Meera",
        "last_name": "Singh",
        "email": "meera.singh@example.com",
        "phone": "+91-98765-43215",
        "date_of_birth": datetime(1995, 9, 12),
        "address": "Whitefield, Bangalore, Karnataka 560066",
        "state": DonorState.COUNSELING_REQUESTED,
        "bank_index": 2  # Genesis
    },
    {
        "first_name": "Riya",
        "last_name": "Agarwal",
        "email": "riya.agarwal@example.com",
        "phone": "+91-98765-43216",
        "date_of_birth": datetime(1996, 4, 25),
        "address": "Jubilee Hills, Hyderabad, Telangana 500033",
        "state": DonorState.DONOR_ONBOARDED,
        "bank_index": 3  # Bloom
    },
    {
        "first_name": "Aditi",
        "last_name": "Verma",
        "email": "aditi.verma@example.com",
        "phone": "+91-98765-43217",
        "date_of_birth": datetime(1997, 12, 3),
        "address": "Madhapur, Hyderabad, Telangana 500081",
        "state": DonorState.CONSENT_PENDING,
        "bank_index": 3  # Bloom
    },
    {
        "first_name": "Lakshmi",
        "last_name": "Iyer",
        "email": "lakshmi.iyer@example.com",
        "phone": "+91-98765-43218",
        "date_of_birth": datetime(1995, 6, 14),
        "address": "Anna Nagar, Chennai, Tamil Nadu 600040",
        "state": DonorState.DONOR_ONBOARDED,
        "bank_index": 4  # Radiance
    },
    {
        "first_name": "Pooja",
        "last_name": "Desai",
        "email": "pooja.desai@example.com",
        "phone": "+91-98765-43219",
        "date_of_birth": datetime(1998, 8, 27),
        "address": "Adyar, Chennai, Tamil Nadu 600020",
        "state": DonorState.ELIGIBILITY_DECISION,
        "bank_index": 4  # Radiance
    },
    {
        "first_name": "Neha",
        "last_name": "Joshi",
        "email": "neha.joshi@example.com",
        "phone": "+91-98765-43220",
        "date_of_birth": datetime(1996, 2, 10),
        "address": "Viman Nagar, Pune, Maharashtra 411014",
        "state": DonorState.ACCOUNT_CREATED,
        "bank_index": 5  # Hope
    },
    {
        "first_name": "Simran",
        "last_name": "Kapoor",
        "email": "simran.kapoor@example.com",
        "phone": "+91-98765-43221",
        "date_of_birth": datetime(1997, 10, 5),
        "address": "Kothrud, Pune, Maharashtra 411038",
        "state": DonorState.LEAD_CREATED,
        "bank_index": 5  # Hope
    },
    {
        "first_name": "Isha",
        "last_name": "Mehta",
        "email": "isha.mehta@example.com",
        "phone": "+91-98765-43222",
        "date_of_birth": datetime(1995, 11, 18),
        "address": "Satellite, Ahmedabad, Gujarat 380015",
        "state": DonorState.DONOR_ONBOARDED,
        "bank_index": 6  # Serenity
    },
    {
        "first_name": "Tanvi",
        "last_name": "Shah",
        "email": "tanvi.shah@example.com",
        "phone": "+91-98765-43223",
        "date_of_birth": datetime(1998, 3, 29),
        "address": "Vastrapur, Ahmedabad, Gujarat 380015",
        "state": DonorState.BANK_SELECTED,
        "bank_index": 6  # Serenity
    },
    {
        "first_name": "Aisha",
        "last_name": "Khan",
        "email": "aisha.khan@example.com",
        "phone": "+91-98765-43224",
        "date_of_birth": datetime(1996, 7, 7),
        "address": "Salt Lake, Kolkata, West Bengal 700064",
        "state": DonorState.VISITOR,
        "bank_index": None  # No bank selected yet
    }
]


def seed_database():
    """Populate database with dummy banks and donors"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Check if data already exists
        existing_banks = db.query(Bank).count()
        if existing_banks > 0:
            print(f"⚠️  Database already has {existing_banks} banks. Adding more data...")
        
        # Create banks
        bank_objects = []
        print("\n📦 Creating banks...")
        for bank_data in BANKS:
            location = bank_data.pop("location")
            bank = Bank(
                email=bank_data["email"],
                hashed_password=hash_password("password123"),  # Default password
                name=bank_data["name"],
                phone=bank_data["phone"],
                website=bank_data["website"],
                description=bank_data["description"],
                address=f"{location['address']}\nCity: {location['city']}, State: {location['state']}",
                state=bank_data["state"],
                is_verified=bank_data["is_verified"],
                is_subscribed=bank_data["is_subscribed"],
                subscription_tier=bank_data["subscription_tier"]
            )
            
            # Set subscription dates if subscribed
            if bank.is_subscribed:
                bank.subscription_started_at = datetime.now() - timedelta(days=30)
                bank.subscription_expires_at = datetime.now() + timedelta(days=335)
            
            # Set verification date if verified
            if bank.is_verified:
                bank.verified_at = datetime.now() - timedelta(days=60)
            
            # Add counseling config
            bank.counseling_config = {
                "methods": ["video", "call", "in_person"],
                "time_slots": ["9:00 AM - 11:00 AM", "2:00 PM - 4:00 PM"],
                "auto_approve": False
            }
            
            db.add(bank)
            db.flush()  # Flush immediately to get ID
            db.refresh(bank)  # Refresh to get the generated ID
            bank_objects.append(bank)
            print(f"  ✓ Created bank: {bank.name} ({location['city']})")
        
        db.commit()
        print(f"✅ Successfully created {len(bank_objects)} banks")
        
        # Create donors
        print("\n👥 Creating donors...")
        donor_count = 0
        for donor_data in DONORS:
            bank_index = donor_data.pop("bank_index", None)
            
            donor = Donor(
                first_name=donor_data["first_name"],
                last_name=donor_data["last_name"],
                email=donor_data["email"],
                hashed_password=hash_password("password123"),  # Default password
                phone=donor_data["phone"],
                date_of_birth=donor_data["date_of_birth"],
                address=donor_data["address"],
                state=donor_data["state"]
            )
            
            # Associate with bank if bank_index is provided
            if bank_index is not None and bank_index < len(bank_objects):
                donor.bank_id = bank_objects[bank_index].id
                donor.selected_at = datetime.now() - timedelta(days=random_days())
            
            # Add medical interest info for leads and onwards
            if donor.state != DonorState.VISITOR:
                donor.medical_interest_info = {
                    "type": "egg" if donor_count % 2 == 0 else "sperm",
                    "motivation": "Want to help families in need",
                    "health_conditions": "None"
                }
            
            db.add(donor)
            db.flush()  # Flush immediately
            donor_count += 1
            bank_name = bank_objects[bank_index].name if bank_index is not None else "No bank"
            print(f"  ✓ Created donor: {donor.first_name} {donor.last_name} - {donor.state.value} ({bank_name})")
        
        db.commit()
        print(f"✅ Successfully created {donor_count} donors")
        
        # Create consent templates for operational banks
        print("\n📄 Creating consent templates...")
        template_count = 0
        for bank in bank_objects:
            if bank.state == BankState.OPERATIONAL:
                templates = [
                    {
                        "title": "General Consent Form",
                        "content": f"I, the undersigned, hereby consent to participate in the donor program at {bank.name}. I understand the process and my rights.",
                        "order": 1
                    },
                    {
                        "title": "Medical Information Release",
                        "content": "I authorize the release of my medical information to authorized personnel for the purpose of donor screening and management.",
                        "order": 2
                    },
                    {
                        "title": "Privacy Policy Agreement",
                        "content": "I have read and agree to the privacy policy. I understand how my personal data will be collected, stored, and used.",
                        "order": 3
                    },
                    {
                        "title": "Legal Rights Acknowledgment",
                        "content": "I acknowledge that I have been informed of my legal rights and responsibilities as a donor under ICMR ART guidelines.",
                        "order": 4
                    }
                ]
                
                for template_data in templates:
                    template = ConsentTemplate(
                        bank_id=bank.id,
                        title=template_data["title"],
                        content=template_data["content"],
                        order=template_data["order"],
                        version="1.0",
                        is_active=True
                    )
                    db.add(template)
                    template_count += 1
                
        db.commit()
        print(f"✅ Successfully created {template_count} consent templates")
        
        print("\n" + "="*60)
        print("🎉 Database seeding completed successfully!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • {len(bank_objects)} banks created")
        print(f"   • {donor_count} donors created")
        print(f"   • {template_count} consent templates created")
        print(f"\n🔑 Default credentials:")
        print(f"   • Bank logins: Use any bank email (e.g., contact@lifespring.in)")
        print(f"   • Donor logins: Use any donor email (e.g., priya.sharma@example.com)")
        print(f"   • Password for all: password123")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def random_days():
    """Return random number of days between 1-90"""
    import random
    return random.randint(1, 90)


if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Seed the database
    seed_database()
