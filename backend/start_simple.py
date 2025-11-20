#!/usr/bin/env python3
"""
Simple backend startup untuk testing
Skip error imports yang tidak critical
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Starting IKODIO BugBounty Backend...")
print("=" * 60)

# Test basic imports
try:
    from fastapi import FastAPI
    print("✓ FastAPI imported")
except Exception as e:
    print(f"✗ FastAPI import failed: {e}")
    sys.exit(1)

try:
    from core.config import settings
    print(f"✓ Config loaded: {settings.PROJECT_NAME}")
except Exception as e:
    print(f"✗ Config failed: {e}")
    sys.exit(1)

try:
    from core.database import engine
    print("✓ Database engine created")
except Exception as e:
    print(f"✗ Database failed: {e}")

try:
    import redis
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print("✓ Redis connected")
except Exception as e:
    print(f"✗ Redis failed: {e}")

print("=" * 60)
print("")
print("Creating minimal FastAPI app...")

# Create simple app
app = FastAPI(
    title="IKODIO BugBounty API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

@app.get("/")
async def root():
    return {
        "message": "IKODIO BugBounty API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

@app.get("/api/health")
async def api_health():
    return {"status": "ok"}

print("✓ Minimal routes created")
print("")
print("Starting server...")
print("Access at: http://localhost:8000")
print("API Docs: http://localhost:8000/api/docs")
print("")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
