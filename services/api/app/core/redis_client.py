"""
Redis client management for AutoPro Daune API.

This module provides Redis connection management with connection pooling,
health checks, and graceful fallback handling.
"""
import asyncio
import logging
from functools import lru_cache
from typing import Optional, Any, Dict, Union
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

from .config import get_settings

log = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper with connection management and health checks."""
    
    def __init__(self, redis_url: str):
        """Initialize Redis client with connection URL."""
        self.redis_url = redis_url
        self._client: Optional[Redis] = None
        self._connection_pool = None
        
    async def connect(self) -> bool:
        """Establish Redis connection."""
        try:
            # Create connection pool
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Create Redis client
            self._client = Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._client.ping()
            log.info("✅ Redis connection established")
            return True
            
        except Exception as e:
            log.error(f"❌ Redis connection failed: {e}")
            self._client = None
            self._connection_pool = None
            return False
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None
        log.info("✅ Redis connection closed")
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        if not self._client:
            return False
        
        try:
            await self._client.ping()
            return True
        except (ConnectionError, TimeoutError):
            log.warning("⚠️ Redis health check failed")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self._client:
            return None
        
        try:
            value = await self._client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            log.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """Set key-value pair with optional expiration."""
        if not self._client:
            return False
        
        try:
            result = await self._client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)
        except Exception as e:
            log.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        if not self._client:
            return 0
        
        try:
            return await self._client.delete(*keys)
        except Exception as e:
            log.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        if not self._client:
            return 0
        
        try:
            return await self._client.exists(*keys)
        except Exception as e:
            log.error(f"Redis EXISTS error for keys {keys}: {e}")
            return 0
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment key value."""
        if not self._client:
            return None
        
        try:
            return await self._client.incr(key, amount)
        except Exception as e:
            log.error(f"Redis INCR error for key '{key}': {e}")
            return None
    
    async def expire(self, key: str, time: int) -> bool:
        """Set key expiration time."""
        if not self._client:
            return False
        
        try:
            return await self._client.expire(key, time)
        except Exception as e:
            log.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value."""
        if not self._client:
            return None
        
        try:
            value = await self._client.hget(name, key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            log.error(f"Redis HGET error for hash '{name}', key '{key}': {e}")
            return None
    
    async def hset(self, name: str, key: str, value: str) -> bool:
        """Set hash field value."""
        if not self._client:
            return False
        
        try:
            result = await self._client.hset(name, key, value)
            return bool(result)
        except Exception as e:
            log.error(f"Redis HSET error for hash '{name}', key '{key}': {e}")
            return False
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Get all hash fields."""
        if not self._client:
            return {}
        
        try:
            result = await self._client.hgetall(name)
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in result.items()}
        except Exception as e:
            log.error(f"Redis HGETALL error for hash '{name}': {e}")
            return {}
    
    @asynccontextmanager
    async def pipeline(self):
        """Create Redis pipeline context manager."""
        if not self._client:
            yield None
            return
        
        pipe = self._client.pipeline()
        try:
            yield pipe
        finally:
            await pipe.reset()


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def init_redis() -> RedisClient:
    """Initialize Redis client."""
    global _redis_client
    
    if _redis_client is None:
        settings = get_settings()
        _redis_client = RedisClient(settings.REDIS_URL)
        await _redis_client.connect()
    
    return _redis_client


@lru_cache()
def get_redis() -> RedisClient:
    """Get Redis client instance (synchronous version for dependency injection)."""
    global _redis_client
    
    if _redis_client is None:
        settings = get_settings()
        _redis_client = RedisClient(settings.REDIS_URL)
        # Note: Connection will be established on first use
    
    return _redis_client


async def get_redis_async() -> RedisClient:
    """Get Redis client instance (async version)."""
    return await init_redis()


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None