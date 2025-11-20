#!/bin/bash

# Automated Backup Script for IKODIO BugBounty Platform
# Backs up PostgreSQL, Redis, uploaded files, and configurations

set -e

# Configuration
BACKUP_DIR="/var/backups/ikodio"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
S3_BUCKET="${S3_BUCKET:-s3://ikodio-backups}"

# Database credentials
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-ikodio_bugbounty}"
DB_USER="${DB_USER:-ikodio}"
PGPASSWORD="${DB_PASSWORD}"
export PGPASSWORD

# Redis
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create directories
mkdir -p "${BACKUP_DIR}"/{postgres,redis,files,configs}

# Backup PostgreSQL
log "📦 Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "${BACKUP_DIR}/postgres/postgres_${DATE}.sql.gz"
log "✅ PostgreSQL backup completed"

# Backup Redis
log "📦 Backing up Redis..."
docker-compose exec -T redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb "${BACKUP_DIR}/redis/redis_${DATE}.rdb"
gzip "${BACKUP_DIR}/redis/redis_${DATE}.rdb"
log "✅ Redis backup completed"

# Backup files
log "📦 Backing up uploaded files..."
tar -czf "${BACKUP_DIR}/files/files_${DATE}.tar.gz" -C /app/uploads . 2>/dev/null || log "⚠️  No uploads directory"

# Backup configs
log "📦 Backing up configurations..."
tar -czf "${BACKUP_DIR}/configs/configs_${DATE}.tar.gz" docker-compose.yml .env backend/core/config.py

# Upload to S3 (if configured)
if command -v aws &> /dev/null && [ -n "$AWS_ACCESS_KEY_ID" ]; then
    log "☁️  Uploading to S3..."
    tar -czf "/tmp/backup_${DATE}.tar.gz" -C "$BACKUP_DIR" .
    aws s3 cp "/tmp/backup_${DATE}.tar.gz" "${S3_BUCKET}/backups/"
    rm "/tmp/backup_${DATE}.tar.gz"
    log "✅ S3 upload completed"
fi

# Cleanup old backups
log "🧹 Cleaning up old backups..."
find "${BACKUP_DIR}" -type f -mtime +${RETENTION_DAYS} -delete

log "✅ Backup completed successfully"
