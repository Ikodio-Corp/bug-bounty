#!/bin/bash

# Deploy updates to production

set -e

echo "🚀 Deploying Ikodio Bug Bounty Platform..."

# Pull latest changes (if using git)
# git pull origin main

# Rebuild containers
echo "🏗️  Rebuilding containers..."
docker-compose build

# Run database migrations
echo "🗄️  Running migrations..."
docker-compose exec -T backend alembic upgrade head

# Restart services with zero downtime
echo "🔄 Restarting services..."
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# Clean up old images
echo "🧹 Cleaning up..."
docker image prune -f

echo "✅ Deployment complete!"
