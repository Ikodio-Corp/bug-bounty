#!/bin/bash

# Ikodio Bug Bounty Platform - Installation Script
# This script sets up the complete platform on a physical server

set -e

echo "🚀 Installing Ikodio Bug Bounty Platform..."
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (use sudo)"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create .env file from example
echo "⚙️  Creating environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please update with your configuration."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p nginx/ssl
mkdir -p nginx/logs
mkdir -p database/backups
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh

# Generate SSL certificates (self-signed for development)
echo "🔒 Generating SSL certificates..."
if [ ! -f nginx/ssl/cert.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Build and start containers
echo "🏗️  Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T backend alembic upgrade head

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
docker-compose exec -T frontend npm install

echo ""
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "🌐 Access the platform at:"
echo "   Frontend: https://localhost"
echo "   API Docs: https://localhost/api/docs"
echo "   Grafana:  http://localhost:3001"
echo ""
echo "📊 Default credentials:"
echo "   Grafana: admin / admin"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Shell:        docker-compose exec backend bash"
echo ""
echo "📝 Next steps:"
echo "   1. Update .env with your API keys"
echo "   2. Create admin user: ./scripts/create-admin.sh"
echo "   3. Review logs: ./scripts/view-logs.sh"
echo ""
