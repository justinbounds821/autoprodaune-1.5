"""
Middleware for FastMCP Server
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing information"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        logger.info(f"→ {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[{response.status_code}] "
            f"({duration:.3f}s)"
        )

        # Add timing header
        response.headers["X-Process-Time"] = str(duration)

        return response


class OrchestratorHealthMiddleware(BaseHTTPMiddleware):
    """Check orchestrator health and add to response headers"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add orchestrator health header to all responses
        try:
            from clients.orchestrator_client import get_orchestrator_client

            orchestrator = get_orchestrator_client()
            is_healthy = orchestrator.ping()
            response.headers["X-Orchestrator-Health"] = "healthy" if is_healthy else "down"
        except Exception:
            response.headers["X-Orchestrator-Health"] = "unknown"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            # Let FastAPI's default error handler deal with it
            raise
