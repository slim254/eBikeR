import structlog
from typing import Any, Dict, Optional
from rest_framework.request import Request

# Configure structlog to work with django-structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request_info(request: Request, action: str, **kwargs) -> Dict[str, Any]:
    """Extract and log request information."""
    user_id = request.user.id if request.user.is_authenticated else None
    user_email = request.user.email if request.user.is_authenticated else None

    log_data = {
        "action": action,
        "method": request.method,
        "path": request.path,
        "user_id": user_id,
        "user_email": user_email,
        "ip_address": _get_client_ip(request),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        **kwargs,
    }

    return log_data


def _get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def log_api_request(
    logger: structlog.BoundLogger, request: Request, action: str, **kwargs
):
    """Log API request with structured data."""
    log_data = log_request_info(request, action, **kwargs)
    logger.info("API Request", **log_data)


def log_api_response(
    logger: structlog.BoundLogger,
    request: Request,
    action: str,
    status_code: int,
    **kwargs,
):
    """Log API response with structured data."""
    log_data = log_request_info(request, action, status_code=status_code, **kwargs)
    logger.info("API Response", **log_data)


def log_api_error(
    logger: structlog.BoundLogger,
    request: Request,
    action: str,
    error: Exception,
    **kwargs,
):
    """Log API error with structured data."""
    log_data = log_request_info(
        request, action, error=str(error), error_type=type(error).__name__, **kwargs
    )
    logger.error("API Error", **log_data)


def log_user_action(
    logger: structlog.BoundLogger,
    request: Request,
    action: str,
    resource_id: Optional[str] = None,
    **kwargs,
):
    """Log user actions for audit trail."""
    log_data = log_request_info(request, action, resource_id=resource_id, **kwargs)
    logger.info("User Action", **log_data)


def log_business_event(logger: structlog.BoundLogger, event: str, **kwargs):
    """Log business events."""
    logger.info("Business Event", event_name=event, **kwargs)
