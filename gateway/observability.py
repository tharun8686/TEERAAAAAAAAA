"""
TerraEdge — Phase 8 Observability, Structured JSON Logging & Request Correlation.
Provides centralized request tracking (X-Request-ID), context propagation,
and sanitized structured logging without credential leakage.
"""

from __future__ import annotations
import contextvars
import datetime
import json
import logging
import sys
import uuid
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import GATEWAY_ID, LOG_LEVEL

# Context variable for tracing current request ID across async tasks
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)

# Sensitive keys that must NEVER be logged in plaintext
SENSITIVE_KEYS = {
    "password", "token", "secret", "api_key", "service_key",
    "auth", "authorization", "key", "access_token", "jwt",
}


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively masks sensitive keys from log payloads."""
    sanitized = {}
    for k, v in data.items():
        if any(sens in k.lower() for sens in SENSITIVE_KEYS):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_dict(v)
        elif isinstance(v, list):
            sanitized[k] = [sanitize_dict(item) if isinstance(item, dict) else item for item in v]
        else:
            sanitized[k] = v
    return sanitized


class StructuredLogger:
    """JSON structured event logger for edge gateway operations."""
    def __init__(self, name: str = "terraedge"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        # Attach console stream handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
            self.logger.addHandler(handler)

    def log(
        self,
        level: str,
        event: str,
        component: str = "gateway",
        node_id: Optional[str] = None,
        hazard: Optional[str] = None,
        alert_id: Optional[str] = None,
        latency_ms: Optional[float] = None,
        **extra: Any,
    ) -> None:
        req_id = request_id_ctx.get() or extra.pop("request_id", None)

        record = {
            "timestamp": _utc_now_iso(),
            "level": level.upper(),
            "component": component,
            "event": event,
            "gateway_id": GATEWAY_ID,
        }

        if req_id:
            record["request_id"] = req_id
        if node_id:
            record["node_id"] = node_id
        if hazard:
            record["hazard"] = hazard
        if alert_id:
            record["alert_id"] = alert_id
        if latency_ms is not None:
            record["latency_ms"] = round(latency_ms, 2)

        if extra:
            clean_extra = sanitize_dict(extra)
            record.update(clean_extra)

        msg = json.dumps(record, default=str)
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(msg)

    def info(self, event: str, **kwargs):
        self.log("INFO", event, **kwargs)

    def warning(self, event: str, **kwargs):
        self.log("WARNING", event, **kwargs)

    def error(self, event: str, **kwargs):
        self.log("ERROR", event, **kwargs)

    def debug(self, event: str, **kwargs):
        self.log("DEBUG", event, **kwargs)


# Global structured logger singleton
logger = StructuredLogger()


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that captures or generates X-Request-ID
    and propagates it into context and response headers.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        req_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:12].upper()}"
        request.state.request_id = req_id
        token = request_id_ctx.set(req_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_ctx.reset(token)
