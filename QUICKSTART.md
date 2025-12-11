# ðŸš€ Quick Start - Ikodio Bug Bounty Platform

## Installation (5 Minutes)

```bash
cd ~/Documents/ikodio-bugbounty
sudo ./scripts/install.sh
```

## Access Platform

- **Website**: https://localhost
- **API Docs**: https://localhost/api/docs
- **Monitoring**: http://localhost:3001

## Essential Commands

```bash
# View all logs
./scripts/view-logs.sh

# View specific service
./scripts/view-logs.sh backend

# Create admin user
./scripts/create-admin.sh

# Backup database
./scripts/backup.sh

# Deploy updates
./scripts/deploy.sh

# Check health
curl -k https://localhost/health
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart service
docker-compose restart backend-api-1

# View running services
docker-compose ps

# Execute command in container
docker-compose exec backend bash
```

## Database Commands

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Rollback
docker-compose exec backend alembic downgrade -1

# Database shell
docker-compose exec postgres psql -U ikodio ikodio_bugbounty
```

## Configuration Files

- `.env` - Main configuration (copy from `.env.example`)
- `backend/core/config.py` - Feature flags
- `docker-compose.yml` - Service definitions
- `nginx/nginx.conf` - Reverse proxy settings

## Required API Keys (Add to .env)

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_API_KEY=sk_test_...
```

## Directory Structure

```
ikodio-bugbounty/
”œ”€”€ backend/          # FastAPI backend
”œ”€”€ frontend/         # Next.js frontend
”œ”€”€ database/         # Migrations & backups
”œ”€”€ nginx/            # Reverse proxy config
”œ”€”€ scripts/          # Deployment scripts
”””€”€ docker-compose.yml
```

## Troubleshooting

**Services won't start:**
```bash
docker-compose down
docker-compose up -d
```

**Check logs:**
```bash
./scripts/view-logs.sh
```

**Reset everything:**
```bash
docker-compose down -v
sudo ./scripts/install.sh
```

## Service Ports

- Nginx: 80, 443
- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432
- Redis: 6379
- RabbitMQ: 5672, 15672
- Elasticsearch: 9200
- Prometheus: 9090
- Grafana: 3001

## Default Credentials

- **Grafana**: admin / admin
- **RabbitMQ**: guest / guest
- **Database**: ikodio / ikodio123

** Change these in production!**

## Feature Flags (.env)

```bash
ENABLE_AI_AGENTS=true
ENABLE_MARKETPLACE=true
ENABLE_GUILD=true
ENABLE_UNIVERSITY=true
ENABLE_QUANTUM=false
ENABLE_SATELLITE=false
ENABLE_GEOPOLITICAL=false
ENABLE_DAO=true
```

## Support

- Full setup guide: `SETUP.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Project overview: `README.md`

## Quick Health Check

```bash
# All services running?
docker-compose ps

# API healthy?
curl -k https://localhost/health

# Frontend accessible?
curl -k https://localhost

# Database connected?
docker-compose exec postgres pg_isready
```

## Development Workflow

1. Edit code in `backend/` or `frontend/`
2. Service auto-reloads (dev mode)
3. Test changes: `curl -k https://localhost/api/...`
4. Commit changes
5. Deploy: `./scripts/deploy.sh`

## Production Checklist

- [ ] Update `.env` with production values
- [ ] Change default passwords
- [ ] Add SSL certificates (Let's Encrypt)
- [ ] Configure domain DNS
- [ ] Set up email SMTP
- [ ] Add AI API keys
- [ ] Configure payment gateway
- [ ] Enable monitoring alerts
- [ ] Set up automated backups
- [ ] Test all features

---

**Ready to launch!** ðŸŽ‰

For detailed instructions, see `SETUP.md`
