"""TRMNL client implementations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

_LOGGER = logging.getLogger(__name__)


class TRMNLClientBase(ABC):
    """Base class for TRMNL API clients."""

    def __init__(
        self,
        device_id: str,
        api_key: str,
        api_endpoint: str,
        request_timeout: int = 30,
    ):
        """Initialize TRMNL client."""
        self.device_id = device_id
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.request_timeout = request_timeout

    @abstractmethod
    async def send_image(
        self, image_url: str, refresh_rate: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send an image to the TRMNL device.

        Args:
            image_url: URL of the image to display
            refresh_rate: Optional refresh rate in seconds

        Returns:
            Response dict with success status and details
        """

    @abstractmethod
    async def send_merge_variables(
        self, variables: Dict[str, Any], merge_strategy: str = "deep_merge"
    ) -> Dict[str, Any]:
        """Send merge variables to the TRMNL device (for webhook-based updates).

        Args:
            variables: Dictionary of variables to merge
            merge_strategy: Strategy for merging (deep_merge, stream, etc.)

        Returns:
            Response dict with success status and details
        """

    @abstractmethod
    async def get_device_status(self) -> Dict[str, Any]:
        """Get the current status of the TRMNL device.

        Returns:
            Device status dict
        """

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the TRMNL device/server.

        Returns:
            True if connection is successful, False otherwise
        """
