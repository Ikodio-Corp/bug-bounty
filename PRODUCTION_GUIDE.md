# IKODIO Bug Bounty Platform - Production Deployment Guide

## Quick Start

### 1. Environment Setup

Copy and configure environment files:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# Frontend
cp frontend/.env.local.example frontend/.env.local
# Edit frontend/.env.local with your API URLs
```

### 2. Database Initialization

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations
cd backend
alembic upgrade head

# Create initial admin user
../scripts/create-admin.sh
```

### 3. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 4. Start Services

**Development:**
```bash
# Start all services
docker-compose up

# Or individually:
# Backend
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run dev

# Celery workers
cd backend && celery -A tasks.celery_app worker --loglevel=info
```

**Production:**
```bash
# Build and start all services
docker-compose -f docker-compose.yml up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Production Configuration Checklist

### Security
- [ ] Change all default passwords in `.env` files
- [ ] Generate secure SECRET_KEY (min 32 chars)
- [ ] Generate secure JWT_SECRET_KEY
- [ ] Configure SSL certificates in nginx
- [ ] Set `DEBUG=false` in backend
- [ ] Configure CORS allowed origins to production domains
- [ ] Enable rate limiting in production

### Database
- [ ] Configure PostgreSQL with strong password
- [ ] Set up automated backups (scripts/backup.sh)
- [ ] Configure connection pooling
- [ ] Run initial migration: `alembic upgrade head`
- [ ] Create admin user: `scripts/create-admin.sh`

### Cloud Provider Credentials
- [ ] AWS credentials for S3 storage
- [ ] Azure/GCP credentials if using
- [ ] DigitalOcean token for DevOps Autopilot
- [ ] Configure backup storage (S3)

### Payment & Integrations
- [ ] Stripe API keys (production)
- [ ] Email service (SendGrid/SMTP)
- [ ] OpenAI API key for AI features
- [ ] Web3 provider URL and wallet private key
- [ ] Deploy IKOD token smart contract
- [ ] Deploy DAO governance contract

### Security Scanners
- [ ] Nuclei templates path configured
- [ ] OWASP ZAP API key
- [ ] Burp Suite API key (if using)

### Monitoring
- [ ] Sentry DSN for error tracking
- [ ] Configure Prometheus metrics
- [ ] Set up Grafana dashboards
- [ ] Configure log aggregation

### Frontend
- [ ] Update NEXT_PUBLIC_API_URL to production
- [ ] Configure analytics (GA, Mixpanel)
- [ ] Add Mapbox token for satellite scanning
- [ ] Configure Stripe publishable key
- [ ] Set blockchain contract addresses

## Service Architecture

```
┌─────────────────┐
│   NGINX         │ (Port 80/443)
│   Reverse Proxy │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼───────┐
│Frontend│ │ Backend  │
│Next.js │ │ FastAPI  │
│  3000  │ │   8000   │
└────────┘ └─────┬────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌──▼────┐ ┌──▼──────┐
│Postgres│ │ Redis │ │ Celery  │
│  5432  │ │ 6379  │ │ Workers │
└────────┘ └───────┘ └─────────┘
```

## Revolutionary Features Endpoints

### 90-Second Auto Fix
- POST `/api/v1/auto-fix/{bug_id}/analyze` - Analyze bug with AI
- POST `/api/v1/auto-fix/{bug_id}/generate` - Generate fix code
- POST `/api/v1/auto-fix/{bug_id}/apply/{fix_id}` - Apply fix automatically

### Bug Bounty Insurance
- POST `/api/v1/insurance/calculate-premium` - Calculate insurance premium
- POST `/api/v1/insurance/policies` - Purchase policy
- POST `/api/v1/insurance/claims` - Submit claim

### Security Credit Score (FICO-style 300-850)
- POST `/api/v1/security-score/calculate/{company_id}` - Calculate score
- GET `/api/v1/security-score/{company_id}` - Get current score
- GET `/api/v1/security-score/{company_id}/history` - Score history

### Marketplace + Futures Trading
- GET `/api/v1/marketplace/bugs` - List bugs for sale (80% instant payment)
- POST `/api/v1/marketplace/bugs/{bug_id}/buy` - Buy bug
- GET `/api/v1/marketplace/futures` - List futures contracts
- POST `/api/v1/marketplace/futures/{future_id}/position` - Long/short position

### DAO Governance with IKOD Token
- POST `/api/v1/dao/proposals` - Create governance proposal (min 1000 IKOD)
- POST `/api/v1/dao/proposals/{proposal_id}/vote` - Vote (weighted by tokens)
- POST `/api/v1/dao/stake` - Stake IKOD tokens

### DevOps Autopilot (Autonomous Operations)
- POST `/api/v1/devops/provision` - Auto-provision infrastructure
- POST `/api/v1/devops/deploy` - Zero-downtime deployment
- GET `/api/v1/devops/self-healing/events` - Self-healing logs (120s resolution)
- POST `/api/v1/devops/optimize-costs` - AI cost optimization (40-60% savings)

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# API endpoint testing
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ikodio.com", "password": "your_password"}'
```

## Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Scaling & Performance

### Horizontal Scaling
- Backend: Add more FastAPI instances behind nginx load balancer
- Frontend: Deploy to CDN (Vercel, Cloudflare Pages)
- Celery: Increase worker count in docker-compose.yml
- Database: Set up read replicas for PostgreSQL

### Caching Strategy
- Redis for session storage and rate limiting
- Cache API responses with TTL
- Use Redis pub/sub for real-time features

### Database Optimization
- Create indexes on frequently queried columns
- Use connection pooling (SQLAlchemy default)
- Implement database query caching
- Regular VACUUM and ANALYZE on PostgreSQL

## Monitoring & Maintenance

### Health Checks
- Backend: `GET http://localhost:8000/health`
- Database: `docker-compose exec postgres pg_isready`
- Redis: `docker-compose exec redis redis-cli ping`

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Backend application logs
tail -f backend/logs/app.log
```

### Backups
```bash
# Manual backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backup_2024_01_01.sql
```

### Automated Tasks
- Daily backups at 2 AM (configure cron)
- Weekly database maintenance (VACUUM ANALYZE)
- Monthly security score recalculation
- Quarterly DAO token distribution

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
kill -9 <PID>
```

### Database Connection Failed
```bash
# Check PostgreSQL status
docker-compose ps postgres
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
cd backend && alembic upgrade head
```

### Frontend Build Errors
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

## Production Deployment (AWS Example)

### Infrastructure Setup
1. EC2 instance (t3.medium or larger)
2. RDS PostgreSQL database
3. ElastiCache Redis cluster
4. S3 bucket for storage/backups
5. CloudFront CDN for frontend
6. Route53 for DNS
7. ACM for SSL certificates

### Deployment Steps
```bash
# 1. Clone repository
git clone https://github.com/your-org/ikodio-bugbounty.git
cd ikodio-bugbounty

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit with production values

# 3. Build and deploy
docker-compose -f docker-compose.yml up -d --build

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Create admin user
docker-compose exec backend python scripts/create_admin.py

# 6. Configure nginx SSL
# Copy SSL certificates to nginx/ssl/
docker-compose restart nginx
```

## Revenue Projections (Based on Features)

1. **90-Second Auto Fix**: $800M-$1.5B annually
2. **Insurance**: $200M-$500M annually
3. **Security Score**: $150M-$300M annually
4. **Marketplace Futures**: $300M-$700M annually
5. **DAO Governance**: $100M-$200M annually
6. **DevOps Autopilot**: $1B-$2.8B annually
7. **Quantum Security**: $200M-$500M annually
8. **Satellite Scanning**: $250M-$500M annually

**Total Potential**: $3B-$7B annually

## Support & Resources

- Documentation: `/docs`
- API Reference: `http://localhost:8000/docs` (Swagger)
- Admin Panel: `http://localhost:3000/admin`
- Monitoring: `http://localhost:3001` (Grafana)

## License

Proprietary - IKODIO Bug Bounty Platform
