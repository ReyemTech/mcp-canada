"""Per-source token bucket rate limiter — stub for scaffold phase."""

from dataclasses import dataclass, field
import asyncio
import time


@dataclass
class TokenBucket:
    """Async token bucket rate limiter."""

    rate: float  # tokens per second
    capacity: float  # max burst size
    _tokens: float = field(init=False)
    _last_refill: float = field(init=False)
    _lock: asyncio.Lock = field(init=False)

    def __post_init__(self) -> None:
        self._tokens = self.capacity
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire one token, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last_refill = now

            if self._tokens >= 1:
                self._tokens -= 1
                return

        # Not enough tokens — wait for one to refill
        wait_time = (1 - self._tokens) / self.rate
        await asyncio.sleep(wait_time)
        await self.acquire()


_limiters: dict[str, TokenBucket] = {}


def get_limiter(source: str, rate: float = 10.0, capacity: float = 10) -> TokenBucket:
    """Return the singleton TokenBucket for the given source."""
    if source not in _limiters:
        _limiters[source] = TokenBucket(rate=rate, capacity=capacity)
    return _limiters[source]
