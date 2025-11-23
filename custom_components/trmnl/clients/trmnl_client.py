"""TRMNL client factory and utilities."""
import logging
from typing import Optional

from .byos_client import BYOSClient, TerminusClient
from .standard_trmnl import StandardTRMNLClient
from . import TRMNLClientBase
from ..const import (
    IMPL_STANDARD,
    IMPL_TERMINUS,
    IMPL_GENERIC_BYOS,
)

_LOGGER = logging.getLogger(__name__)


class TRMNLClientFactory:
    """Factory for creating TRMNL API clients."""

    @staticmethod
    def create_client(
        implementation_type: str,
        device_id: str,
        api_key: str,
        api_endpoint: str,
        request_timeout: int = 30,
    ) -> Optional[TRMNLClientBase]:
        """Create appropriate TRMNL client based on implementation type.

        Args:
            implementation_type: Type of TRMNL implementation
            device_id: Device identifier
            api_key: API key or authentication token
            api_endpoint: API endpoint URL
            request_timeout: Request timeout in seconds

        Returns:
            Appropriate TRMNL client instance or None if invalid type
        """
        if implementation_type == IMPL_STANDARD:
            _LOGGER.debug("Creating Standard TRMNL client")
            return StandardTRMNLClient(
                device_id=device_id,
                api_key=api_key,
                api_endpoint=api_endpoint,
                request_timeout=request_timeout,
            )
        elif implementation_type == IMPL_TERMINUS:
            _LOGGER.debug("Creating Terminus BYOS client")
            return TerminusClient(
                device_id=device_id,
                api_key=api_key,
                api_endpoint=api_endpoint,
                request_timeout=request_timeout,
            )
        elif implementation_type == IMPL_GENERIC_BYOS:
            _LOGGER.debug("Creating generic BYOS client")
            return BYOSClient(
                device_id=device_id,
                api_key=api_key,
                api_endpoint=api_endpoint,
                request_timeout=request_timeout,
            )
        else:
            _LOGGER.error(f"Unknown implementation type: {implementation_type}")
            return None
