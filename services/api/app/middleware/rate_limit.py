"""
Rate limiting middleware for AutoPro Daune API.
"""

import time
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# In-memory storage for rate limiting (in production, use Redis)
rate_limit_storage: Dict[str, Dict[str, float]] = {}

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 5, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier (IP address or user ID)
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        # Clean old entries
        if client_id in rate_limit_storage:
            rate_limit_storage[client_id] = {
                timestamp: timestamp 
                for timestamp in rate_limit_storage[client_id].values()
                if current_time - timestamp < self.time_window
            }
        else:
            rate_limit_storage[client_id] = {}
        
        # Check if limit exceeded
        if len(rate_limit_storage[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        rate_limit_storage[client_id][str(current_time)] = current_time
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        current_time = time.time()
        
        if client_id not in rate_limit_storage:
            return self.max_requests
        
        # Clean old entries
        rate_limit_storage[client_id] = {
            timestamp: timestamp 
            for timestamp in rate_limit_storage[client_id].values()
            if current_time - timestamp < self.time_window
        }
        
        return max(0, self.max_requests - len(rate_limit_storage[client_id]))

def get_client_id(request: Request) -> str:
    """
    Get client identifier from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client identifier (IP address)
    """
    # Try to get real IP from headers (for reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"

def rate_limit_middleware(max_requests: int = 5, time_window: int = 60):
    """
    Create rate limiting middleware.
    
    Args:
        max_requests: Maximum requests per time window
        time_window: Time window in seconds
        
    Returns:
        Middleware function
    """
    limiter = RateLimiter(max_requests, time_window)
    
    async def middleware(request: Request, call_next):
        # Only apply rate limiting to video generation endpoint
        if request.url.path == "/api/video/generate" and request.method == "POST":
            client_id = get_client_id(request)
            
            if not limiter.is_allowed(client_id):
                remaining = limiter.get_remaining_requests(client_id)
                logging.warning(f"Rate limit exceeded for client {client_id}")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {max_requests} requests per {time_window} seconds",
                        "retry_after": time_window,
                        "remaining_requests": remaining
                    },
                    headers={
                        "Retry-After": str(time_window),
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(time.time() + time_window))
                    }
                )
        
        response = await call_next(request)
        return response
    
    return middleware
