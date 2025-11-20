# IKODIO BUGBOUNTY - Testing & Deployment Guide

## Status Perbaikan

### Completed
1. Fixed audit_log.py - Added Boolean and ForeignKey imports
2. Fixed layout.tsx - Removed PWAInstaller, fixed metadata warnings
3. Fixed logo di dashboard - Text only "Ikodio"
4. Created .env file dengan semua variabel yang dibutuhkan
5. Created comprehensive setup scripts
6. Removed obsolete version dari docker-compose.yml

### Scripts Created
1. **check-system.sh** - Comprehensive system check
2. **quick-setup.sh** - Automated setup untuk dependencies
3. **test-system.sh** - Integration testing script

## Quick Start (Untuk Testing)

### 1. Setup Environment

```bash
# Run automated setup
./scripts/quick-setup.sh
```

Setup ini akan:
- Create Python virtual environment di backend/venv
- Install semua Python dependencies
- Install frontend dependencies
- Start Docker services (postgres, redis, rabbitmq, elasticsearch)
- Verify installation

### 2. Start Backend

```bash
cd backend
source venv/bin/activate
python3 main.py
```

Backend akan running di: http://localhost:8000

### 3. Start Frontend

```bash
# Terminal baru
cd frontend
npm run dev
```

Frontend akan running di: http://localhost:3000

### 4. Run Tests

```bash
# System check
./scripts/check-system.sh

# Comprehensive integration test
./scripts/test-system.sh
```

## Manual Setup (Jika Script Gagal)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
python3 main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Docker Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis rabbitmq elasticsearch

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

## Testing Checklist

### Backend Tests
- [ ] Database connection works
- [ ] Redis connection works
- [ ] API health endpoint responds
- [ ] All route files can be imported
- [ ] Database models can be imported
- [ ] Authentication endpoints work
- [ ] CRUD operations work

### Frontend Tests
- [ ] Homepage loads without errors
- [ ] Dashboard loads and displays correctly
- [ ] Login/Register pages work
- [ ] API calls connect to backend
- [ ] Navigation works
- [ ] Forms submit correctly

### Integration Tests
- [ ] Frontend can authenticate with backend
- [ ] Scans can be created
- [ ] Bugs can be submitted
- [ ] Marketplace listings load
- [ ] WebSocket connections work
- [ ] Real-time updates function

## Common Issues & Solutions

### 1. Python Import Errors

**Issue:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Docker Services Not Starting

**Issue:** Services fail to start atau stuck

**Solution:**
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Start fresh
docker-compose up -d

# Check logs
docker-compose logs
```

### 3. Frontend Compilation Errors

**Issue:** Next.js errors atau warnings

**Solution:**
```bash
cd frontend

# Clear cache
rm -rf .next
rm -rf node_modules

# Reinstall
npm install

# Rebuild
npm run dev
```

### 4. Database Connection Errors

**Issue:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check if postgres is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify .env settings
grep DB_ .env

# Test connection
docker-compose exec postgres psql -U ikodio -d ikodio_bugbounty
```

### 5. Port Already in Use

**Issue:** `Port 8000 is already in use`

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Environment Variables

Critical variables yang harus di-set:

```bash
# Database
DB_PASSWORD=IkodioBugBounty2025!SecureDB
DB_USER=ikodio
DB_NAME=ikodio_bugbounty

# Security
JWT_SECRET=your-secret-key-32-chars-minimum
ENCRYPTION_KEY=must-be-exactly-32-characters!

# Services
RABBITMQ_PASSWORD=IkodioRabbitMQ2025!Secure
GRAFANA_ADMIN_PASSWORD=IkodioGrafana2025!Admin

# Optional (untuk AI features)
OPENAI_API_KEY=sk-your-key-here
```

## API Endpoints to Test

### Public Endpoints
- GET `/health` - Health check
- GET `/` - API root
- GET `/api/docs` - Swagger documentation
- POST `/api/auth/login` - User login
- POST `/api/auth/register` - User registration

### Protected Endpoints (require JWT)
- GET `/api/users/me` - Current user
- GET `/api/bugs` - List bugs
- POST `/api/bugs` - Create bug
- GET `/api/scans` - List scans
- POST `/api/scans` - Start scan
- GET `/api/marketplace` - Marketplace listings

## Database Migrations

```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history
```

## Monitoring URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/IkodioGrafana2025!Admin)
- RabbitMQ: http://localhost:15672 (ikodio/IkodioRabbitMQ2025!Secure)
- Elasticsearch: http://localhost:9200

## Next Steps After Setup

1. **Create Admin User**
   ```bash
   cd backend
   source venv/bin/activate
   python3 -c "from services.auth_service import create_admin; create_admin()"
   ```

2. **Load Sample Data** (optional)
   ```bash
   python3 scripts/load_sample_data.py
   ```

3. **Run Tests**
   ```bash
   cd backend
   pytest tests/ -v
   ```

4. **Start Monitoring**
   - Access Grafana at http://localhost:3001
   - Import dashboards dari monitoring/grafana/dashboards/
   - Configure alerts di Prometheus

## Production Deployment

Before deploying to production:

1. Change all passwords in .env
2. Set DEBUG=false
3. Configure SSL certificates
4. Setup proper backup system
5. Enable Sentry error tracking
6. Configure email/SMS notifications
7. Setup proper logging
8. Configure firewall rules
9. Enable rate limiting
10. Setup monitoring alerts

## Support

Jika masih ada error setelah mengikuti guide ini:

1. Check logs: `docker-compose logs -f`
2. Run system check: `./scripts/check-system.sh`
3. Run test suite: `./scripts/test-system.sh`
4. Check error details di terminal output
5. Verify semua environment variables di .env

## Performance Tips

1. Use Redis untuk caching
2. Enable database connection pooling
3. Use CDN untuk static assets
4. Enable gzip compression
5. Optimize database queries
6. Use async operations
7. Enable query caching
8. Use load balancer untuk multiple backends
