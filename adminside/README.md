# ArtPriv Admin Portal

A **standalone** admin portal for managing the ArtPriv IVF Donor-Bank Management System. This module is completely self-contained and can be integrated with any version of the main ArtPriv application.

## 📁 Structure

```
adminside/
├── backend/                 # FastAPI Admin API
│   ├── .env                # Environment configuration
│   ├── .env.example        # Configuration template
│   ├── main.py             # App entry point
│   ├── routes.py           # API endpoints
│   ├── models.py           # SQLAlchemy models (standalone)
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # Authentication utilities
│   ├── config.py           # Settings management
│   ├── database.py         # Database connection
│   ├── seed_admins.py      # Admin user creation
│   └── requirements.txt    # Python dependencies
│
├── src/                    # Next.js Frontend
│   ├── app/
│   │   ├── login/          # Admin login
│   │   ├── dashboard/      # Main dashboard
│   │   ├── banks/          # Bank management
│   │   │   └── [id]/       # Bank detail page
│   │   ├── donors/         # Donor management
│   │   │   └── [id]/       # Donor detail page
│   │   └── subscriptions/  # Subscription analytics
│   └── lib/
│       └── api.ts          # API client
│
├── .env.local              # Frontend environment
├── .env.example            # Frontend config template
└── package.json            # Node.js dependencies
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# Create admin users
python seed_admins.py

# Start server
uvicorn main:app --reload --port 8001
```

### 2. Frontend Setup

```bash
cd adminside  # (root of admin portal)

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL

# Start development server
npm run dev -- -p 3001
```

### 3. Access Admin Portal

Open http://localhost:3001 and login with:
- **Email:** admin@artpriv.com
- **Password:** admin123

## 🔧 Configuration

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT secret (must match main app) | ✅ |
| `ALGORITHM` | JWT algorithm (default: HS256) | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 60) | ❌ |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | ❌ |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Admin backend URL | ✅ |

## 🔌 Integration Guide

### Connecting to a Different Database

1. Update `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

2. Ensure the database has these tables:
   - `banks` - Bank entities
   - `donors` - Donor entities
   - `donor_state_history` - Donor state changes
   - `admins` - Admin users (created by seed script)
   - `activity_logs` - Admin activity audit trail

3. Run `python seed_admins.py` to create admin users

### Matching JWT with Main Application

The `SECRET_KEY` in `backend/.env` **must match** the main application's JWT secret for token compatibility. This allows:
- Shared authentication (optional)
- Consistent token validation

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/login` | POST | Admin authentication |
| `/api/admin/dashboard` | GET | Dashboard statistics |
| `/api/admin/banks` | GET | List banks (paginated) |
| `/api/admin/banks/{id}` | GET | Bank details |
| `/api/admin/banks/{id}/verify` | PUT | Verify bank |
| `/api/admin/banks/{id}/subscription` | PUT | Update subscription |
| `/api/admin/donors` | GET | List donors (paginated) |
| `/api/admin/donors/{id}` | GET | Donor details + history |
| `/api/admin/activity-logs` | GET | Audit trail |
| `/api/admin/subscriptions/analytics` | GET | Revenue analytics |

## 🎨 Features

- **Dashboard** - Real-time stats, subscription breakdown, activity feed
- **Bank Management** - List, filter, verify, manage subscriptions
- **Donor Management** - View all donors with state history
- **Subscription Analytics** - Revenue tracking, tier distribution
- **Activity Logging** - Full admin action audit trail
- **Dark Theme** - Modern glassmorphism UI

## 🔒 Security

- JWT-based authentication
- Role-based access control (super_admin, support, viewer)
- Activity logging for all admin actions
- CORS protection

## 📦 Dependencies

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose (JWT)
- bcrypt
- psycopg2-binary (PostgreSQL)

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS

---

**This admin portal is completely standalone** - it only requires a PostgreSQL database with the expected table structure. No files from other directories are imported or required.
