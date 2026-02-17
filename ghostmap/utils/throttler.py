"""
GHOSTMAP Adaptive Throttler — Manage request concurrency and handle rate limits.
"""

import asyncio
import logging
import random
import time
from typing import Optional

logger = logging.getLogger("ghostmap.utils.throttler")

class AdaptiveThrottler:
    """
    Manages delays and concurrency to respect rate limits.
    """

    def __init__(self, initial_rate_limit: float = 5.0, min_delay: float = 0.1):
        self.initial_delay = 1.0 / initial_rate_limit if initial_rate_limit > 0 else 0.0
        self.current_delay = self.initial_delay
        self.min_delay = min_delay
        self.max_delay = 60.0  # Max backoff
        self.consecutive_errors = 0
        self.is_throttled = False
        self.last_adjustment = time.time()
        self._lock: Optional[asyncio.Lock] = None

    async def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def wait(self):
        """Pause execution if needed."""
        if self.current_delay > 0:
            # Add jitter to avoid thundering herd
            jitter = random.uniform(0.8, 1.2)
            await asyncio.sleep(self.current_delay * jitter)

    async def report_result(self, status_code: int):
        """Update throttling state based on response."""
        lock = await self._get_lock()
        async with lock:
            now = time.time()
            
            # Rate Limited (429) or Blocked (403/WAF)
            if status_code == 429 or (status_code == 403 and self.consecutive_errors > 5):
                self.consecutive_errors += 1
                self.is_throttled = True
                
                # Exponential Backoff
                self.current_delay = min(self.max_delay, max(1.0, self.current_delay * 2))
                logger.warning(f"Rate Limited ({status_code})! Backing off to {self.current_delay:.2f}s")
             
            # Timeouts (0) - treat as sign of congestion if frequent
            elif status_code == 0:
                 self.consecutive_errors += 1
                 if self.consecutive_errors > 3:
                     self.is_throttled = True
                     self.current_delay = min(self.max_delay, max(1.0, self.current_delay * 1.5))
                     logger.warning(f"Repeated Timeouts! Backing off to {self.current_delay:.2f}s")

            # Success (200-3xx) or Soft Failure (404)
            elif status_code < 500:
                self.consecutive_errors = 0
                
                # Gradual Recovery
                if self.is_throttled and (now - self.last_adjustment > 5.0):
                    self.current_delay = max(self.min_delay, self.current_delay * 0.9)
                    if self.current_delay < self.initial_delay * 1.5:
                        self.is_throttled = False
                    self.last_adjustment = now

    def wait_sync(self):
        """Synchronous version of wait."""
        if self.current_delay > 0:
            jitter = random.uniform(0.8, 1.2)
            time.sleep(self.current_delay * jitter)

    def report_result_sync(self, status_code: int):
        """Synchronous version of report_result."""
        # Simple lock for thread safety if needed (though fuzzer is mostly single-threaded logic in loop)
        # But requests might be threaded? GhostFuzzer seems single threaded loop.
        now = time.time()
        
        if status_code == 429 or (status_code == 403 and self.consecutive_errors > 5):
            self.consecutive_errors += 1
            self.is_throttled = True
            self.current_delay = min(self.max_delay, max(1.0, self.current_delay * 2))
            logger.warning(f"Rate Limited ({status_code})! Backing off to {self.current_delay:.2f}s")
            
        elif status_code == 0:
             self.consecutive_errors += 1
             if self.consecutive_errors > 3:
                 self.is_throttled = True
                 self.current_delay = min(self.max_delay, max(1.0, self.current_delay * 1.5))
                 logger.warning(f"Repeated Timeouts! Backing off to {self.current_delay:.2f}s")

        elif status_code < 500:
            self.consecutive_errors = 0
            if self.is_throttled and (now - self.last_adjustment > 5.0):
                self.current_delay = max(self.min_delay, self.current_delay * 0.9)
                if self.current_delay < self.initial_delay * 1.5:
                    self.is_throttled = False
                self.last_adjustment = now

