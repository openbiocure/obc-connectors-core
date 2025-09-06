"""Unit tests for rate limiter."""

import asyncio
import pytest
import time
from unittest.mock import patch
from obc_connector_sdk.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test cases for RateLimiter."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_second=10.0)
        assert limiter.requests_per_second == 10.0
        assert limiter._last_request_time == 0.0

    def test_rate_limiter_zero_rate(self):
        """Test rate limiter with zero rate."""
        limiter = RateLimiter(requests_per_second=0.0)
        assert limiter.requests_per_second == 0.0

    def test_rate_limiter_negative_rate(self):
        """Test rate limiter with negative rate."""
        limiter = RateLimiter(requests_per_second=-1.0)
        assert limiter.requests_per_second == -1.0

    @pytest.mark.asyncio
    async def test_acquire_first_request(self):
        """Test acquiring permission for first request."""
        limiter = RateLimiter(requests_per_second=10.0)
        
        start_time = time.time()
        await limiter.acquire()
        end_time = time.time()
        
        # First request should not be delayed
        assert end_time - start_time < 0.1
        assert limiter._last_request_time > 0

    @pytest.mark.asyncio
    async def test_acquire_rate_limiting(self):
        """Test that rate limiting works correctly."""
        limiter = RateLimiter(requests_per_second=2.0)  # 2 requests per second
        
        # First request should not be delayed
        start_time = time.time()
        await limiter.acquire()
        first_duration = time.time() - start_time
        
        # Second request should be delayed
        start_time = time.time()
        await limiter.acquire()
        second_duration = time.time() - start_time
        
        # Second request should take at least 0.5 seconds (1/2 requests per second)
        assert second_duration >= 0.4  # Allow some tolerance
        assert first_duration < 0.1

    @pytest.mark.asyncio
    async def test_acquire_multiple_requests(self):
        """Test multiple requests with rate limiting."""
        limiter = RateLimiter(requests_per_second=1.0)  # 1 request per second
        
        start_time = time.time()
        
        # Make 3 requests
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()
        
        total_duration = time.time() - start_time
        
        # Should take at least 2 seconds (1 second between each request)
        assert total_duration >= 1.8  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_acquire_concurrent_requests(self):
        """Test concurrent requests with rate limiting."""
        limiter = RateLimiter(requests_per_second=10.0)
        
        async def make_request():
            await limiter.acquire()
            return time.time()
        
        # Make 5 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_time
        
        # All requests should complete
        assert len(results) == 5
        
        # Should not take too long (rate limiter should handle concurrency)
        assert total_duration < 1.0

    @pytest.mark.asyncio
    async def test_acquire_high_rate(self):
        """Test rate limiter with high rate."""
        limiter = RateLimiter(requests_per_second=1000.0)
        
        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()
        total_duration = time.time() - start_time
        
        # High rate should not cause significant delay
        assert total_duration < 0.1

    @pytest.mark.asyncio
    async def test_acquire_zero_rate(self):
        """Test rate limiter with zero rate."""
        limiter = RateLimiter(requests_per_second=0.0)
        
        # This should not hang indefinitely
        with pytest.raises(ZeroDivisionError):
            await limiter.acquire()

    @pytest.mark.asyncio
    async def test_acquire_negative_rate(self):
        """Test rate limiter with negative rate."""
        limiter = RateLimiter(requests_per_second=-1.0)
        
        # Negative rate should result in negative wait time, so no waiting
        start_time = time.time()
        await limiter.acquire()
        duration = time.time() - start_time
        
        # Should complete quickly without waiting
        assert duration < 0.1

    @pytest.mark.asyncio
    async def test_acquire_with_mock_time(self):
        """Test rate limiter with mocked time."""
        limiter = RateLimiter(requests_per_second=2.0)
        
        with patch('time.time') as mock_time:
            # First request at time 0
            mock_time.return_value = 0.0
            await limiter.acquire()
            
            # Second request at time 0.2 (should be delayed)
            mock_time.return_value = 0.2
            await limiter.acquire()
            
            # Should have called time.time() for both requests
            assert mock_time.call_count >= 2

    @pytest.mark.asyncio
    async def test_acquire_precision(self):
        """Test rate limiter precision."""
        limiter = RateLimiter(requests_per_second=10.0)  # 0.1 second between requests
        
        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        duration = time.time() - start_time
        
        # Should be close to 0.1 seconds
        assert 0.05 <= duration <= 0.15
