"""
Rate Limiter
------------
Token-budget-aware rate limiter for Anthropic API calls.
Tracks requests and estimated tokens over a rolling 60-second window.
"""

import time
from collections import deque
from threading import Lock
from typing import Deque, Tuple


class RateLimiter:
    def __init__(self, requests_per_minute: int = 50, tokens_per_minute: int = 40_000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute   = tokens_per_minute
        self._request_times: Deque[float]          = deque()
        self._token_log:     Deque[Tuple[float, int]] = deque()
        self._lock = Lock()

    def _evict_old(self) -> None:
        cutoff = time.monotonic() - 60.0
        while self._request_times and self._request_times[0] < cutoff:
            self._request_times.popleft()
        while self._token_log and self._token_log[0][0] < cutoff:
            self._token_log.popleft()

    def _try_acquire(self, estimated_tokens: int) -> bool:
        self._evict_old()
        if len(self._request_times) >= self.requests_per_minute:
            return False
        if sum(t for _, t in self._token_log) + estimated_tokens > self.tokens_per_minute:
            return False
        now = time.monotonic()
        self._request_times.append(now)
        self._token_log.append((now, estimated_tokens))
        return True

    def wait_if_needed(self, estimated_tokens: int = 1_000, poll_interval: float = 0.5) -> None:
        """Block until a request slot is available."""
        with self._lock:
            while not self._try_acquire(estimated_tokens):
                time.sleep(poll_interval)
                self._evict_old()

    def get_usage(self) -> dict:
        with self._lock:
            self._evict_old()
            tokens_used = sum(t for _, t in self._token_log)
            return {
                "requests_used":    len(self._request_times),
                "requests_limit":   self.requests_per_minute,
                "tokens_used":      tokens_used,
                "tokens_limit":     self.tokens_per_minute,
                "requests_remaining": self.requests_per_minute - len(self._request_times),
                "tokens_remaining":   self.tokens_per_minute  - tokens_used,
            }
