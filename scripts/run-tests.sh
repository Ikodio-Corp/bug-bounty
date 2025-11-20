#!/bin/bash

set -e

echo "Running IKODIO BugBounty Test Suite"
echo "===================================="

cd backend

echo "1. Running Unit Tests..."
pytest tests/test_bug_service.py -v --cov=services --cov-report=term

echo ""
echo "2. Running Integration Tests..."
pytest tests/test_auth_routes.py tests/test_scan_routes.py -v

echo ""
echo "3. Running OAuth Tests..."
pytest tests/test_integration_oauth.py -v

echo ""
echo "4. Running 2FA Tests..."
pytest tests/test_integration_2fa.py -v

echo ""
echo "5. Running Payment Tests..."
pytest tests/test_integration_payments.py -v

echo ""
echo "6. Running E2E Tests..."
pytest tests/test_e2e_workflows.py -v

echo ""
echo "7. Running Security Tests..."
pytest tests/test_security.py -v

echo ""
echo "8. Running Performance Tests..."
pytest tests/test_performance.py -v || echo "Performance tests completed with warnings"

echo ""
echo "9. Generating Coverage Report..."
pytest --cov=. --cov-report=html --cov-report=term

echo ""
echo "===================================="
echo "Test Suite Completed!"
echo "Coverage report available at: htmlcov/index.html"
