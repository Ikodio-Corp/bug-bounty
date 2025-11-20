#!/bin/bash

set -e

ENVIRONMENT=${1:-production}
BACKUP_FILE=${2:-latest}
NAMESPACE="ikodio-bugbounty"
S3_BUCKET="ikodio-backups"

if [ "$ENVIRONMENT" == "staging" ]; then
    NAMESPACE="ikodio-staging"
fi

echo "Database Backup Restoration"
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo ""

if [ "$BACKUP_FILE" == "latest" ]; then
    echo "Fetching latest backup..."
    BACKUP_FILE=$(aws s3 ls s3://${S3_BUCKET}/database/${ENVIRONMENT}/ | \
        grep "\.sql\.gz$" | \
        sort -r | \
        head -n 1 | \
        awk '{print $4}')
    
    if [ -z "$BACKUP_FILE" ]; then
        echo "Error: No backup files found"
        exit 1
    fi
    
    echo "Latest backup: $BACKUP_FILE"
else
    echo "Using specified backup: $BACKUP_FILE"
fi

read -p "This will OVERWRITE the current database. Continue? (yes/no): " -r
if [ "$REPLY" != "yes" ]; then
    echo "Restoration cancelled"
    exit 0
fi

echo ""
echo "Downloading backup from S3..."
aws s3 cp s3://${S3_BUCKET}/database/${ENVIRONMENT}/${BACKUP_FILE} ./${BACKUP_FILE}

echo "Verifying backup file..."
if [ ! -f "./${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found"
    exit 1
fi

FILE_SIZE=$(stat -f%z ${BACKUP_FILE})
echo "Backup file size: ${FILE_SIZE} bytes"

if [ "$FILE_SIZE" -lt 1000 ]; then
    echo "Error: Backup file too small, may be corrupted"
    exit 1
fi

echo ""
echo "Getting PostgreSQL pod..."
POSTGRES_POD=$(kubectl get pods -n ${NAMESPACE} -l app=postgres -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POSTGRES_POD" ]; then
    echo "Error: PostgreSQL pod not found"
    exit 1
fi

echo "PostgreSQL pod: $POSTGRES_POD"

echo ""
echo "Scaling down backend and celery..."
kubectl scale deployment -n ${NAMESPACE} --replicas=0 \
    ikodio-bugbounty-backend \
    ikodio-bugbounty-celery-worker \
    ikodio-bugbounty-celery-beat

echo "Waiting for pods to terminate..."
kubectl wait --for=delete pod -n ${NAMESPACE} -l app=backend --timeout=300s || true
kubectl wait --for=delete pod -n ${NAMESPACE} -l app=celery-worker --timeout=300s || true

echo ""
echo "Copying backup to PostgreSQL pod..."
kubectl cp ./${BACKUP_FILE} ${NAMESPACE}/${POSTGRES_POD}:/tmp/${BACKUP_FILE}

echo "Dropping existing database..."
kubectl exec -n ${NAMESPACE} ${POSTGRES_POD} -- \
    psql -U postgres -c "DROP DATABASE IF EXISTS ikodio_bugbounty;"

echo "Creating new database..."
kubectl exec -n ${NAMESPACE} ${POSTGRES_POD} -- \
    psql -U postgres -c "CREATE DATABASE ikodio_bugbounty OWNER ikodio_user;"

echo "Restoring database..."
kubectl exec -n ${NAMESPACE} ${POSTGRES_POD} -- \
    bash -c "gunzip < /tmp/${BACKUP_FILE} | psql -U ikodio_user ikodio_bugbounty"

echo "Cleaning up backup file from pod..."
kubectl exec -n ${NAMESPACE} ${POSTGRES_POD} -- rm /tmp/${BACKUP_FILE}

echo ""
echo "Scaling up backend and celery..."
kubectl scale deployment -n ${NAMESPACE} --replicas=3 ikodio-bugbounty-backend
kubectl scale deployment -n ${NAMESPACE} --replicas=3 ikodio-bugbounty-celery-worker
kubectl scale deployment -n ${NAMESPACE} --replicas=1 ikodio-bugbounty-celery-beat

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -n ${NAMESPACE} -l app=backend --timeout=300s
kubectl wait --for=condition=ready pod -n ${NAMESPACE} -l app=celery-worker --timeout=300s

echo ""
echo "Verifying restoration..."
RECORD_COUNT=$(kubectl exec -n ${NAMESPACE} ${POSTGRES_POD} -- \
    psql -U ikodio_user ikodio_bugbounty -t -c "SELECT COUNT(*) FROM users;")

echo "Users in database: ${RECORD_COUNT}"

echo ""
echo "Cleaning up local backup file..."
rm ./${BACKUP_FILE}

echo ""
echo "Database restoration completed successfully"
echo "Backup file: ${BACKUP_FILE}"
echo "Restored records: ${RECORD_COUNT}"
