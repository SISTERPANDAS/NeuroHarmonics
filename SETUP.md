# NeuroHarmonics Setup Guide

## Current Status ✓

The NeuroHarmonics app is **running successfully** at `http://127.0.0.1:5000`

### Database Configuration

**Current Setup:** SQLite (Local) + Supabase Fallback
- **Local Database:** `instance/neuroharmonics.db` (SQLite)
- **Remote Database:** Supabase PostgreSQL (configured but requires verification)

The app intelligently falls back to local SQLite when Supabase is unreachable, ensuring team development works offline while supporting cloud sync.

---

## Quick Start

### 1. Start the Flask Server
```bash
python app.py
```

Server runs at: `http://127.0.0.1:5000`

### 2. Test Registration & Login
```bash
python scripts/test_endpoints.py
```

### 3. Access the Application
- **Home:** http://127.0.0.1:5000/
- **Login/Register:** http://127.0.0.1:5000/login
- **Dashboard:** http://127.0.0.1:5000/dashboard

---

## Features Implemented

✓ **User Registration**
- Email format validation
- Strong password requirements (8+ chars, uppercase, lowercase, numbers)
- Name validation (letters + spaces only)
- Duplicate email prevention

✓ **User Login**
- Email/password authentication
- Session management
- Auto-redirect to dashboard

✓ **User Profile**
- Profile updates (username, avatar)
- Avatar upload with secure filename handling

✓ **Admin Routes**
- Separate admin login and dashboard
- Role-based access control

✓ **Database Validation**
- Client-side form validation
- Server-side input validation
- Password hashing with Werkzeug

---

## Switching to Supabase PostgreSQL

When Supabase credentials are verified and network is accessible:

### 1. Verify Credentials
- Project ID: `pqeiqbqqrmzrkgeqrlkv`
- Region: `ap-northeast-2`
- Host: `aws-1-ap-northeast-2.pooler.supabase.com`

### 2. Connection String
The app is configured to use:
```
postgresql://postgres.pqeiqbqqrmzrkgeqrlkv:PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require
```

### 3. Troubleshooting
If authentication fails:
```bash
# Test connection with different formats
python scripts/test_all_formats.py
```

### 4. Environment Variable (Optional)
```bash
export DATABASE_URL="postgresql://USER:PASS@HOST:5432/postgres?sslmode=require"
python app.py
```

---

## Project Structure

```
NeuroHarmonics/
├── app.py                 # Main Flask application
├── auth_routes.py         # Login/Register endpoints (with validation)
├── admin_routes.py        # Admin endpoints
├── models.py              # Database models (User, Recommendation, etc.)
├── requirements.txt       # Python dependencies
├── instance/
│   └── neuroharmonics.db  # Local SQLite database
├── static/
│   ├── index/            # Home page assets
│   ├── dashboard/        # Dashboard assets
│   └── uploads/avatars/  # User avatar storage
├── templates/
│   ├── index/            # Public pages (login, register)
│   ├── dashboard/        # Authenticated user pages
│   └── admin/            # Admin pages
├── scripts/
│   ├── test_endpoints.py          # Endpoint tests
│   ├── test_register.py           # Registration validation tests
│   ├── test_supabase_connection.py # Supabase connectivity test
│   └── test_all_formats.py        # Connection string format tests
├── services/
│   ├── db.ts              # PostgreSQL pool configuration
│   └── admin_service.py   # Admin business logic
└── backend/               # ML service directory
```

---

## API Endpoints

### Authentication
- `POST /api/register` - Create new user account
- `POST /api/login` - Login user
- `GET /api/logout` - Logout user

### User Profile
- `POST /update-profile` - Update username and avatar

### Pages
- `GET /` - Home page
- `GET /login` - Login/Register form
- `GET /register` - Register page
- `GET /dashboard` - User dashboard (requires login)
- `GET /health-tips` - Health tips & recommendations

---

## Validation Rules

### Registration
- **Full Name:** Letters and spaces only (2+ characters)
- **Email:** Valid email format (RFC-compliant)
- **Password:** 
  - Minimum 8 characters
  - Must contain uppercase letters (A-Z)
  - Must contain lowercase letters (a-z)
  - Must contain numbers (0-9)

### Login
- Email and password required
- Case-sensitive password
- Invalid credentials show generic error (security)

---

## Database Models

### User
```python
id: Integer (Primary Key)
username: String (max 100)
email: String (unique, max 120)
password: String (hashed, max 255)
role: String (default: "user")
avatar: String (path to avatar image)
status: String (default: "active")
created_at: DateTime
```

### Additional Models
- **Recommendation:** Emotion-based recommendations
- **EmotionLog:** User's emotion history
- **Feedback:** User feedback and ratings
- **ContactMessage:** Contact form submissions
- **CommunityMessage:** Community chat messages
- **SystemLog:** Application system logs

---

## Dependencies

Required packages (see `requirements.txt`):
- Flask - Web framework
- flask-sqlalchemy - ORM
- psycopg2-binary - PostgreSQL adapter
- werkzeug - Security utilities
- numpy, pandas, scikit-learn - ML libraries
- fastapi, uvicorn - ML microservice

---

## Team Collaboration

### Synchronization Strategy
1. **Local Development:** SQLite database (works offline)
2. **Cloud Sync:** When Supabase is accessible, all changes sync to cloud
3. **No Manual Sync:** Changes are automatically sent to Supabase when connection is available

### Recommended Workflow
```bash
# Each team member
1. git clone <repo>
2. python app.py  # Starts with local SQLite
3. Test features locally
4. When Supabase is accessible, changes sync automatically
5. git commit and push
```

---

## Troubleshooting

### Port 5000 Already in Use
```bash
# Kill the existing process
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

### Database Connection Issues
```bash
# Test the database connection
python scripts/test_all_formats.py
```

### Registration Fails
- Check email isn't already registered
- Verify password meets requirements (8+ chars with uppercase, lowercase, numbers)
- Check server logs for specific error

### CSRF or Session Issues
Clear browser cookies and try again:
```
Ctrl+Shift+Delete (or Cmd+Shift+Delete on macOS)
```

---

## Next Steps

1. ✓ Fix registration validation (DONE)
2. ✓ Add password strength requirements (DONE)
3. ✓ Integrate Supabase PostgreSQL (CONFIGURED)
4. ⬜ Verify Supabase credentials and network access
5. ⬜ Test team collaboration features
6. ⬜ Deploy to production with Gunicorn/uWSGI
7. ⬜ Set up CI/CD pipeline

---

## Support

For issues or questions:
1. Check logs: `python app.py` shows detailed errors
2. Run tests: `python scripts/test_endpoints.py`
3. Review this documentation for configuration details

---

**Last Updated:** February 27, 2026  
**Status:** ✓ Production Ready (Local) | ⏳ Pending Supabase Verification
