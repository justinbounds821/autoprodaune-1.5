"""
Rate limiting middleware for AutoPro Daune API.

Provides in-memory rate limiting with optional Redis backend for distributed systems.
"""

import time
import hashlib
from typing import Dict, Callable
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class InMemoryRateLimiter:
    """In-memory rate limiter using sliding window."""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: str, max_requests: int, time_window: int) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        window_start = now - time_window
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < window_start:
            self.requests[key].popleft()
        
        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_remaining(self, key: str, max_requests: int, time_window: int) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - time_window
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < window_start:
            self.requests[key].popleft()
        
        return max(0, max_requests - len(self.requests[key]))

# Global rate limiter instance
_rate_limiter = InMemoryRateLimiter()

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    if hasattr(request.client, "host"):
        return request.client.host
    
    return "unknown"

def create_rate_limit_key(request: Request, identifier: str = None) -> str:
    """Create a unique key for rate limiting."""
    if identifier:
        base_key = identifier
    else:
        client_ip = get_client_ip(request)
        base_key = client_ip
    
    # Hash the key for privacy and consistent length
    return hashlib.sha256(base_key.encode()).hexdigest()[:16]

async def rate_limit_middleware(
    max_requests: int = 60,
    time_window: int = 60,
    identifier_func: Callable[[Request], str] = None
):
    """
    Rate limiting middleware factory.
    
    Args:
        max_requests: Maximum requests allowed in time window
        time_window: Time window in seconds
        identifier_func: Function to extract identifier from request
    """
    async def middleware(request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics", "/"]:
            return await call_next(request)
        
        # Create rate limit key
        if identifier_func:
            identifier = identifier_func(request)
        else:
            identifier = None
        
        rate_limit_key = create_rate_limit_key(request, identifier)
        
        # Check rate limit
        if not _rate_limiter.is_allowed(rate_limit_key, max_requests, time_window):
            remaining = _rate_limiter.get_remaining(rate_limit_key, max_requests, time_window)
            
            headers = {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time()) + time_window),
                "Retry-After": str(time_window)
            }
            
            logger.warning(f"Rate limit exceeded for key: {rate_limit_key[:8]}...")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {max_requests} per {time_window} seconds",
                    "retry_after": time_window
                },
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = _rate_limiter.get_remaining(rate_limit_key, max_requests, time_window)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + time_window)
        
        return response
    
    return middleware

# Predefined rate limiters for different endpoints
def api_rate_limiter():
    """Standard API rate limiter: 120 requests per minute."""
    return rate_limit_middleware(max_requests=120, time_window=60)

def video_generation_rate_limiter():
    """Video generation rate limiter: 5 requests per minute."""
    return rate_limit_middleware(max_requests=5, time_window=60)

def upload_rate_limiter():
    """File upload rate limiter: 10 requests per minute."""
    return rate_limit_middleware(max_requests=10, time_window=60)

def auth_rate_limiter():
    """Authentication rate limiter: 10 attempts per 5 minutes."""
    return rate_limit_middleware(max_requests=10, time_window=300)