#!/bin/bash

# ==========================================
# IKODIO BUGBOUNTY - System Check Script
# ==========================================
# Comprehensive system check untuk semua komponen

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/Users/hylmii/Documents/ikodio-bugbounty"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}IKODIO BUGBOUNTY - System Check${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Function to check status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

# 1. Check Environment File
echo -e "${YELLOW}[1/10] Checking .env file...${NC}"
if [ -f "$PROJECT_ROOT/.env" ]; then
    check_status ".env file exists"
    
    # Check critical variables
    if grep -q "DB_PASSWORD=IkodioBugBounty2025" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}  - Database password configured${NC}"
    else
        echo -e "${YELLOW}  - WARNING: Database password may not be set${NC}"
    fi
    
    if grep -q "JWT_SECRET=" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}  - JWT secret configured${NC}"
    else
        echo -e "${RED}  - ERROR: JWT secret not set${NC}"
    fi
else
    echo -e "${RED}✗ .env file not found!${NC}"
    echo -e "${YELLOW}  Run: cp .env.example .env${NC}"
fi
echo ""

# 2. Check Python Installation
echo -e "${YELLOW}[2/10] Checking Python...${NC}"
python3 --version &> /dev/null
check_status "Python 3 installed"
echo ""

# 3. Check Node.js Installation
echo -e "${YELLOW}[3/10] Checking Node.js...${NC}"
node --version &> /dev/null
check_status "Node.js installed"
echo ""

# 4. Check Docker
echo -e "${YELLOW}[4/10] Checking Docker...${NC}"
docker --version &> /dev/null
check_status "Docker installed"

docker-compose version &> /dev/null
check_status "Docker Compose installed"
echo ""

# 5. Check Backend Dependencies
echo -e "${YELLOW}[5/10] Checking Backend Dependencies...${NC}"
cd "$PROJECT_ROOT/backend"

if python3 -c "import fastapi" 2>/dev/null; then
    check_status "FastAPI installed"
else
    echo -e "${RED}✗ FastAPI not installed${NC}"
    echo -e "${YELLOW}  Run: cd backend && pip3 install -r requirements.txt${NC}"
fi

if python3 -c "import sqlalchemy" 2>/dev/null; then
    check_status "SQLAlchemy installed"
else
    echo -e "${RED}✗ SQLAlchemy not installed${NC}"
fi

if python3 -c "import redis" 2>/dev/null; then
    check_status "Redis client installed"
else
    echo -e "${RED}✗ Redis client not installed${NC}"
fi
echo ""

# 6. Check Frontend Dependencies
echo -e "${YELLOW}[6/10] Checking Frontend Dependencies...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ -d "node_modules" ]; then
    check_status "node_modules exists"
else
    echo -e "${RED}✗ node_modules not found${NC}"
    echo -e "${YELLOW}  Run: cd frontend && npm install${NC}"
fi

if [ -f "package.json" ]; then
    check_status "package.json exists"
else
    echo -e "${RED}✗ package.json not found${NC}"
fi
echo ""

# 7. Check Docker Services
echo -e "${YELLOW}[7/10] Checking Docker Services...${NC}"
cd "$PROJECT_ROOT"

RUNNING_CONTAINERS=$(docker-compose ps -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$RUNNING_CONTAINERS" -gt 0 ]; then
    check_status "$RUNNING_CONTAINERS Docker containers running"
    docker-compose ps
else
    echo -e "${YELLOW}✗ No Docker containers running${NC}"
    echo -e "${YELLOW}  Run: docker-compose up -d${NC}"
fi
echo ""

# 8. Check Database Models
echo -e "${YELLOW}[8/10] Checking Database Models...${NC}"
cd "$PROJECT_ROOT/backend"

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from models.audit_log import AuditLog
    from models.notification import Notification
    from models.transaction import Transaction
    from models.futures import FuturesContract
    print('All new models imported successfully')
except Exception as e:
    print(f'Error importing models: {e}')
    sys.exit(1)
" 2>&1

if [ $? -eq 0 ]; then
    check_status "Database models can be imported"
else
    echo -e "${RED}✗ Database models have import errors${NC}"
fi
echo ""

# 9. Check API Routes
echo -e "${YELLOW}[9/10] Checking API Routes...${NC}"
cd "$PROJECT_ROOT/backend/api/routes"

ROUTE_FILES=$(ls -1 *.py 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}  Found $ROUTE_FILES route files${NC}"

# Check critical routes
for route in auth.py users.py bugs.py scans.py marketplace.py; do
    if [ -f "$route" ]; then
        echo -e "${GREEN}  ✓ $route${NC}"
    else
        echo -e "${RED}  ✗ $route missing${NC}"
    fi
done
echo ""

# 10. Check Frontend Pages
echo -e "${YELLOW}[10/10] Checking Frontend Pages...${NC}"
cd "$PROJECT_ROOT/frontend/app"

PAGE_DIRS=$(find . -type f -name "page.tsx" 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}  Found $PAGE_DIRS page components${NC}"

# Check critical pages
for page in page.tsx dashboard/page.tsx login/page.tsx register/page.tsx bugs/page.tsx scans/page.tsx marketplace/page.tsx; do
    if [ -f "$page" ]; then
        echo -e "${GREEN}  ✓ $page${NC}"
    else
        echo -e "${RED}  ✗ $page missing${NC}"
    fi
done
echo ""

# Summary
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Summary${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}Components Found:${NC}"
echo -e "  - Backend API routes: $ROUTE_FILES files"
echo -e "  - Frontend pages: $PAGE_DIRS components"
echo -e "  - Docker containers: $RUNNING_CONTAINERS running"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Install backend dependencies: ${CYAN}cd backend && pip3 install -r requirements.txt${NC}"
echo -e "2. Install frontend dependencies: ${CYAN}cd frontend && npm install${NC}"
echo -e "3. Start Docker services: ${CYAN}docker-compose up -d${NC}"
echo -e "4. Run database migrations: ${CYAN}cd backend && alembic upgrade head${NC}"
echo -e "5. Start backend: ${CYAN}cd backend && python3 main.py${NC}"
echo -e "6. Start frontend: ${CYAN}cd frontend && npm run dev${NC}"
echo ""

echo -e "${GREEN}✓ System check complete${NC}"
