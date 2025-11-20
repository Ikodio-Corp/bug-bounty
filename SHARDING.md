# Database Sharding Configuration

## Overview
IKODIO BugBounty Platform implements horizontal database sharding for scalability and performance.

## Sharding Strategy

### Shard Distribution
- **Shard 0**: US East (Primary) - Users 0-999,999
- **Shard 1**: US West - Users 1,000,000-1,999,999
- **Shard 2**: EU - Users 2,000,000-2,999,999

### Sharding Keys
- **Users**: `user_id` (hash-based)
- **Bugs**: `bug_id` (hash-based)
- **Scans**: `scan_id` (hash-based)
- **Geographic Data**: `region` (geographic-based)

## Implementation

### 1. Database Setup

Create separate databases for each shard:

```sql
-- Shard 0
CREATE DATABASE ikodio_shard_0;

-- Shard 1
CREATE DATABASE ikodio_shard_1;

-- Shard 2
CREATE DATABASE ikodio_shard_2;
```

### 2. Configuration

Add to `.env`:

```bash
# Sharding Configuration
ENABLE_SHARDING=true

# Shard 0 - US East
DATABASE_URL_SHARD_0=postgresql://user:pass@db-shard-0:5432/ikodio_shard_0

# Shard 1 - US West
DATABASE_URL_SHARD_1=postgresql://user:pass@db-shard-1:5432/ikodio_shard_1

# Shard 2 - EU
DATABASE_URL_SHARD_2=postgresql://user:pass@db-shard-2:5432/ikodio_shard_2
```

### 3. Initialize Shards

```bash
# Run migrations on each shard
alembic -x shard=0 upgrade head
alembic -x shard=1 upgrade head
alembic -x shard=2 upgrade head
```

## Usage Examples

### Using Sharded Services

```python
from core.sharding import ShardedBugService, ShardedUserService

# Bug service
bug_service = ShardedBugService()

# Get bug (automatically routed to correct shard)
bug = await bug_service.get_bug(bug_id=12345)

# Create bug
new_bug = await bug_service.create_bug(
    bug_id=67890,
    title="XSS Vulnerability",
    severity="high"
)

# Search across all shards
bugs = await bug_service.search_bugs({
    "severity": "critical",
    "status": "open"
})

# User service
user_service = ShardedUserService()

# Get user
user = await user_service.get_user(user_id=54321)

# Get user by email (searches all shards)
user = await user_service.get_user_by_email("user@example.com")
```

### Direct Shard Manager Usage

```python
from core.sharding import get_shard_manager

manager = get_shard_manager()

# Get session for specific user
user_id = 12345
session = await manager.get_session_by_key(user_id)

# Execute query
from models.user import User
from sqlalchemy import select

query = select(User).where(User.id == user_id)
result = await session.execute(query)
user = result.scalar_one_or_none()

await session.close()
```

## Migration Strategy

### Phase 1: Single Database (Current)
- All data in single database
- No sharding enabled

### Phase 2: Dual Mode
- Sharding enabled
- New data goes to shards
- Old data remains in primary DB
- Background migration process

### Phase 3: Full Sharding
- All data migrated to shards
- Primary DB decommissioned
- Full horizontal scaling

## Data Migration Script

```python
# backend/scripts/migrate_to_shards.py

import asyncio
from core.database import get_db
from core.sharding import get_shard_manager
from models.user import User
from sqlalchemy import select

async def migrate_users():
    """Migrate users to sharded databases"""
    
    # Get old database session
    old_db = await anext(get_db())
    
    # Get shard manager
    shard_manager = get_shard_manager()
    
    # Fetch all users
    result = await old_db.execute(select(User))
    users = result.scalars().all()
    
    print(f"Migrating {len(users)} users...")
    
    for user in users:
        # Determine target shard
        shard_id = shard_manager.get_shard_id_by_hash(user.id)
        
        # Get shard session
        shard_session = await shard_manager.get_session(shard_id)
        
        try:
            # Check if user already exists
            existing = await shard_session.get(User, user.id)
            
            if not existing:
                # Copy user to shard
                shard_session.add(user)
                await shard_session.commit()
                print(f"Migrated user {user.id} to shard {shard_id}")
            else:
                print(f"User {user.id} already in shard {shard_id}")
        
        finally:
            await shard_session.close()
    
    print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate_users())
```

## Monitoring

### Shard Health Check

```python
from core.sharding import get_shard_manager

async def check_shard_health():
    manager = get_shard_manager()
    
    for shard_id in manager.shards.keys():
        try:
            session = await manager.get_session(shard_id)
            await session.execute("SELECT 1")
            await session.close()
            print(f"Shard {shard_id}: Healthy")
        except Exception as e:
            print(f"Shard {shard_id}: Unhealthy - {e}")
```

### Metrics to Monitor

- **Per-Shard Metrics**:
  - Query latency
  - Connection pool usage
  - Disk space
  - Query rate
  - Error rate

- **Cross-Shard Metrics**:
  - Data distribution balance
  - Cross-shard query frequency
  - Rebalancing operations

## Best Practices

### DO:
- ✅ Use shard key in WHERE clauses when possible
- ✅ Minimize cross-shard queries
- ✅ Cache frequently accessed data
- ✅ Monitor shard balance
- ✅ Plan for shard rebalancing

### DON'T:
- ❌ Use JOINs across shards
- ❌ Use transactions across shards
- ❌ Hardcode shard IDs
- ❌ Ignore data skew
- ❌ Forget to backup all shards

## Performance Benefits

### Before Sharding (Single DB)
- **Max Throughput**: ~1,000 queries/sec
- **Storage Limit**: 1TB
- **Scaling**: Vertical only

### After Sharding (3 Shards)
- **Max Throughput**: ~3,000 queries/sec
- **Storage Limit**: 3TB
- **Scaling**: Horizontal + Vertical

### Projected (10 Shards)
- **Max Throughput**: ~10,000 queries/sec
- **Storage Limit**: 10TB
- **Scaling**: Near-linear

## Troubleshooting

### Issue: Unbalanced Shards

**Symptom**: One shard has significantly more data

**Solution**:
```python
# Rebalance by migrating data
from core.sharding import get_shard_manager

manager = get_shard_manager()
# Implement rebalancing logic
```

### Issue: Cross-Shard Query Slow

**Symptom**: Queries searching all shards are slow

**Solution**:
- Add caching layer
- Use read replicas
- Denormalize data for common queries

### Issue: Shard Connection Failed

**Symptom**: Cannot connect to specific shard

**Solution**:
1. Check database server status
2. Verify connection string
3. Check firewall rules
4. Review connection pool settings

## Future Enhancements

- [ ] Automatic shard rebalancing
- [ ] Dynamic shard addition
- [ ] Cross-shard distributed transactions
- [ ] Shard-aware query optimizer
- [ ] Geographic routing optimization
- [ ] Multi-region active-active setup
