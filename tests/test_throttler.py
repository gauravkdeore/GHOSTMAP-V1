
import pytest
import asyncio
import time
from ghostmap.utils.throttler import AdaptiveThrottler


def test_adaptive_throttler_backoff_sync_wrapper():
    async def _test():
        throttler = AdaptiveThrottler(initial_rate_limit=10.0, min_delay=0.1)
        
        # Initial state
        assert throttler.current_delay == 0.1
        assert not throttler.is_throttled
        
        # Simulate 429
        await throttler.report_result(429)
        assert throttler.is_throttled
        assert throttler.current_delay == 1.0  # Min backoff
        
        # Simulate another 429 (exponential)
        await throttler.report_result(429)
        assert throttler.current_delay == 2.0
    
    asyncio.run(_test())


def test_sync_throttler():
    throttler = AdaptiveThrottler(initial_rate_limit=5.0)
    throttler.report_result_sync(429)
    assert throttler.is_throttled
    assert throttler.current_delay >= 1.0
