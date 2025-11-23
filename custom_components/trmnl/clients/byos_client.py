"""BYOS (Bring Your Own Server) TRMNL client."""
import logging
from typing import Any, Dict, Optional

import aiohttp

from . import TRMNLClientBase

_LOGGER = logging.getLogger(__name__)


class BYOSClient(TRMNLClientBase):
    """Base client for BYOS implementations (Terminus, generic BYOS, etc.)."""

    def __init__(
        self,
        device_id: str,
        api_key: str,
        api_endpoint: str,
        request_timeout: int = 30,
    ):
        """Initialize BYOS client."""
        super().__init__(device_id, api_key, api_endpoint, request_timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def test_connection(self) -> bool:
        """Test connection to BYOS server."""
        try:
            session = await self._get_session()
            headers = self._get_headers()

            async with session.get(
                f"{self.api_endpoint}/api/setup",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                if resp.status in (200, 201):
                    _LOGGER.debug(
                        f"Successfully connected to BYOS server at {self.api_endpoint}"
                    )
                    return True
                else:
                    _LOGGER.error(
                        f"BYOS server returned status {resp.status}: {await resp.text()}"
                    )
                    return False
        except Exception as err:
            _LOGGER.error(f"Failed to test BYOS connection: {err}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with device ID."""
        headers = {"ID": self.device_id}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def send_image(
        self, image_url: str, refresh_rate: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send an image to the BYOS device.

        BYOS implementations typically use a playlist or direct image serving.
        This method assumes the server has a way to set the image URL.
        """
        try:
            session = await self._get_session()
            headers = self._get_headers()

            payload = {"image_url": image_url}
            if refresh_rate:
                payload["refresh_rate"] = refresh_rate

            # Try to send to /api/display endpoint (device-facing)
            # Most BYOS implementations allow updating what the device will see
            async with session.post(
                f"{self.api_endpoint}/api/display",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                response_data = (
                    await resp.json() if resp.content_type == "application/json" else {}
                )

                if resp.status in (200, 201):
                    _LOGGER.debug(f"Image sent to BYOS device {self.device_id}")
                    return {
                        "success": True,
                        "message": "Image sent to BYOS device",
                        "image_url": image_url,
                    }
                else:
                    error_msg = response_data.get(
                        "error", f"HTTP {resp.status}"
                    )
                    _LOGGER.error(
                        f"Failed to send image to BYOS device: {error_msg}"
                    )
                    return {"success": False, "error": error_msg}
        except Exception as err:
            _LOGGER.error(f"Exception sending image to BYOS device: {err}")
            return {"success": False, "error": str(err)}

    async def send_merge_variables(
        self, variables: Dict[str, Any], merge_strategy: str = "deep_merge"
    ) -> Dict[str, Any]:
        """Send data to BYOS device.

        For BYOS, this typically updates the current display data or playlist.
        """
        try:
            session = await self._get_session()
            headers = self._get_headers()

            payload = {
                "variables": variables,
                "merge_strategy": merge_strategy,
            }

            async with session.post(
                f"{self.api_endpoint}/api/display",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                response_data = (
                    await resp.json() if resp.content_type == "application/json" else {}
                )

                if resp.status in (200, 201):
                    _LOGGER.debug(
                        f"Variables sent to BYOS device {self.device_id}"
                    )
                    return {"success": True, "message": "Variables updated"}
                else:
                    error_msg = response_data.get(
                        "error", f"HTTP {resp.status}"
                    )
                    _LOGGER.error(f"Failed to send variables to BYOS: {error_msg}")
                    return {"success": False, "error": error_msg}
        except Exception as err:
            _LOGGER.error(f"Exception sending variables to BYOS: {err}")
            return {"success": False, "error": str(err)}

    async def get_device_status(self) -> Dict[str, Any]:
        """Get device status from BYOS server."""
        try:
            session = await self._get_session()
            headers = self._get_headers()

            async with session.get(
                f"{self.api_endpoint}/api/display",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                if resp.status in (200, 201):
                    data = await resp.json()
                    return {
                        "success": True,
                        "status": "online",
                        "image_url": data.get("image_url"),
                        "refresh_rate": data.get("refresh_rate", 1800),
                        "device_id": self.device_id,
                    }
                else:
                    return {
                        "success": False,
                        "status": "offline",
                        "error": f"HTTP {resp.status}",
                    }
        except Exception as err:
            _LOGGER.error(f"Failed to get BYOS device status: {err}")
            return {"success": False, "status": "error", "error": str(err)}


class TerminusClient(BYOSClient):
    """Specialized client for Terminus BYOS implementation."""

    async def send_image(
        self, image_url: str, refresh_rate: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send image to Terminus device."""
        # Terminus uses playlists or direct assignment
        # This is similar to the base BYOS but could have specific handling
        return await super().send_image(image_url, refresh_rate)
