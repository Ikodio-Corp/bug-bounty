#!/bin/bash

# IKODIO Bug Bounty Platform - Dependency Installation Script
# Run this script to install all required dependencies

set -e

echo "=================================="
echo "IKODIO Dependency Installation"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Backend Dependencies
echo "[1/2] Installing Backend Dependencies..."
echo "----------------------------------------"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Backend dependencies installed"
echo ""

cd ..

# Frontend Dependencies
echo "[2/2] Installing Frontend Dependencies..."
echo "----------------------------------------"
cd frontend

if [ ! -f "package.json" ]; then
    echo "Error: package.json not found"
    exit 1
fi

echo "Installing Node.js packages..."
npm install

echo "✓ Frontend dependencies installed"
echo ""

cd ..

# Summary
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next Steps:"
echo "1. Configure environment variables:"
echo "   cp backend/.env.example backend/.env"
echo "   cp frontend/.env.local.example frontend/.env.local"
echo ""
echo "2. Start services:"
echo "   docker-compose up -d postgres redis"
echo ""
echo "3. Run database migrations:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "4. Seed database (optional):"
echo "   python database/seeds/seed_initial_data.py"
echo "   python database/seeds/seed_revolutionary_data.py"
echo ""
echo "5. Start development servers:"
echo "   Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "=================================="
