"""
Production Security & Observability Middleware for NutriScan.
Includes:
1. SecurityHeadersMiddleware: Enforces OWASP-recommended HTTP response security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy).
2. CorrelationIdMiddleware: Guarantees every HTTP transaction carries an X-Correlation-ID for end-to-end clinical traceability and audit logs.
"""

import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable for thread-safe/async-safe correlation ID propagation
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def get_current_correlation_id() -> str:
    """Returns the current request's correlation ID or generates a fallback."""
    cid = correlation_id_ctx.get()
    return cid if cid else str(uuid.uuid4())


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies strict enterprise security headers to protect against
    Clickjacking, MIME confusion, XSS, and unauthorized framing.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # 1. Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 2. Prevent clickjacking / frame embedding
        response.headers["X-Frame-Options"] = "DENY"
        
        # 3. HTTP Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 4. Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-ancestors 'none'; "
            "object-src 'none';"
        )
        
        # 5. Referrer Policy & Permissions
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Extracts or generates an X-Correlation-ID for every incoming request,
    attaches it to context, and echoes it in the outgoing HTTP response.
    """
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        token = correlation_id_ctx.set(req_id)
        try:
            response: Response = await call_next(request)
            response.headers["X-Correlation-ID"] = req_id
            return response
        finally:
            correlation_id_ctx.reset(token)
