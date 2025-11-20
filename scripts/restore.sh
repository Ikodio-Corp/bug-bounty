#!/bin/bash

# Restore database from backup

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    echo "Available backups:"
    ls -lh database/backups/
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will restore the database from backup"
echo "   All current data will be lost!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "📦 Restoring database from $BACKUP_FILE..."

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | docker-compose exec -T postgres psql -U ikodio ikodio_bugbounty
else
    cat $BACKUP_FILE | docker-compose exec -T postgres psql -U ikodio ikodio_bugbounty
fi

echo "✅ Database restored successfully"
