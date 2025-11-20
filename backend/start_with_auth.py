#!/usr/bin/env python3
"""
Backend with Mock Authentication
Quick setup untuk testing dashboard
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

# Configuration
SECRET_KEY = "ikodio-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock users database - passwords are stored in plain text for demo
MOCK_USERS = {
    "admin@ikodio.com": {
        "id": 1,
        "email": "admin@ikodio.com",
        "username": "admin",
        "password": "admin123",  # Plain text for demo
        "full_name": "Admin IKODIO",
        "is_active": True,
        "is_superuser": True,
        "role": "admin"
    },
    "demo@ikodio.com": {
        "id": 2,
        "email": "demo@ikodio.com",
        "username": "demo",
        "password": "demo123",  # Plain text for demo
        "full_name": "Demo User",
        "is_active": True,
        "is_superuser": False,
        "role": "user"
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    role: str

# Create app
app = FastAPI(
    title="IKODIO BugBounty API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password, stored_password):
    # Simple comparison for demo (not secure for production!)
    return plain_password == stored_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = MOCK_USERS.get(email)
        if user is None:
            raise credentials_exception
        return user
    except jwt.PyJWTError:
        raise credentials_exception

# Routes
@app.get("/")
async def root():
    return {
        "message": "IKODIO BugBounty API",
        "version": "1.0.0",
        "status": "running",
        "auth": "enabled"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "mock",
        "redis": "connected",
        "auth": "enabled"
    }

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "auth": "enabled"}

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Try email or username
    user = MOCK_USERS.get(form_data.username)
    if not user:
        # Try finding by username
        for email, u in MOCK_USERS.items():
            if u["username"] == form_data.username:
                user = u
                break
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/register")
async def register(email: str, username: str, password: str, full_name: str = None):
    if email in MOCK_USERS:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": len(MOCK_USERS) + 1,
        "email": email,
        "username": username,
        "password": password,  # Plain text for demo
        "full_name": full_name or username,
        "is_active": True,
        "is_superuser": False,
        "role": "user"
    }
    MOCK_USERS[email] = new_user
    
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=User)
async def get_me(current_user = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        full_name=current_user["full_name"],
        is_active=current_user["is_active"],
        role=current_user["role"]
    )

@app.get("/api/dashboard/stats")
async def dashboard_stats(current_user = Depends(get_current_user)):
    return {
        "total_scans": 42,
        "active_bugs": 15,
        "resolved_bugs": 27,
        "total_earnings": 15000,
        "pending_rewards": 2500,
        "success_rate": 85.5,
        "rank": 127,
        "recent_scans": [
            {"id": 1, "target": "example.com", "status": "completed", "bugs_found": 3},
            {"id": 2, "target": "testsite.com", "status": "in_progress", "bugs_found": 0},
        ]
    }

print("=" * 60)
print("IKODIO BugBounty Backend - With Mock Auth")
print("=" * 60)
print("")
print("Mock User Accounts:")
print("  Admin:")
print("    Email: admin@ikodio.com")
print("    Password: admin123")
print("")
print("  Demo:")
print("    Email: demo@ikodio.com")
print("    Password: demo123")
print("")
print("Starting server...")
print("Access at: http://localhost:8001")
print("API Docs: http://localhost:8001/api/docs")
print("")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
