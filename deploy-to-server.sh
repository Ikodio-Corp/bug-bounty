#!/bin/bash

# Deploy IKODIO BugBounty to Production Server
# Server: 192.168.100.6:7420
# User: ikodioxlapo

set -e

echo "======================================================"
echo "   IKODIO BugBounty - Production Deployment Script   "
echo "======================================================"
echo ""

# Configuration
SERVER_USER="ikodioxlapo"
SERVER_HOST="192.168.100.6"
SERVER_PORT="7420"
SERVER_PASS="Mi252512@"
REMOTE_DIR="/home/ikodioxlapo/ikodio-bugbounty"
LOCAL_DIR="/Users/hylmii/Documents/ikodio-bugbounty"

echo "📦 Step 1: Preparing deployment package..."
cd "$LOCAL_DIR"

# Create deployment archive (exclude venv and node_modules)
echo "Creating archive..."
tar -czf deploy.tar.gz \
  --exclude='backend/venv' \
  --exclude='frontend/node_modules' \
  --exclude='frontend/.next' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='deploy.tar.gz' \
  .

echo "✓ Archive created: $(du -h deploy.tar.gz | cut -f1)"

echo ""
echo "🚀 Step 2: Uploading to server..."
# Use tar over SSH pipe instead of SCP
cat deploy.tar.gz | sshpass -p "$SERVER_PASS" ssh -p "$SERVER_PORT" ${SERVER_USER}@${SERVER_HOST} 'cat > /tmp/deploy.tar.gz'
echo "✓ Upload complete"

echo ""
echo "🔧 Step 3: Deploying on server..."
sshpass -p "$SERVER_PASS" ssh -p "$SERVER_PORT" ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
set -e

echo "Creating directory structure..."
mkdir -p /home/ikodioxlapo/ikodio-bugbounty
cd /home/ikodioxlapo/ikodio-bugbounty

# Backup existing deployment
if [ -d "backend" ]; then
  echo "Backing up existing deployment..."
  tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz backend frontend 2>/dev/null || true
fi

echo "Extracting new files..."
tar -xzf /tmp/deploy.tar.gz
rm /tmp/deploy.tar.gz

echo "Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up environment file..."
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://ikodio:ikodio123@localhost/ikodio_bugbounty
POSTGRES_USER=ikodio
POSTGRES_PASSWORD=ikodio123
POSTGRES_DB=ikodio_bugbounty

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=IKODIO BugBounty Platform
ENVIRONMENT=production
DEBUG=false
API_V1_PREFIX=/api/v1

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://192.168.100.6:3000,http://192.168.100.6

# Email (configure with your SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@ikodio.com

# Stripe (configure with your keys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Elasticsearch
ELASTICSEARCH_HOST=localhost:9200
EOF

echo "✓ Backend setup complete"

echo ""
echo "Setting up frontend..."
cd ../frontend

# Install Node.js if not present
if ! command -v node &> /dev/null; then
  echo "Installing Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

echo "Installing dependencies..."
npm install

echo "Setting up environment file..."
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://192.168.100.6:8000
NEXT_PUBLIC_WS_URL=ws://192.168.100.6:8000/ws
EOF

echo "Building frontend..."
npm run build

echo "✓ Frontend setup complete"

echo ""
echo "========================================="
echo "   Deployment Complete! ✓"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Start backend:  cd ~/ikodio-bugbounty/backend && source venv/bin/activate && python start_simple.py"
echo "2. Start frontend: cd ~/ikodio-bugbounty/frontend && npm start"
echo ""
echo "Access the application at:"
echo "  Frontend: http://192.168.100.6:3000"
echo "  Backend:  http://192.168.100.6:8000"
echo "  API Docs: http://192.168.100.6:8000/api/docs"
echo ""

ENDSSH

echo ""
echo "✓ Deployment complete!"
echo ""
echo "📋 Summary:"
echo "  Server:   ${SERVER_HOST}:${SERVER_PORT}"
echo "  User:     ${SERVER_USER}"
echo "  Location: ${REMOTE_DIR}"
echo ""
echo "🎯 To start services on server, run:"
echo "   sshpass -p '${SERVER_PASS}' ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST}"
echo ""

# Cleanup
rm -f deploy.tar.gz

echo "✅ All done!"
