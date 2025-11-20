# Production Environment Setup Guide

## Prerequisites

Before deploying to production, ensure you have:

1. Domain name configured (ikodio.com)
2. SSL certificates (Let's Encrypt or commercial)
3. Cloud infrastructure (AWS, GCP, or Azure)
4. Database servers provisioned
5. Redis cluster setup
6. Monitoring tools configured
7. CI/CD pipeline ready

## Environment Variables

### Required Configuration

Copy `.env.production.example` to `.env.production` and update all values:

```bash
cp .env.production.example .env.production
```

### Critical Values to Change

**Security Keys** (Generate with `openssl rand -base64 32`):
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `REDIS_PASSWORD`

**Database Credentials**:
- `DATABASE_URL` - Primary database connection
- `DATABASE_URL_SHARD_0/1/2` - Shard connections
- Update username, password, and host

**External Services**:
- `STRIPE_SECRET_KEY` - Production Stripe key
- `SMTP_PASSWORD` - Email service password
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `SENTRY_DSN` - Error tracking

## Infrastructure Setup

### 1. Database Configuration

#### PostgreSQL Primary
```sql
-- Create production database
CREATE DATABASE ikodio_prod;
CREATE USER ikodio_prod WITH ENCRYPTED PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE ikodio_prod TO ikodio_prod;

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '10MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Reload configuration
SELECT pg_reload_conf();
```

#### Database Sharding
```bash
# Run migration script
python backend/scripts/migrate_sharding.py all

# Verify shard connections
python backend/scripts/migrate_sharding.py verify
```

### 2. Redis Configuration

```bash
# Redis production config
cat > /etc/redis/redis-prod.conf << EOF
bind 0.0.0.0
protected-mode yes
port 6379
requirepass secure-redis-password
maxmemory 4gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
EOF

# Start Redis
redis-server /etc/redis/redis-prod.conf
```

### 3. SSL/TLS Certificates

#### Using Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d ikodio.com -d www.ikodio.com -d api.ikodio.com

# Auto-renewal
sudo certbot renew --dry-run
```

#### Manual Certificate
```bash
# Copy certificates
sudo cp ikodio.crt /etc/ssl/certs/
sudo cp ikodio.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/ikodio.key
```

### 4. Nginx Configuration

```nginx
# /etc/nginx/sites-available/ikodio-prod
upstream backend {
    least_conn;
    server backend-1.internal:8000 max_fails=3 fail_timeout=30s;
    server backend-2.internal:8000 max_fails=3 fail_timeout=30s;
    server backend-3.internal:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name ikodio.com www.ikodio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ikodio.com www.ikodio.com;

    ssl_certificate /etc/ssl/certs/ikodio.crt;
    ssl_certificate_key /etc/ssl/private/ikodio.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location / {
        root /var/www/ikodio/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

### 5. Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 6. Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace ikodio-prod

# Create secrets
kubectl create secret generic ikodio-secrets \
    --from-env-file=.env.production \
    --namespace=ikodio-prod

# Apply configurations
kubectl apply -f kubernetes/prod/ --namespace=ikodio-prod

# Check deployment
kubectl get pods -n ikodio-prod
kubectl get services -n ikodio-prod
```

## Monitoring Setup

### 1. Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ikodio-backend'
    static_configs:
      - targets: ['backend-1:8000', 'backend-2:8000', 'backend-3:8000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 2. Grafana

```bash
# Import dashboards
curl -X POST http://grafana:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/dashboards/ikodio-main.json
```

### 3. Sentry

```python
# Already configured in backend/main.py
# Update SENTRY_DSN in .env.production
```

## Database Migration

```bash
# Run migrations
alembic upgrade head

# Seed production data
python backend/database/seeds/production_seed.py

# Verify
python -c "from backend.core.database import engine; print('Connected:', engine.url)"
```

## Health Checks

```bash
# Backend health
curl https://api.ikodio.com/health

# Database health
curl https://api.ikodio.com/health/db

# Redis health
curl https://api.ikodio.com/health/redis

# All services
curl https://api.ikodio.com/health/all
```

## Backup Configuration

### Database Backup
```bash
# Daily backup script
cat > /opt/ikodio/scripts/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/database"
pg_dump -U ikodio_prod ikodio_prod | gzip > "$BACKUP_DIR/ikodio_$DATE.sql.gz"
# Keep only last 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/ikodio/scripts/backup-db.sh

# Add to crontab
echo "0 2 * * * /opt/ikodio/scripts/backup-db.sh" | crontab -
```

### Redis Backup
```bash
# Redis persistence already enabled with appendonly yes
# Additional backup
redis-cli --rdb /backup/redis/dump_$(date +%Y%m%d).rdb
```

## Security Hardening

### 1. Firewall Rules
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (change default port)
sudo ufw allow 2222/tcp

# Enable firewall
sudo ufw enable
```

### 2. Fail2Ban
```bash
# Install
sudo apt-get install fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Database Security
```sql
-- Restrict superuser access
REVOKE ALL ON DATABASE ikodio_prod FROM PUBLIC;

-- Enable SSL connections only
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';
```

## Performance Tuning

### 1. Application
- Enable connection pooling (already configured)
- Implement caching (Redis configured)
- Use CDN for static assets
- Enable gzip compression (Nginx configured)

### 2. Database
- Create appropriate indexes
- Analyze query performance
- Configure autovacuum
- Monitor slow queries

### 3. Redis
- Monitor memory usage
- Configure eviction policy
- Use Redis cluster for scaling

## Scaling Strategy

### Horizontal Scaling
```bash
# Add more backend instances
docker-compose -f docker-compose.prod.yml scale backend=5

# Or with Kubernetes
kubectl scale deployment ikodio-backend --replicas=5 -n ikodio-prod
```

### Database Read Replicas
```sql
-- Setup streaming replication
-- On primary:
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'rep_password';

-- On replica:
pg_basebackup -h primary-host -D /var/lib/postgresql/data -U replicator -P -W
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Nginx configured
- [ ] Docker containers running
- [ ] Monitoring dashboards accessible
- [ ] Backup jobs scheduled
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] DNS records configured
- [ ] CDN configured
- [ ] Email service tested
- [ ] Payment gateway tested
- [ ] Error tracking configured
- [ ] Documentation updated

## Rollback Procedure

```bash
# 1. Stop current deployment
docker-compose -f docker-compose.prod.yml down

# 2. Restore previous image
docker tag ikodio-backend:previous ikodio-backend:latest

# 3. Restore database backup
gunzip < /backup/database/ikodio_YYYYMMDD.sql.gz | psql -U ikodio_prod ikodio_prod

# 4. Restart services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://api.ikodio.com/health
```

## Maintenance Mode

```bash
# Enable maintenance mode
echo "maintenance_mode = true" > /var/www/ikodio/maintenance

# Nginx will serve maintenance page
# Configure in Nginx:
if (-f /var/www/ikodio/maintenance) {
    return 503;
}
error_page 503 @maintenance;
location @maintenance {
    root /var/www/ikodio;
    rewrite ^(.*)$ /maintenance.html break;
}

# Disable maintenance mode
rm /var/www/ikodio/maintenance
```

## Support Contacts

- DevOps: devops@ikodio.com
- Security: security@ikodio.com
- On-call: +1-XXX-XXX-XXXX
- PagerDuty: https://ikodio.pagerduty.com
