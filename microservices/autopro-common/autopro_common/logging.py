"""
Structured logging utilities with OpenTelemetry tracing support
"""
import json
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

# Context variable for trace/span IDs
trace_context: ContextVar[Dict[str, str]] = ContextVar("trace_context", default={})


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace context if available
        ctx = trace_context.get()
        if ctx:
            log_data.update(ctx)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def setup_logging(
    service_name: str,
    level: str = "INFO",
    json_format: bool = True
) -> None:
    """
    Setup structured logging for a service
    
    Args:
        service_name: Name of the microservice
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting (True) or simple text (False)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            f"%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Set service name in context
    trace_context.set({"service": service_name})


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_trace_context(trace_id: Optional[str] = None, span_id: Optional[str] = None) -> None:
    """
    Set trace context for distributed tracing
    
    Args:
        trace_id: Distributed trace ID
        span_id: Current span ID
    """
    ctx = trace_context.get().copy()
    if trace_id:
        ctx["trace_id"] = trace_id
    if span_id:
        ctx["span_id"] = span_id
    trace_context.set(ctx)


def log_metric(logger: logging.Logger, metric_name: str, value: float, **tags: Any) -> None:
    """
    Log a metric with structured data
    
    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        **tags: Additional tags/labels
    """
    extra = {
        "metric_name": metric_name,
        "metric_value": value,
        **tags
    }
    logger.info(f"Metric: {metric_name}={value}", extra={"extra": extra})
