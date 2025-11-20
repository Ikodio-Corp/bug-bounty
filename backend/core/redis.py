"""
Redis configuration and connection management
"""

import redis.asyncio as aioredis
from redis import Redis
import logging
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)

# Global Redis clients
redis_client: Optional[Redis] = None
async_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> Redis:
    """
    Get synchronous Redis client
    """
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50
        )
    return redis_client


async def get_async_redis() -> aioredis.Redis:
    """
    Get asynchronous Redis client
    """
    global async_redis_client
    if async_redis_client is None:
        async_redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50
        )
    return async_redis_client


async def init_redis():
    """
    Initialize Redis connections
    """
    try:
        await get_async_redis()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {str(e)}")
        raise


async def close_redis():
    """
    Close Redis connections
    """
    global redis_client, async_redis_client
    try:
        if redis_client:
            redis_client.close()
        if async_redis_client:
            await async_redis_client.close()
        logger.info("Redis connections closed")
    except Exception as e:
        logger.error(f"Error closing Redis: {str(e)}")


class RedisCache:
    """
    Redis caching utilities
    """
    
    @staticmethod
    async def get(key: str) -> Optional[str]:
        """Get value from cache"""
        client = await get_async_redis()
        return await client.get(key)
    
    @staticmethod
    async def set(key: str, value: str, expire: int = 3600):
        """Set value in cache with expiration"""
        client = await get_async_redis()
        await client.set(key, value, ex=expire)
    
    @staticmethod
    async def delete(key: str):
        """Delete key from cache"""
        client = await get_async_redis()
        await client.delete(key)
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists"""
        client = await get_async_redis()
        return await client.exists(key)
    
    @staticmethod
    async def increment(key: str, amount: int = 1) -> int:
        """Increment counter"""
        client = await get_async_redis()
        return await client.incrby(key, amount)
    
    @staticmethod
    async def expire(key: str, seconds: int):
        """Set expiration on key"""
        client = await get_async_redis()
        await client.expire(key, seconds)
