"""
Error Handler Middleware - Middleware pentru tratarea excepțiilor globale
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import json

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handler pentru tratarea excepțiilor globale"""
    
    def __init__(self):
        self.error_stats = {
            "total_errors": 0,
            "error_types": {},
            "error_endpoints": {},
            "last_error_time": None
        }
    
    async def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Tratează excepțiile HTTP"""
        error_id = self._generate_error_id()
        
        error_details = {
            "error_id": error_id,
            "type": "HTTPException",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
        
        # Log error
        logger.error(f"HTTP Error {exc.status_code}: {exc.detail}", extra=error_details)
        
        # Update stats
        self._update_error_stats("HTTPException", str(request.url.path))
        
        # Return appropriate response
        if exc.status_code >= 500:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": "Internal Server Error",
                    "error_id": error_id,
                    "message": "A server error occurred. Please try again later.",
                    "timestamp": error_details["timestamp"]
                }
            )
        else:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "error_id": error_id,
                    "timestamp": error_details["timestamp"]
                }
            )
    
    async def handle_validation_error(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """Tratează erorile de validare"""
        error_id = self._generate_error_id()
        
        error_details = {
            "error_id": error_id,
            "type": "ValidationError",
            "status_code": 422,
            "errors": exc.errors(),
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
        
        # Log error
        logger.error(f"Validation Error: {exc.errors()}", extra=error_details)
        
        # Update stats
        self._update_error_stats("ValidationError", str(request.url.path))
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "error_id": error_id,
                "details": exc.errors(),
                "timestamp": error_details["timestamp"]
            }
        )
    
    async def handle_database_error(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Tratează erorile de bază de date"""
        error_id = self._generate_error_id()
        
        error_details = {
            "error_id": error_id,
            "type": "DatabaseError",
            "status_code": 500,
            "detail": str(exc),
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
        
        # Log error with stack trace
        logger.error(f"Database Error: {str(exc)}", extra=error_details, exc_info=True)
        
        # Update stats
        self._update_error_stats("DatabaseError", str(request.url.path))
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database Error",
                "error_id": error_id,
                "message": "A database error occurred. Please try again later.",
                "timestamp": error_details["timestamp"]
            }
        )
    
    async def handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Tratează excepțiile generale"""
        error_id = self._generate_error_id()
        
        error_details = {
            "error_id": error_id,
            "type": type(exc).__name__,
            "status_code": 500,
            "detail": str(exc),
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', None),
            "traceback": traceback.format_exc()
        }
        
        # Log error with stack trace
        logger.error(f"General Error: {str(exc)}", extra=error_details, exc_info=True)
        
        # Update stats
        self._update_error_stats(type(exc).__name__, str(request.url.path))
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "error_id": error_id,
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": error_details["timestamp"]
            }
        )
    
    async def handle_rate_limit_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Tratează erorile de rate limiting"""
        error_id = self._generate_error_id()
        
        error_details = {
            "error_id": error_id,
            "type": "RateLimitError",
            "status_code": 429,
            "detail": str(exc),
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
        
        # Log error
        logger.warning(f"Rate Limit Exceeded: {str(exc)}", extra=error_details)
        
        # Update stats
        self._update_error_stats("RateLimitError", str(request.url.path))
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate Limit Exceeded",
                "error_id": error_id,
                "message": "Too many requests. Please try again later.",
                "retry_after": 60,
                "timestamp": error_details["timestamp"]
            }
        )
    
    async def handle_timeout_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Tratează erorile de timeout"""
        error_id = self._generate_error_id()
        
        error_details = {
            "error_id": error_id,
            "type": "TimeoutError",
            "status_code": 504,
            "detail": str(exc),
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', None)
        }
        
        # Log error
        logger.error(f"Timeout Error: {str(exc)}", extra=error_details)
        
        # Update stats
        self._update_error_stats("TimeoutError", str(request.url.path))
        
        return JSONResponse(
            status_code=504,
            content={
                "error": "Request Timeout",
                "error_id": error_id,
                "message": "The request took too long to process. Please try again.",
                "timestamp": error_details["timestamp"]
            }
        )
    
    def _generate_error_id(self) -> str:
        """Generează un ID unic pentru eroare"""
        timestamp = int(time.time() * 1000)
        return f"ERR_{timestamp}"
    
    def _update_error_stats(self, error_type: str, endpoint: str):
        """Actualizează statisticile de erori"""
        self.error_stats["total_errors"] += 1
        self.error_stats["last_error_time"] = datetime.now().isoformat()
        
        # Update error types
        if error_type not in self.error_stats["error_types"]:
            self.error_stats["error_types"][error_type] = 0
        self.error_stats["error_types"][error_type] += 1
        
        # Update error endpoints
        if endpoint not in self.error_stats["error_endpoints"]:
            self.error_stats["error_endpoints"][endpoint] = 0
        self.error_stats["error_endpoints"][endpoint] += 1
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Returnează statisticile de erori"""
        return self.error_stats
    
    def reset_error_stats(self):
        """Resetează statisticile de erori"""
        self.error_stats = {
            "total_errors": 0,
            "error_types": {},
            "error_endpoints": {},
            "last_error_time": None
        }

# Singleton instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Returnează instanța singleton a ErrorHandler"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

# Exception handlers pentru FastAPI
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler pentru excepțiile HTTP"""
    handler = get_error_handler()
    return await handler.handle_http_exception(request, exc)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler pentru erorile de validare"""
    handler = get_error_handler()
    return await handler.handle_validation_error(request, exc)

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler pentru erorile de bază de date"""
    handler = get_error_handler()
    return await handler.handle_database_error(request, exc)

async def general_exception_handler(request: Request, exc: Exception):
    """Handler pentru excepțiile generale"""
    handler = get_error_handler()
    return await handler.handle_general_exception(request, exc)

async def rate_limit_exception_handler(request: Request, exc: Exception):
    """Handler pentru erorile de rate limiting"""
    handler = get_error_handler()
    return await handler.handle_rate_limit_error(request, exc)

async def timeout_exception_handler(request: Request, exc: Exception):
    """Handler pentru erorile de timeout"""
    handler = get_error_handler()
    return await handler.handle_timeout_error(request, exc)
