#!/bin/bash

# Create admin user

echo "Creating admin user..."

docker-compose exec backend python -c "
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db, engine
from services.auth_service import AuthService
from models.user import UserRole

async def create_admin():
    async with AsyncSession(engine) as db:
        auth_service = AuthService(db)
        
        email = input('Admin email: ')
        username = input('Admin username: ')
        password = input('Admin password: ')
        full_name = input('Full name: ')
        
        user = await auth_service.create_user(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            role=UserRole.ADMIN
        )
        
        print(f'✅ Admin user created: {user.username}')

asyncio.run(create_admin())
"
