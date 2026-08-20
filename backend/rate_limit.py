"""
A small in-memory rate limiter — no Redis needed for a project this size.
Tracks request timestamps per IP in a sliding window.
"""

import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, window_seconds: int, max_requests: int):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        recent = [t for t in self.hits[key] if t > cutoff]
        recent.append(now)
        self.hits[key] = recent
        return len(recent) <= self.max_requests


# 10 login attempts per 15 minutes, 300 general API calls per minute — per IP
login_limiter = RateLimiter(window_seconds=15 * 60, max_requests=10)
api_limiter = RateLimiter(window_seconds=60, max_requests=300)
