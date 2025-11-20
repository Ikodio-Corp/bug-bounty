#!/usr/bin/env python3
"""Test registration directly"""
import asyncio
import sys
sys.path.insert(0, '/home/ikodioxlapo/ikodio-bugbounty/backend')

from services.auth_service import AuthService
from core.database import AsyncSessionLocal
from core.security import Security
from models.user import UserRole

async def test():
    db = AsyncSessionLocal()
    service = AuthService(db)
    
    try:
        user = await service.create_user(
            email="test@example.com",
            username="testuser",
            password="Test1234!",
            full_name="Test User",
            role=UserRole.HUNTER
        )
        print(f"✅ User created: {user.id}, {user.email}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

asyncio.run(test())
