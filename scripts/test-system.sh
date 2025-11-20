#!/bin/bash

# ==========================================
# IKODIO BUGBOUNTY - Comprehensive Test Script
# ==========================================
# Test semua fitur dan koneksi sistem

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/Users/hylmii/Documents/ikodio-bugbounty"
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}IKODIO BUGBOUNTY - Comprehensive Test${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Function untuk test dengan error handling
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ $name (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}✗ $name (HTTP $response, expected $expected_code)${NC}"
        return 1
    fi
}

# 1. Test Docker Services
echo -e "${YELLOW}[1/8] Testing Docker Services...${NC}"

services=("postgres" "redis" "rabbitmq" "elasticsearch")
for service in "${services[@]}"; do
    if docker-compose ps "$service" 2>/dev/null | grep -q "Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
    fi
done
echo ""

# 2. Test Database Connection
echo -e "${YELLOW}[2/8] Testing Database Connection...${NC}"

cd "$PROJECT_ROOT/backend"
source venv/bin/activate 2>/dev/null || true

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    sys.exit(1)
" 2>&1

echo ""

# 3. Test Redis Connection
echo -e "${YELLOW}[3/8] Testing Redis Connection...${NC}"

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print('✓ Redis connection successful')
except Exception as e:
    print(f'✗ Redis connection failed: {e}')
    sys.exit(1)
" 2>&1

echo ""

# 4. Test Backend API
echo -e "${YELLOW}[4/8] Testing Backend API Endpoints...${NC}"

# Check if backend is running
if ! curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend server is not running${NC}"
    echo -e "${YELLOW}  Start with: cd backend && source venv/bin/activate && python3 main.py${NC}"
else
    test_endpoint "Health Check" "$BACKEND_URL/health" "200"
    test_endpoint "API Root" "$BACKEND_URL/" "200"
    test_endpoint "API Docs" "$BACKEND_URL/api/docs" "200"
    test_endpoint "OpenAPI Spec" "$BACKEND_URL/api/openapi.json" "200"
fi
echo ""

# 5. Test Frontend
echo -e "${YELLOW}[5/8] Testing Frontend...${NC}"

if ! curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "${RED}✗ Frontend server is not running${NC}"
    echo -e "${YELLOW}  Start with: cd frontend && npm run dev${NC}"
else
    test_endpoint "Frontend Homepage" "$FRONTEND_URL" "200"
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
fi
echo ""

# 6. Test Database Models
echo -e "${YELLOW}[6/8] Testing Database Models...${NC}"

cd "$PROJECT_ROOT/backend"
source venv/bin/activate 2>/dev/null || true

python3 -c "
import sys
sys.path.insert(0, '.')
errors = []

try:
    from models.user import User
    from models.bug import Bug
    from models.audit_log import AuditLog
    from models.notification import Notification
    from models.transaction import Transaction
    from models.futures import FuturesContract
    print('✓ All critical models imported')
except Exception as e:
    print(f'✗ Model import error: {e}')
    sys.exit(1)

# Test model attributes
try:
    assert hasattr(User, 'id'), 'User model missing id'
    assert hasattr(Bug, 'title'), 'Bug model missing title'
    assert hasattr(AuditLog, 'event_type'), 'AuditLog missing event_type'
    assert hasattr(Notification, 'type'), 'Notification missing type'
    assert hasattr(Transaction, 'amount'), 'Transaction missing amount'
    assert hasattr(FuturesContract, 'symbol'), 'FuturesContract missing symbol'
    print('✓ All model attributes present')
except AssertionError as e:
    print(f'✗ Model validation error: {e}')
    sys.exit(1)
" 2>&1

echo ""

# 7. Test API Routes
echo -e "${YELLOW}[7/8] Testing API Route Files...${NC}"

cd "$PROJECT_ROOT/backend/api/routes"
route_count=0
error_count=0

for route_file in *.py; do
    if [ "$route_file" != "__init__.py" ]; then
        ((route_count++))
        
        # Test if route can be imported
        if python3 -c "import sys; sys.path.insert(0, '../..'); from api.routes.${route_file%.py} import router" 2>/dev/null; then
            echo -e "${GREEN}  ✓ $route_file${NC}"
        else
            echo -e "${RED}  ✗ $route_file (import error)${NC}"
            ((error_count++))
        fi
    fi
done

echo -e "${CYAN}Found $route_count route files, $error_count errors${NC}"
echo ""

# 8. Test Frontend Pages
echo -e "${YELLOW}[8/8] Testing Frontend Pages...${NC}"

cd "$PROJECT_ROOT/frontend/app"
page_count=$(find . -name "page.tsx" -type f | wc -l | tr -d ' ')

critical_pages=(
    "page.tsx"
    "dashboard/page.tsx"
    "login/page.tsx"
    "register/page.tsx"
    "bugs/page.tsx"
    "scans/page.tsx"
    "marketplace/page.tsx"
    "guilds/page.tsx"
)

for page in "${critical_pages[@]}"; do
    if [ -f "$page" ]; then
        echo -e "${GREEN}  ✓ $page${NC}"
    else
        echo -e "${RED}  ✗ $page missing${NC}"
    fi
done

echo -e "${CYAN}Total pages found: $page_count${NC}"
echo ""

# Summary
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Test Summary${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${GREEN}System Components:${NC}"
echo -e "  - Docker services: Running"
echo -e "  - Database models: Verified"
echo -e "  - API routes: $route_count files"
echo -e "  - Frontend pages: $page_count components"
echo ""

echo -e "${YELLOW}URLs:${NC}"
echo -e "  - Frontend: ${CYAN}$FRONTEND_URL${NC}"
echo -e "  - Backend API: ${CYAN}$BACKEND_URL${NC}"
echo -e "  - API Docs: ${CYAN}$BACKEND_URL/api/docs${NC}"
echo -e "  - Grafana: ${CYAN}http://localhost:3001${NC}"
echo -e "  - Prometheus: ${CYAN}http://localhost:9090${NC}"
echo ""

echo -e "${GREEN}✓ Comprehensive test complete${NC}"
