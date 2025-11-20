"""
Database Sharding Strategy for IKODIO BugBounty Platform
Implements horizontal database partitioning for scalability
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings


class ShardStrategy(Enum):
    """Sharding strategies"""
    HASH = "hash"
    RANGE = "range"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"


class DatabaseShardManager:
    """
    Manages database sharding for horizontal scaling
    
    Sharding Keys:
    - Users: user_id (hash-based)
    - Bugs: bug_id (hash-based)
    - Scans: scan_id (hash-based)
    - Geographic data: region (geographic)
    """
    
    def __init__(self, shard_configs: List[Dict[str, Any]]):
        """
        Initialize shard manager
        
        Args:
            shard_configs: List of shard configurations
            Example:
            [
                {"id": 0, "url": "postgresql://...", "weight": 1},
                {"id": 1, "url": "postgresql://...", "weight": 1},
                {"id": 2, "url": "postgresql://...", "weight": 1}
            ]
        """
        self.shards = {}
        self.shard_weights = {}
        self.total_weight = 0
        
        for config in shard_configs:
            shard_id = config["id"]
            self.shards[shard_id] = {
                "engine": create_async_engine(config["url"], pool_pre_ping=True),
                "session_maker": sessionmaker(
                    bind=create_async_engine(config["url"]),
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            }
            weight = config.get("weight", 1)
            self.shard_weights[shard_id] = weight
            self.total_weight += weight
        
        self.num_shards = len(self.shards)
    
    def get_shard_id_by_hash(self, key: Any) -> int:
        """
        Determine shard ID using consistent hashing
        
        Args:
            key: Sharding key (user_id, bug_id, etc.)
        
        Returns:
            Shard ID
        """
        key_str = str(key)
        hash_value = int(hashlib.md5(key_str.encode()).hexdigest(), 16)
        return hash_value % self.num_shards
    
    def get_shard_id_by_range(self, key: int, ranges: List[tuple]) -> int:
        """
        Determine shard ID using range-based partitioning
        
        Args:
            key: Numeric key
            ranges: List of (min, max, shard_id) tuples
        
        Returns:
            Shard ID
        """
        for min_val, max_val, shard_id in ranges:
            if min_val <= key < max_val:
                return shard_id
        
        # Default to last shard if out of range
        return ranges[-1][2]
    
    def get_shard_id_by_geography(self, region: str) -> int:
        """
        Determine shard ID based on geographic region
        
        Args:
            region: Geographic region code (US, EU, ASIA, etc.)
        
        Returns:
            Shard ID
        """
        region_mapping = {
            "US": 0,
            "EU": 1,
            "ASIA": 2,
            "default": 0
        }
        return region_mapping.get(region.upper(), region_mapping["default"])
    
    async def get_session(self, shard_id: int) -> AsyncSession:
        """
        Get database session for specific shard
        
        Args:
            shard_id: Shard identifier
        
        Returns:
            AsyncSession for the shard
        """
        if shard_id not in self.shards:
            raise ValueError(f"Shard {shard_id} not found")
        
        session_maker = self.shards[shard_id]["session_maker"]
        return session_maker()
    
    async def get_session_by_key(
        self,
        key: Any,
        strategy: ShardStrategy = ShardStrategy.HASH
    ) -> AsyncSession:
        """
        Get database session based on sharding key and strategy
        
        Args:
            key: Sharding key
            strategy: Sharding strategy to use
        
        Returns:
            AsyncSession for appropriate shard
        """
        if strategy == ShardStrategy.HASH:
            shard_id = self.get_shard_id_by_hash(key)
        elif strategy == ShardStrategy.GEOGRAPHIC:
            shard_id = self.get_shard_id_by_geography(key)
        else:
            # Default to hash
            shard_id = self.get_shard_id_by_hash(key)
        
        return await self.get_session(shard_id)
    
    async def execute_on_all_shards(self, query_func, *args, **kwargs) -> List[Any]:
        """
        Execute query on all shards (for aggregation, search, etc.)
        
        Args:
            query_func: Async function to execute
            *args, **kwargs: Arguments for query function
        
        Returns:
            List of results from all shards
        """
        results = []
        
        for shard_id in self.shards.keys():
            session = await self.get_session(shard_id)
            try:
                result = await query_func(session, *args, **kwargs)
                results.append(result)
            finally:
                await session.close()
        
        return results
    
    async def close_all(self):
        """Close all shard connections"""
        for shard in self.shards.values():
            await shard["engine"].dispose()


class ShardedRepository:
    """
    Base repository with sharding support
    Example usage for any model
    """
    
    def __init__(self, shard_manager: DatabaseShardManager):
        self.shard_manager = shard_manager
    
    async def get_by_id(self, model_class, item_id: int):
        """Get item by ID from appropriate shard"""
        session = await self.shard_manager.get_session_by_key(item_id)
        try:
            result = await session.get(model_class, item_id)
            return result
        finally:
            await session.close()
    
    async def create(self, model_class, item_id: int, **kwargs):
        """Create item in appropriate shard"""
        session = await self.shard_manager.get_session_by_key(item_id)
        try:
            instance = model_class(id=item_id, **kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance
        finally:
            await session.close()
    
    async def update(self, model_class, item_id: int, **kwargs):
        """Update item in appropriate shard"""
        session = await self.shard_manager.get_session_by_key(item_id)
        try:
            instance = await session.get(model_class, item_id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                await session.refresh(instance)
            return instance
        finally:
            await session.close()
    
    async def delete(self, model_class, item_id: int):
        """Delete item from appropriate shard"""
        session = await self.shard_manager.get_session_by_key(item_id)
        try:
            instance = await session.get(model_class, item_id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
        finally:
            await session.close()
    
    async def search_all_shards(self, query_func, *args, **kwargs):
        """Search across all shards and aggregate results"""
        results = await self.shard_manager.execute_on_all_shards(
            query_func, *args, **kwargs
        )
        
        # Flatten results
        all_items = []
        for shard_results in results:
            if isinstance(shard_results, list):
                all_items.extend(shard_results)
            elif shard_results:
                all_items.append(shard_results)
        
        return all_items


# Example shard configuration
SHARD_CONFIGS = [
    {
        "id": 0,
        "url": settings.DATABASE_URL_SHARD_0,
        "weight": 1,
        "description": "Primary shard - US East"
    },
    {
        "id": 1,
        "url": settings.DATABASE_URL_SHARD_1,
        "weight": 1,
        "description": "Secondary shard - US West"
    },
    {
        "id": 2,
        "url": settings.DATABASE_URL_SHARD_2,
        "weight": 1,
        "description": "Tertiary shard - EU"
    }
]


# Global shard manager instance
_shard_manager: Optional[DatabaseShardManager] = None


def get_shard_manager() -> DatabaseShardManager:
    """Get global shard manager instance"""
    global _shard_manager
    
    if _shard_manager is None:
        # Initialize with shard configs from settings
        if hasattr(settings, 'ENABLE_SHARDING') and settings.ENABLE_SHARDING:
            _shard_manager = DatabaseShardManager(SHARD_CONFIGS)
        else:
            # Single shard mode (no sharding)
            _shard_manager = DatabaseShardManager([{
                "id": 0,
                "url": settings.DATABASE_URL,
                "weight": 1
            }])
    
    return _shard_manager


async def initialize_shards():
    """Initialize all database shards"""
    manager = get_shard_manager()
    
    # Test connections to all shards
    for shard_id in manager.shards.keys():
        try:
            session = await manager.get_session(shard_id)
            await session.close()
            print(f"Shard {shard_id} initialized successfully")
        except Exception as e:
            print(f"Failed to initialize shard {shard_id}: {e}")
            raise


async def close_shards():
    """Close all shard connections"""
    manager = get_shard_manager()
    await manager.close_all()


# Example usage in services
class ShardedBugService:
    """Bug service with sharding support"""
    
    def __init__(self):
        self.shard_manager = get_shard_manager()
        self.repository = ShardedRepository(self.shard_manager)
    
    async def get_bug(self, bug_id: int):
        """Get bug from appropriate shard"""
        from models.bug import Bug
        return await self.repository.get_by_id(Bug, bug_id)
    
    async def create_bug(self, bug_id: int, **bug_data):
        """Create bug in appropriate shard"""
        from models.bug import Bug
        return await self.repository.create(Bug, bug_id, **bug_data)
    
    async def search_bugs(self, filters: Dict[str, Any]):
        """Search bugs across all shards"""
        from models.bug import Bug
        from sqlalchemy import select
        
        async def query_func(session, filters):
            query = select(Bug)
            for key, value in filters.items():
                query = query.where(getattr(Bug, key) == value)
            result = await session.execute(query)
            return result.scalars().all()
        
        return await self.repository.search_all_shards(query_func, filters)


class ShardedUserService:
    """User service with sharding support"""
    
    def __init__(self):
        self.shard_manager = get_shard_manager()
        self.repository = ShardedRepository(self.shard_manager)
    
    async def get_user(self, user_id: int):
        """Get user from appropriate shard"""
        from models.user import User
        return await self.repository.get_by_id(User, user_id)
    
    async def get_user_by_email(self, email: str):
        """Get user by email (requires searching all shards)"""
        from models.user import User
        from sqlalchemy import select
        
        async def query_func(session, email):
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
        results = await self.repository.search_all_shards(query_func, email)
        return next((r for r in results if r), None)
