# 🔧 Network Troubleshooting - IKODIO BugBounty

## ❌ Masalah: ERR_CONNECTION_TIMED_OUT

Aplikasi deployed di server **192.168.100.6** tapi tidak bisa diakses dari Mac/browser.

## ✅ Status Deployment

| Component | Status | Port | Accessible |
|-----------|--------|------|------------|
| Backend | ✅ Running | 8001 | ✅ From server itself |
| Frontend | ✅ Running | 3003 | ✅ From server itself |
| Firewall | ✅ Configured | 8001, 3003 | ✅ Rules added |
| SSH | ✅ Working | 7420 | ✅ From Mac |

## 🔍 Root Cause

**Network Isolation:** Mac Anda tidak berada di network yang sama dengan server (192.168.100.x/24).

**Test dari server berhasil:**
```bash
# Dari server sendiri:
curl http://192.168.100.6:8001/health
# ✅ {"status":"healthy","database":"connected","redis":"connected"}

curl http://192.168.100.6:3003
# ✅ HTTP/1.1 200 OK
```

**Test dari Mac timeout:**
```bash
# Dari Mac:
curl http://192.168.100.6:8001/health
# ❌ Connection timeout
```

## 💡 Solusi

### Option 1: Akses dari Komputer di Network yang Sama ⭐ RECOMMENDED

Gunakan komputer/device yang terhubung ke **network 192.168.100.x**:

```
http://192.168.100.6:3003  ← Frontend
http://192.168.100.6:8001  ← Backend
```

### Option 2: SSH Tunnel (Untuk Development)

Buat tunnel dari Mac ke server:

```bash
# Jalankan ini di terminal (biarkan running):
ssh -p 7420 -L 3003:localhost:3003 -L 8001:localhost:8001 ikodioxlapo@192.168.100.6
# Password: Mi252512@

# Lalu akses via localhost:
http://localhost:3003  ← Frontend via tunnel
http://localhost:8001  ← Backend via tunnel
```

### Option 3: VPN ke Network Server

Setup VPN untuk join network 192.168.100.x, lalu akses langsung ke IP server.

### Option 4: Public Domain dengan Reverse Proxy

Setup nginx reverse proxy dengan domain public:

```nginx
# /etc/nginx/sites-available/ikodio-bugbounty
server {
    listen 80;
    server_name bugbounty.ikodio.com;
    
    location / {
        proxy_pass http://localhost:3003;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
    }
}
```

Lalu akses via: `http://bugbounty.ikodio.com`

## 🧪 Verification Tests

### Test dari Server (Always Works) ✅

```bash
ssh -p 7420 ikodioxlapo@192.168.100.6

# Test backend
curl http://192.168.100.6:8001/health
curl http://localhost:8001/health

# Test frontend
curl http://192.168.100.6:3003
curl http://localhost:3003
```

### Test dari Mac (Network Dependent)

```bash
# Ping test
ping 192.168.100.6

# Port test
nc -zv 192.168.100.6 3003
nc -zv 192.168.100.6 8001

# HTTP test
curl http://192.168.100.6:8001/health
```

### Test SSH Tunnel

```bash
# Create tunnel
ssh -p 7420 -L 8001:localhost:8001 ikodioxlapo@192.168.100.6 -N &

# Test via tunnel
curl http://localhost:8001/health
```

## 📋 Network Information

**Server:**
- IP: 192.168.100.6
- Network: 192.168.100.0/24
- Interface: eno1
- Gateway: 192.168.100.1 (assumed)

**Services:**
- Backend: 0.0.0.0:8001 (listening on all interfaces)
- Frontend: :::3003 (listening on all interfaces IPv6)
- SSH: 0.0.0.0:7420

**Firewall (ufw):**
```
8001/tcp    ALLOW    Anywhere
3003/tcp    ALLOW    Anywhere
7420/tcp    ALLOW    Anywhere (already configured)
```

## 🎯 Quick Fix Script

Simpan sebagai `connect-via-tunnel.sh`:

```bash
#!/bin/bash
echo "🚇 Creating SSH Tunnel to Production Server..."
echo ""
echo "Akses setelah tunnel terbentuk:"
echo "  Frontend: http://localhost:3003"
echo "  Backend:  http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop"
echo ""

ssh -p 7420 \
  -L 3003:localhost:3003 \
  -L 8001:localhost:8001 \
  ikodioxlapo@192.168.100.6
```

Jalankan:
```bash
chmod +x connect-via-tunnel.sh
./connect-via-tunnel.sh
# Enter password: Mi252512@
```

## 📞 Next Steps

1. **Untuk Development/Testing:**
   - Gunakan SSH tunnel dari Mac
   - Atau akses dari komputer di network 192.168.100.x

2. **Untuk Production:**
   - Setup domain (e.g., bugbounty.ikodio.com)
   - Configure nginx reverse proxy
   - Enable SSL with Let's Encrypt
   - Setup monitoring

3. **Untuk Team Access:**
   - Setup VPN server di network 192.168.100.x
   - Atau expose via cloudflare tunnel
   - Atau gunakan ngrok untuk temporary access

---

**Status:** ✅ Server running, network access limited to local network
**Last Updated:** November 20, 2025
