#!/bin/bash

# API Documentation Generator
# Generates OpenAPI, Markdown, and Postman documentation

set -e

echo "======================================"
echo "IKODIO API Documentation Generator"
echo "======================================"

cd "$(dirname "$0")/.."

# Check if backend is running
echo "Checking if backend is running..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" | grep -q "200"; then
    echo "Backend is running"
else
    echo "Warning: Backend is not running. Starting backend..."
    # Start backend in background
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    echo "Waiting for backend to start..."
    sleep 5
fi

# Generate documentation
echo ""
echo "Generating API documentation..."
python backend/scripts/generate_docs.py

# Stop backend if we started it
if [ ! -z "$BACKEND_PID" ]; then
    echo "Stopping backend..."
    kill $BACKEND_PID
fi

echo ""
echo "======================================"
echo "Documentation generated successfully!"
echo ""
echo "Generated files:"
echo "  - docs/api/openapi.json"
echo "  - docs/api/API.md"
echo "  - docs/api/postman_collection.json"
echo ""
echo "View documentation:"
echo "  - Swagger UI: http://localhost:8000/api/docs"
echo "  - ReDoc: http://localhost:8000/api/redoc"
echo "  - Markdown: cat docs/api/API.md"
echo ""
echo "Import Postman collection:"
echo "  File -> Import -> docs/api/postman_collection.json"
echo "======================================"
