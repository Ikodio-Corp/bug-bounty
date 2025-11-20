"""
Database migration script for sharding implementation
Run this script to initialize sharded databases
"""

import asyncio
import sys
from sqlalchemy import text
from core.config import settings
from core.database import engine
from core.sharding import get_shard_manager, SHARD_CONFIGS


async def create_shard_databases():
    """Create databases for each shard"""
    
    if not settings.ENABLE_SHARDING:
        print("Sharding is not enabled in configuration")
        return
    
    print("Creating shard databases...")
    
    # Connect to default postgres database to create new databases
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        
        for config in SHARD_CONFIGS:
            shard_id = config["id"]
            db_name = f"ikodio_shard_{shard_id}"
            
            try:
                # Check if database exists
                result = await conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                )
                exists = result.scalar()
                
                if not exists:
                    print(f"Creating database: {db_name}")
                    await conn.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"Database {db_name} created successfully")
                else:
                    print(f"Database {db_name} already exists")
            
            except Exception as e:
                print(f"Error creating database {db_name}: {e}")


async def run_migrations_on_shards():
    """Run Alembic migrations on all shards"""
    
    import subprocess
    
    print("\nRunning migrations on all shards...")
    
    for config in SHARD_CONFIGS:
        shard_id = config["id"]
        print(f"\nMigrating shard {shard_id}...")
        
        try:
            # Set DATABASE_URL for this shard
            env = {
                "DATABASE_URL": config["url"]
            }
            
            # Run alembic upgrade
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Shard {shard_id} migration successful")
                print(result.stdout)
            else:
                print(f"Shard {shard_id} migration failed")
                print(result.stderr)
        
        except Exception as e:
            print(f"Error migrating shard {shard_id}: {e}")


async def verify_shard_connections():
    """Verify connections to all shards"""
    
    print("\nVerifying shard connections...")
    
    shard_manager = get_shard_manager()
    
    for shard_id in shard_manager.shards.keys():
        try:
            session = await shard_manager.get_session(shard_id)
            
            # Test connection
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
            await session.close()
            
            print(f"Shard {shard_id}: Connection successful")
        
        except Exception as e:
            print(f"Shard {shard_id}: Connection failed - {e}")


async def migrate_existing_data():
    """Migrate existing data from single database to shards"""
    
    from sqlalchemy import select
    from core.database import AsyncSessionLocal
    from models.user import User
    from models.bug import Bug, Scan
    
    print("\nMigrating existing data to shards...")
    
    if not settings.ENABLE_SHARDING:
        print("Sharding must be enabled to migrate data")
        return
    
    shard_manager = get_shard_manager()
    
    # Migrate users
    print("\nMigrating users...")
    async with AsyncSessionLocal() as old_db:
        result = await old_db.execute(select(User))
        users = result.scalars().all()
        
        print(f"Found {len(users)} users to migrate")
        
        for user in users:
            shard_id = shard_manager.get_shard_id_by_hash(user.id)
            shard_session = await shard_manager.get_session(shard_id)
            
            try:
                # Check if user already exists
                existing = await shard_session.get(User, user.id)
                
                if not existing:
                    # Create new user in shard
                    new_user = User(
                        id=user.id,
                        email=user.email,
                        username=user.username,
                        hashed_password=user.hashed_password,
                        full_name=user.full_name,
                        role=user.role,
                        is_active=user.is_active,
                        is_verified=user.is_verified
                    )
                    shard_session.add(new_user)
                    await shard_session.commit()
                    print(f"Migrated user {user.id} to shard {shard_id}")
            
            except Exception as e:
                print(f"Error migrating user {user.id}: {e}")
                await shard_session.rollback()
            
            finally:
                await shard_session.close()
    
    # Migrate bugs
    print("\nMigrating bugs...")
    async with AsyncSessionLocal() as old_db:
        result = await old_db.execute(select(Bug))
        bugs = result.scalars().all()
        
        print(f"Found {len(bugs)} bugs to migrate")
        
        for bug in bugs:
            shard_id = shard_manager.get_shard_id_by_hash(bug.id)
            shard_session = await shard_manager.get_session(shard_id)
            
            try:
                existing = await shard_session.get(Bug, bug.id)
                
                if not existing:
                    new_bug = Bug(
                        id=bug.id,
                        reporter_id=bug.reporter_id,
                        title=bug.title,
                        description=bug.description,
                        bug_type=bug.bug_type,
                        severity=bug.severity,
                        status=bug.status,
                        target_url=bug.target_url,
                        proof_of_concept=bug.proof_of_concept,
                        cvss_score=bug.cvss_score
                    )
                    shard_session.add(new_bug)
                    await shard_session.commit()
                    print(f"Migrated bug {bug.id} to shard {shard_id}")
            
            except Exception as e:
                print(f"Error migrating bug {bug.id}: {e}")
                await shard_session.rollback()
            
            finally:
                await shard_session.close()
    
    # Migrate scans
    print("\nMigrating scans...")
    async with AsyncSessionLocal() as old_db:
        result = await old_db.execute(select(Scan))
        scans = result.scalars().all()
        
        print(f"Found {len(scans)} scans to migrate")
        
        for scan in scans:
            shard_id = shard_manager.get_shard_id_by_hash(scan.id)
            shard_session = await shard_manager.get_session(shard_id)
            
            try:
                existing = await shard_session.get(Scan, scan.id)
                
                if not existing:
                    new_scan = Scan(
                        id=scan.id,
                        user_id=scan.user_id,
                        target_url=scan.target_url,
                        scan_type=scan.scan_type,
                        status=scan.status,
                        start_time=scan.start_time
                    )
                    shard_session.add(new_scan)
                    await shard_session.commit()
                    print(f"Migrated scan {scan.id} to shard {shard_id}")
            
            except Exception as e:
                print(f"Error migrating scan {scan.id}: {e}")
                await shard_session.rollback()
            
            finally:
                await shard_session.close()
    
    print("\nData migration completed!")


async def main():
    """Main migration script"""
    
    print("=" * 60)
    print("Database Sharding Migration Script")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            await create_shard_databases()
        
        elif command == "migrate":
            await run_migrations_on_shards()
        
        elif command == "verify":
            await verify_shard_connections()
        
        elif command == "data":
            await migrate_existing_data()
        
        elif command == "all":
            await create_shard_databases()
            await run_migrations_on_shards()
            await verify_shard_connections()
            
            response = input("\nMigrate existing data? (yes/no): ")
            if response.lower() == "yes":
                await migrate_existing_data()
        
        else:
            print(f"Unknown command: {command}")
            print_usage()
    
    else:
        print_usage()


def print_usage():
    """Print usage instructions"""
    
    print("\nUsage:")
    print("  python migrate_sharding.py <command>")
    print("\nCommands:")
    print("  create   - Create shard databases")
    print("  migrate  - Run Alembic migrations on all shards")
    print("  verify   - Verify shard connections")
    print("  data     - Migrate existing data to shards")
    print("  all      - Run all steps")
    print("\nExample:")
    print("  python migrate_sharding.py all")


if __name__ == "__main__":
    asyncio.run(main())
