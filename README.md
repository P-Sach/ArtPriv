# ArtPriv Backend

A FastAPI-based backend system for connecting donors and banks with strict state-driven workflows.

## Features

- **Two User Types**: Donors and Banks with separate dashboards and permissions
- **State Machine Architecture**: Enforced state transitions for both donors and banks
- **Bank Authority**: Banks control critical decisions (consent verification, eligibility)
- **Audit Trail**: Complete state history tracking
- **File Management**: Document and test report uploads
- **JWT Authentication**: Secure token-based authentication
- **Supabase Integration**: PostgreSQL database with Row Level Security

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: ORM for database operations
- **Supabase**: PostgreSQL database hosting
- **JWT**: Authentication tokens
- **Pydantic**: Data validation
- **Bcrypt**: Password hashing

## Project Structure

```
ArtPriv/
├── api/
│   └── routes/
│       ├── auth.py          # Authentication endpoints
│       ├── bank.py          # Bank endpoints
│       ├── donor.py         # Donor endpoints
│       └── public.py        # Public endpoints
├── models/
│   └── models.py            # SQLAlchemy models
├── schemas/
│   └── schemas.py           # Pydantic schemas
├── services/
│   └── business_logic.py    # Business logic layer
├── utils/
│   ├── auth.py              # Auth utilities
│   ├── dependencies.py      # FastAPI dependencies
│   ├── file_upload.py       # File handling
│   └── state_machine.py     # State transitions
├── config.py                # Configuration
├── database.py              # Database setup
├── main.py                  # FastAPI application
├── schema.sql               # Supabase SQL schema
└── requirements.txt         # Dependencies
```

## Setup Instructions

### 1. Database Setup (Supabase)

1. Create a new Supabase project at https://supabase.com
2. Copy your project URL and keys
3. Run the SQL schema:
   - Go to SQL Editor in Supabase dashboard
   - Copy contents of `schema.sql`
   - Execute the SQL

### 2. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
   SECRET_KEY=generate-a-secure-random-string
   ```

3. Generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## State Machines

### Donor States

1. **Visitor** → Browses banks
2. **Bank Selected** → Selects a bank
3. **Lead Created** → Submits interest
4. **Account Created** → Creates login
5. **Counseling Requested** → Requests counseling
6. **Consent Pending** → Signs consent forms
7. **Consent Verified** → Bank verifies consents (Bank Action)
8. **Tests Pending** → Completes medical tests
9. **Eligibility Decision** → Bank reviews (Bank Action)
10. **Donor Onboarded** → Final state (approved donors)

### Bank States

1. **Account Created** → Initial registration
2. **Verification Pending** → Submitted documents
3. **Verified** → Admin approved (Admin Action)
4. **Subscription Pending** → Initiating subscription
5. **Subscribed & Onboarded** → Payment complete
6. **Operational** → Can manage donors

## Key API Endpoints

### Authentication
- `POST /api/auth/bank/register` - Register bank
- `POST /api/auth/bank/login` - Login bank
- `POST /api/auth/donor/login` - Login donor

### Public
- `GET /api/public/banks` - List verified banks
- `GET /api/public/banks/{id}` - Get bank details

### Donor
- `POST /api/donor/lead` - Create donor lead
- `POST /api/donor/account` - Create account
- `POST /api/donor/counseling/request` - Request counseling
- `POST /api/donor/consents/sign` - Sign consent
- `POST /api/donor/tests/upload` - Upload test report
- `GET /api/donor/me` - Get profile

### Bank
- `GET /api/bank/donors` - List bank's donors
- `POST /api/bank/consents/templates` - Create consent template
- `POST /api/bank/consents/verify` - Verify donor consent
- `POST /api/bank/counseling/schedule` - Schedule counseling
- `POST /api/bank/tests/upload` - Upload test report
- `POST /api/bank/eligibility/decide` - Make eligibility decision

## Business Rules

1. **Banks must be verified and subscribed** before interacting with donors
2. **Donors cannot self-advance** past bank-controlled checkpoints
3. **All state transitions are audited** with history tracking
4. **Test reports are visible to donors** regardless of source
5. **Banks have final authority** on eligibility decisions
6. **Exactly 4 consent forms** required from each bank
7. **Counseling configuration** is bank-specific

## Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Row-level security in Supabase
- File upload validation
- State transition validation

## File Uploads

All documents are stored as **PDF files only** in Supabase Storage buckets:
- `certification-documents` - Bank certification PDFs
- `test-reports` - Medical test report PDFs (both bank-conducted and donor-uploaded)
- `consent-forms` - Consent form signature PDFs (optional for digital signatures)
- `counseling-reports` - Counseling session reports/notes PDFs

### Storage Bucket Setup

After running `schema.sql`, create the storage buckets in Supabase Dashboard:

1. Go to **Storage** in Supabase Dashboard
2. Create four buckets:
   - `certification-documents` (private)
   - `test-reports` (private)
   - `consent-forms` (private)
   - `counseling-reports` (private)
3. Configure RLS policies as needed (see schema.sql comments)

**Note:** Only PDF files are accepted for all uploads. The API validates file type and extension.

## Development

### Run Tests
```bash
pytest
```

### Database Migrations
Using Alembic (optional):
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use production-grade WSGI server:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
3. Configure CORS origins appropriately
4. Use environment variables for secrets
5. Enable HTTPS
6. Set up proper file storage (Supabase Storage/S3)
7. Configure Row Level Security policies in Supabase

## License

Proprietary - All rights reserved
