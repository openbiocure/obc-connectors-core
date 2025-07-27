"""Rate limiter utility for managing API rate limits."""

import asyncio
import time
from typing import Optional

class RateLimiter:
    """Utility for managing API rate limits."""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self._lock:
            current_time = time.time()
            time_since_last_request = current_time - self._last_request_time
            min_interval = 1.0 / self.requests_per_second
            
            if time_since_last_request < min_interval:
                # Need to wait
                wait_time = min_interval - time_since_last_request
                await asyncio.sleep(wait_time)
            
            self._last_request_time = time.time() 