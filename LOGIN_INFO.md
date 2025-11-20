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
