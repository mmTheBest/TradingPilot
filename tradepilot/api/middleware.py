from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from tradepilot.config import settings


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.max_request_bytes:
                    return Response(status_code=413, content="request too large")
            except ValueError:
                return Response(status_code=400, content="invalid content-length")
        return await call_next(request)


@dataclass
class RateLimiter:
    window_seconds: int
    max_requests: int
    buckets: dict[str, tuple[datetime, int]] = field(default_factory=dict)

    def allow(self, key: str) -> bool:
        now = datetime.now(tz=timezone.utc)
        window_start, count = self.buckets.get(key, (now, 0))
        if now - window_start > timedelta(seconds=self.window_seconds):
            window_start = now
            count = 0
        count += 1
        self.buckets[key] = (window_start, count)
        return count <= self.max_requests


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.limiter = RateLimiter(window_seconds=60, max_requests=settings.rate_limit_per_minute)

    async def dispatch(self, request: Request, call_next: Callable):
        client = request.client.host if request.client else "unknown"
        if not self.limiter.allow(client):
            return Response(status_code=429, content="rate limit exceeded")
        return await call_next(request)
