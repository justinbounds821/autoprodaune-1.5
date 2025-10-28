"""
Redis cache utilities with async support
"""
import json
import os
from typing import Any, Optional, Union
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

from .logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Async Redis cache manager"""

    def __init__(
        self,
        redis_url: str,
        max_connections: int = 50,
        decode_responses: bool = True,
    ):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL (redis://host:port/db)
            max_connections: Maximum connections in pool
            decode_responses: Automatically decode responses to strings
        """
        self.redis_url = redis_url
        
        # Create connection pool
        self.pool = ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            decode_responses=decode_responses,
        )
        
        # Create Redis client
        self.redis = Redis(connection_pool=self.pool)
        
        logger.info(f"Redis cache initialized: {redis_url}")

    async def ping(self) -> bool:
        """
        Test Redis connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self.redis.ping()
            logger.info("Redis connection test successful")
            return True
        except RedisError as e:
            logger.error(f"Redis connection test failed: {e}")
            return False

    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized if dict/list)
            ttl: Time to live in seconds (None = no expiration)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize complex types to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)
            
            return True
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """
        Delete keys from cache
        
        Args:
            *keys: Cache keys to delete
            
        Returns:
            Number of keys deleted
        """
        try:
            return await self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0

    async def exists(self, *keys: str) -> int:
        """
        Check if keys exist
        
        Args:
            *keys: Cache keys to check
            
        Returns:
            Number of existing keys
        """
        try:
            return await self.redis.exists(*keys)
        except RedisError as e:
            logger.error(f"Redis EXISTS error: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter
        
        Args:
            key: Counter key
            amount: Amount to increment
            
        Returns:
            New value or None on error
        """
        try:
            return await self.redis.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration on a key
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.redis.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    async def flush_all(self) -> bool:
        """
        Flush all keys (USE WITH CAUTION!)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.redis.flushall()
            logger.warning("Redis cache flushed (all keys deleted)")
            return True
        except RedisError as e:
            logger.error(f"Redis FLUSHALL error: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection"""
        await self.redis.close()
        await self.pool.disconnect()
        logger.info("Redis connection closed")


# Global Redis instance
_redis_instance: Optional[RedisCache] = None


def init_redis(redis_url: Optional[str] = None, **kwargs) -> RedisCache:
    """
    Initialize global Redis instance
    
    Args:
        redis_url: Redis URL (defaults to REDIS_URL env var)
        **kwargs: Additional arguments for RedisCache
        
    Returns:
        Initialized RedisCache instance
    """
    global _redis_instance
    
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    _redis_instance = RedisCache(redis_url, **kwargs)
    return _redis_instance


def get_redis() -> RedisCache:
    """
    Get global Redis instance
    
    Returns:
        RedisCache instance
        
    Raises:
        RuntimeError: If Redis not initialized
    """
    if _redis_instance is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_instance
