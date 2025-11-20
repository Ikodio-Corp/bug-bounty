#!/bin/bash

# ==========================================
# IKODIO BUGBOUNTY - Quick Setup Script
# ==========================================
# Setup semua dependencies dan environment

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/Users/hylmii/Documents/ikodio-bugbounty"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}IKODIO BUGBOUNTY - Quick Setup${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 1. Setup Python Virtual Environment
echo -e "${YELLOW}[1/5] Setting up Python virtual environment...${NC}"
cd "$PROJECT_ROOT/backend"

if [ ! -d "venv" ]; then
    echo -e "${CYAN}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# 2. Install Python Dependencies
echo -e "${YELLOW}[2/5] Installing Python dependencies...${NC}"
echo -e "${CYAN}This may take 5-10 minutes...${NC}"

pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies in groups for better error handling
echo -e "${CYAN}Installing core dependencies...${NC}"
pip install fastapi uvicorn pydantic pydantic-settings python-multipart > /dev/null 2>&1
echo -e "${GREEN}✓ FastAPI installed${NC}"

echo -e "${CYAN}Installing database dependencies...${NC}"
pip install sqlalchemy alembic psycopg2-binary asyncpg > /dev/null 2>&1
echo -e "${GREEN}✓ Database libraries installed${NC}"

echo -e "${CYAN}Installing Redis and Celery...${NC}"
pip install redis hiredis celery kombu > /dev/null 2>&1
echo -e "${GREEN}✓ Redis and Celery installed${NC}"

echo -e "${CYAN}Installing AI dependencies (this will take time)...${NC}"
pip install openai anthropic langchain langchain-openai tiktoken > /dev/null 2>&1
echo -e "${GREEN}✓ AI libraries installed${NC}"

echo -e "${CYAN}Installing security and utilities...${NC}"
pip install python-jose passlib bcrypt cryptography python-dotenv requests httpx > /dev/null 2>&1
echo -e "${GREEN}✓ Security libraries installed${NC}"

echo -e "${CYAN}Installing monitoring tools...${NC}"
pip install prometheus-client sentry-sdk loguru > /dev/null 2>&1
echo -e "${GREEN}✓ Monitoring tools installed${NC}"

echo -e "${CYAN}Installing payment and cloud SDKs...${NC}"
pip install stripe boto3 elasticsearch > /dev/null 2>&1
echo -e "${GREEN}✓ Payment and cloud SDKs installed${NC}"

echo -e "${CYAN}Installing testing tools...${NC}"
pip install pytest pytest-asyncio pytest-cov pytest-mock faker > /dev/null 2>&1
echo -e "${GREEN}✓ Testing tools installed${NC}"

echo ""

# 3. Setup Frontend
echo -e "${YELLOW}[3/5] Setting up frontend dependencies...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓ node_modules already exists${NC}"
else
    echo -e "${CYAN}Running npm install...${NC}"
    npm install > /dev/null 2>&1
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi
echo ""

# 4. Setup Docker Services
echo -e "${YELLOW}[4/5] Starting Docker services...${NC}"
cd "$PROJECT_ROOT"

RUNNING=$(docker-compose ps -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$RUNNING" -gt 0 ]; then
    echo -e "${GREEN}✓ Docker services already running ($RUNNING containers)${NC}"
else
    echo -e "${CYAN}Starting Docker services...${NC}"
    docker-compose up -d postgres redis rabbitmq elasticsearch
    
    echo -e "${CYAN}Waiting for services to be ready...${NC}"
    sleep 10
    
    echo -e "${GREEN}✓ Docker services started${NC}"
    docker-compose ps
fi
echo ""

# 5. Verify Installation
echo -e "${YELLOW}[5/5] Verifying installation...${NC}"
cd "$PROJECT_ROOT/backend"
source venv/bin/activate

# Test imports
python3 -c "
import fastapi
import sqlalchemy
import redis
import celery
print('✓ All critical packages imported successfully')
" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies verified${NC}"
else
    echo -e "${RED}✗ Some dependencies failed to import${NC}"
fi

# Test database models
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from models.audit_log import AuditLog
    from models.notification import Notification
    from models.transaction import Transaction
    from models.futures import FuturesContract
    print('✓ Database models imported successfully')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database models verified${NC}"
else
    echo -e "${RED}✗ Database models have errors${NC}"
fi
echo ""

# Summary
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Setup Complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${GREEN}Virtual Environment:${NC}"
echo -e "  Location: ${CYAN}$PROJECT_ROOT/backend/venv${NC}"
echo -e "  Activate: ${CYAN}source backend/venv/bin/activate${NC}"
echo ""

echo -e "${GREEN}Running Services:${NC}"
docker-compose ps 2>/dev/null | grep -E "Up|running" || echo -e "${YELLOW}  No services running yet${NC}"
echo ""

echo -e "${GREEN}Next Steps:${NC}"
echo -e "1. Run database migrations:"
echo -e "   ${CYAN}cd backend && source venv/bin/activate && alembic upgrade head${NC}"
echo -e ""
echo -e "2. Start backend server:"
echo -e "   ${CYAN}cd backend && source venv/bin/activate && python3 main.py${NC}"
echo -e ""
echo -e "3. Start frontend (in new terminal):"
echo -e "   ${CYAN}cd frontend && npm run dev${NC}"
echo -e ""
echo -e "4. Access application:"
echo -e "   Frontend: ${CYAN}http://localhost:3000${NC}"
echo -e "   Backend API: ${CYAN}http://localhost:8000${NC}"
echo -e "   API Docs: ${CYAN}http://localhost:8000/api/docs${NC}"
echo ""

echo -e "${GREEN}✓ Setup complete! Happy hacking!${NC}"
