# 🔐 IKODIO BugBounty - Login Information

## 🎯 Access URLs

**Frontend:** http://192.168.100.6:3003
**Backend API:** http://192.168.100.6:8001
**API Docs:** http://192.168.100.6:8001/api/docs

---

## 👤 Login Credentials

### Admin Account
```
Email: admin@ikodio.com
Password: admin123
Role: Administrator
```

### Demo Account
```
Email: demo@ikodio.com
Password: demo123
Role: User
```

---

## 🚀 How to Access Dashboard

1. **Open Frontend:**
   - Buka browser: http://192.168.100.6:3003
   
2. **Click "Login" or "Sign Up":**
   - Klik button Login di navbar
   - Atau klik Get Started untuk sign up

3. **Enter Credentials:**
   - Masukkan email dan password di atas
   - Click "Login"

4. **Redirect to Dashboard:**
   - Setelah login berhasil, otomatis redirect ke dashboard
   - Dashboard menampilkan stats, scans, bugs, earnings

---

## 📊 Dashboard Features

Setelah login, Anda akan melihat:

- **Overview Stats:** Total scans, bugs found, earnings
- **Recent Scans:** Latest security scans
- **Bug Reports:** Active and resolved bugs
- **Earnings:** Bounty rewards and pending payments
- **Analytics:** Performance charts and metrics

---

## 🔧 API Testing

Test API directly via curl:

```bash
# Get access token
curl -X POST "http://192.168.100.6:8001/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@ikodio.com&password=admin123"

# Use token to access protected endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.100.6:8001/api/dashboard/stats
```

---

## 📝 Notes

- **Authentication:** JWT-based authentication enabled
- **Session:** Token expires in 30 minutes
- **Backend:** Mock database (in-memory users)
- **Frontend:** Full Next.js application with auth flow
- **Security:** Demo setup - not for production use

---

**Status:** ✅ Authentication Enabled | ✅ Dashboard Ready
**Last Updated:** November 20, 2025

Untuk enable full authentication system dengan user login:

### 1. Setup Database

```bash
ssh -p 7420 ikodioxlapo@192.168.100.6

# Login sebagai postgres user
sudo -i -u postgres

# Create database dan user
psql << 'SQL'
CREATE USER ikodio WITH PASSWORD 'Mi252512@';
CREATE DATABASE ikodio_bugbounty OWNER ikodio;
GRANT ALL PRIVILEGES ON DATABASE ikodio_bugbounty TO ikodio;
SQL

exit
```

### 2. Run Database Migrations

```bash
cd ~/ikodio-bugbounty/backend
source venv/bin/activate
alembic upgrade head
```

### 3. Create Admin User

```bash
cd ~/ikodio-bugbounty/backend
source venv/bin/activate

python3 << 'PYSCRIPT'
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DATABASE_URL = "postgresql://ikodio:Mi252512@@localhost/ikodio_bugbounty"
engine = create_engine(DATABASE_URL)

hashed = pwd_context.hash("admin123")

with engine.connect() as conn:
    conn.execute(text("""
        INSERT INTO users (email, username, hashed_password, full_name, is_active, is_superuser, role)
        VALUES ('admin@ikodio.com', 'admin', :pwd, 'Admin IKODIO', true, true, 'admin')
    """), {"pwd": hashed})
    conn.commit()
    
print("✅ Admin created: admin@ikodio.com / admin123")
PYSCRIPT
```

### 4. Restart dengan Full Backend

```bash
# Kill simple backend
fuser -k 8001/tcp

# Start full backend (main.py)
cd ~/ikodio-bugbounty/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > backend.log 2>&1 &
```

---

## 📋 Login Credentials (After Full Setup)

```
Email:    admin@ikodio.com
Username: admin
Password: admin123
```

---

## 🚀 Quick Demo/Testing

Untuk sementara, karena menggunakan **start_simple.py**, Anda bisa:

1. **Test API Endpoints:**
   - http://192.168.100.6:8001/health
   - http://192.168.100.6:8001/api/docs

2. **Access Frontend:**
   - http://192.168.100.6:3003
   - Frontend akan tampil tapi fitur login belum berfungsi penuh

3. **Enable Full Features:**
   - Follow "Setup Full Database & Authentication" di atas
   - Restart dengan main.py backend
   - Semua fitur authentication akan aktif

---

## 📝 Notes

**Current Status:**
- ✅ Backend API running (minimal version)
- ✅ Frontend running
- ⏸️ Database not fully configured
- ⏸️ Authentication endpoints not active

**To Enable Full Features:**
1. Setup PostgreSQL database
2. Run migrations
3. Create admin user
4. Switch to full backend (main.py)

**Alternative - Quick Test:**
Jika hanya ingin test UI/UX tanpa backend integration:
- Frontend masih bisa diakses untuk lihat design
- API endpoints basic masih work (health check, info)
- Full authentication perlu database setup

---

**Status:** ✅ Deployed | ⏸️ Database setup pending
**Last Updated:** November 20, 2025
