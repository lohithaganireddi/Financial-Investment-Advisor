"""
Rate Limiter Service Module

Provides in-memory rate limiting and brute-force protection for sensitive API endpoints.
Tracks client IP request frequencies using a sliding window algorithm with thread safety.
"""

import time
import threading
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException


class RateLimiter:
    """
    Thread-safe sliding-window rate limiter.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Storage: dict mapping (ip, route_key) -> list of timestamp floats
        self._hits: Dict[Tuple[str, str], List[float]] = {}
        # Route limits: route_key -> (max_requests, window_seconds)
        self._rules: Dict[str, Tuple[int, int]] = {
            "auth:login": (5, 60),      # 5 attempts per 60s
            "auth:register": (10, 60),  # 10 attempts per 60s
            "auth:refresh": (30, 60),   # 30 requests per 60s
        }

    def reset(self):
        """Reset all rate limit counters (used in testing)."""
        with self._lock:
            self._hits.clear()

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from Request, handling proxy headers."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def check(self, request: Request, route_key: str):
        """
        Check rate limit for a request on a route_key.
        Raises HTTP 429 with Retry-After header if limit exceeded.
        """
        if route_key not in self._rules:
            return

        max_reqs, window_sec = self._rules[route_key]
        ip = self.get_client_ip(request)
        now = time.time()
        window_start = now - window_sec

        with self._lock:
            key = (ip, route_key)
            timestamps = self._hits.get(key, [])
            # Filter timestamps within current window
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= max_reqs:
                oldest = valid_timestamps[0]
                retry_after = max(1, int(oldest + window_sec - now))
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(retry_after)}
                )

            valid_timestamps.append(now)
            self._hits[key] = valid_timestamps


limiter = RateLimiter()
