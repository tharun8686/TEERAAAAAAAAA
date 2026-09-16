"""
TerraEdge — Phase 8 Security & Role-Based Access Control (RBAC).
Provides lightweight token authentication, role validation (OPERATOR, ADMIN),
in-memory rate limiting, and request size protection.
"""

from __future__ import annotations
from enum import Enum
import time
from typing import Dict, List, Optional
from collections import defaultdict

from fastapi import Depends, HTTPException, Header, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import (
    ADMIN_TOKEN,
    OPERATOR_TOKEN,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_REQUESTS_PER_MIN,
    REQUEST_MAX_SIZE_BYTES,
    SENSOR_TOKEN,
    TERRAEDGE_ENV,
)


class Role(str, Enum):
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"
    SENSOR = "SENSOR"


# Bearer token security scheme (auto_error=False to allow fallback to X-API-Key header)
bearer_scheme = HTTPBearer(auto_error=False)


def get_token_from_request(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> Optional[str]:
    """Extracts authentication token from either X-API-Key header or Bearer authorization."""
    if x_api_key:
        return x_api_key.strip()
    if auth_credentials and auth_credentials.credentials:
        return auth_credentials.credentials.strip()
    return None


def get_current_user_role(token: Optional[str] = Depends(get_token_from_request)) -> Optional[Role]:
    """Resolves caller role from presented token."""
    if not token:
        return None

    if token == ADMIN_TOKEN:
        return Role.ADMIN
    if token == OPERATOR_TOKEN:
        return Role.OPERATOR
    if token == SENSOR_TOKEN:
        return Role.SENSOR
    return None


def require_role(required_role: Role):
    """
    FastAPI dependency factory enforcing role requirements.
    Admin role inherits Operator privileges.
    In development/test mode without an explicit token, requests are permitted with a dev notice,
    preserving backward compatibility for Phase 1-7 test suites.
    When an invalid token is provided or when in PRODUCTION / STRICT mode, authentication is enforced strictly.
    """
    def _role_checker(
        token: Optional[str] = Depends(get_token_from_request),
        user_role: Optional[Role] = Depends(get_current_user_role),
    ) -> Role:
        import os
        strict_mode = (
            TERRAEDGE_ENV == "production"
            or os.getenv("TERRAEDGE_STRICT_AUTH", "false").lower() == "true"
        )

        if not token:
            if strict_mode:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication credentials required (X-API-Key or Bearer token)",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Permissive dev/test fallback
            return Role.ADMIN

        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Admin has access to everything
        if user_role == Role.ADMIN:
            return user_role

        # Operator satisfies Operator role
        if required_role == Role.OPERATOR and user_role == Role.OPERATOR:
            return user_role

        # Otherwise insufficient permissions
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {required_role.value}, current role: {user_role.value}",
        )

    return _role_checker


# Convenient role dependency helpers
require_admin = require_role(Role.ADMIN)
require_operator = require_role(Role.OPERATOR)


# ============================================================================
# In-Memory Rate Limiter
# ============================================================================

class InMemoryRateLimiter:
    """Sliding-window request rate limiter per client IP."""
    def __init__(self, requests_per_minute: int = RATE_LIMIT_REQUESTS_PER_MIN, enabled: bool = RATE_LIMIT_ENABLED):
        self.limit = requests_per_minute
        self.enabled = enabled
        self._history: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        if not self.enabled:
            return True

        now = time.time()
        window_start = now - 60.0

        # Purge entries older than 60s
        timestamps = [t for t in self._history[client_id] if t > window_start]
        self._history[client_id] = timestamps

        if len(timestamps) >= self.limit:
            return False

        self._history[client_id].append(now)
        return True

    def check_rate_limit(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please throttle requests.",
                headers={"Retry-After": "60"},
            )


rate_limiter = InMemoryRateLimiter()


# ============================================================================
# Request Size Limiter Middleware
# ============================================================================

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejects HTTP request payloads larger than configured maximum byte size."""
    def __init__(self, app, max_size_bytes: int = REQUEST_MAX_SIZE_BYTES):
        super().__init__(app)
        self.max_size_bytes = max_size_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_size_bytes:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": "Payload Too Large",
                            "detail": f"Request body size exceeds maximum limit of {self.max_size_bytes} bytes",
                        },
                    )
            except ValueError:
                pass

        return await call_next(request)
