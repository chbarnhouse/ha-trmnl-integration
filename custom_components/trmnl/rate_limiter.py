"""Rate limiter for TRMNL API requests."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

_LOGGER = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for TRMNL API requests."""

    def __init__(
        self,
        device_id: str,
        requests_per_hour: int = 12,
        enabled: bool = True,
    ):
        """Initialize rate limiter.

        Args:
            device_id: Device identifier
            requests_per_hour: Maximum requests allowed per hour
            enabled: Whether rate limiting is enabled
        """
        self.device_id = device_id
        self.requests_per_hour = requests_per_hour
        self.enabled = enabled
        self.request_times: list = []
        self.last_request_time: Optional[datetime] = None

    def can_make_request(self) -> bool:
        """Check if a request can be made within rate limits.

        Returns:
            True if request is allowed, False if rate limited
        """
        if not self.enabled:
            return True

        now = datetime.now()

        # Clean up old requests outside the 1-hour window
        cutoff_time = now - timedelta(hours=1)
        self.request_times = [
            req_time for req_time in self.request_times if req_time > cutoff_time
        ]

        # Check if we can make a request
        if len(self.request_times) < self.requests_per_hour:
            return True

        return False

    def record_request(self) -> None:
        """Record that a request was made."""
        self.request_times.append(datetime.now())
        self.last_request_time = datetime.now()

    def get_remaining_requests(self) -> int:
        """Get number of remaining requests in the current hour window.

        Returns:
            Number of remaining requests, or -1 if unlimited
        """
        if not self.enabled:
            return -1

        now = datetime.now()
        cutoff_time = now - timedelta(hours=1)
        self.request_times = [
            req_time for req_time in self.request_times if req_time > cutoff_time
        ]

        remaining = max(0, self.requests_per_hour - len(self.request_times))
        return remaining

    def get_reset_time(self) -> Optional[datetime]:
        """Get the time when the rate limit resets.

        Returns:
            Datetime of next reset, or None if no requests pending
        """
        if not self.request_times:
            return None

        oldest_request = min(self.request_times)
        return oldest_request + timedelta(hours=1)

    def get_wait_time(self) -> float:
        """Get seconds to wait before next request is allowed.

        Returns:
            Seconds to wait, or 0 if request can be made immediately
        """
        if self.can_make_request():
            return 0

        reset_time = self.get_reset_time()
        if reset_time:
            now = datetime.now()
            wait_seconds = (reset_time - now).total_seconds()
            return max(0, wait_seconds)

        return 0

    def log_status(self) -> None:
        """Log current rate limiter status."""
        if not self.enabled:
            _LOGGER.debug(f"Rate limiting disabled for {self.device_id}")
            return

        remaining = self.get_remaining_requests()
        _LOGGER.debug(
            f"Device {self.device_id}: {remaining}/{self.requests_per_hour} "
            f"requests remaining in current hour"
        )


class RateLimiterManager:
    """Manages rate limiters for multiple devices."""

    def __init__(self):
        """Initialize rate limiter manager."""
        self.limiters: Dict[str, RateLimiter] = {}

    def get_limiter(
        self,
        device_id: str,
        requests_per_hour: int = 12,
        enabled: bool = True,
    ) -> RateLimiter:
        """Get or create a rate limiter for a device.

        Args:
            device_id: Device identifier
            requests_per_hour: Maximum requests per hour
            enabled: Whether rate limiting is enabled

        Returns:
            Rate limiter instance
        """
        if device_id not in self.limiters:
            self.limiters[device_id] = RateLimiter(
                device_id=device_id,
                requests_per_hour=requests_per_hour,
                enabled=enabled,
            )
        return self.limiters[device_id]

    def update_limiter(
        self,
        device_id: str,
        requests_per_hour: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        """Update limiter settings.

        Args:
            device_id: Device identifier
            requests_per_hour: New request limit
            enabled: New enabled status
        """
        if device_id in self.limiters:
            if requests_per_hour is not None:
                self.limiters[device_id].requests_per_hour = requests_per_hour
            if enabled is not None:
                self.limiters[device_id].enabled = enabled
