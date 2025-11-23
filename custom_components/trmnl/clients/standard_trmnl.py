"""Standard TRMNL API client."""
import logging
from typing import Any, Dict, Optional

import aiohttp

from . import TRMNLClientBase

_LOGGER = logging.getLogger(__name__)


class StandardTRMNLClient(TRMNLClientBase):
    """Client for standard TRMNL devices (usetrmnl.com)."""

    def __init__(
        self,
        device_id: str,
        api_key: str,
        api_endpoint: str = "https://usetrmnl.com",
        request_timeout: int = 30,
    ):
        """Initialize Standard TRMNL client."""
        super().__init__(device_id, api_key, api_endpoint, request_timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.plugin_uuid: Optional[str] = None

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
        """Test connection to TRMNL server."""
        try:
            session = await self._get_session()
            headers = {
                "ID": self.device_id,
                "Access-Token": self.api_key,
            }

            async with session.get(
                f"{self.api_endpoint}/api/current_screen",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                if resp.status == 200:
                    _LOGGER.debug("Successfully connected to TRMNL server")
                    return True
                else:
                    _LOGGER.error(
                        f"TRMNL server returned status {resp.status}: {await resp.text()}"
                    )
                    return False
        except Exception as err:
            _LOGGER.error(f"Failed to test TRMNL connection: {err}")
            return False

    async def send_image(
        self, image_url: str, refresh_rate: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send an image to the TRMNL device via webhook.

        For Standard TRMNL, we need to set up a private plugin webhook.
        This method pushes merge variables that trigger a template render
        with the image URL.
        """
        try:
            if not self.plugin_uuid:
                return {
                    "success": False,
                    "error": "Plugin UUID not configured. Set plugin_uuid before sending images.",
                }

            session = await self._get_session()

            payload = {"merge_variables": {"image_url": image_url}}

            if refresh_rate:
                payload["merge_variables"]["refresh_rate"] = refresh_rate

            async with session.post(
                f"{self.api_endpoint}/api/custom_plugins/{self.plugin_uuid}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                response_data = await resp.json()

                if resp.status == 200:
                    _LOGGER.debug(f"Image sent to TRMNL device {self.device_id}")
                    return {
                        "success": True,
                        "message": "Image sent to TRMNL device",
                        "image_url": image_url,
                    }
                else:
                    _LOGGER.error(
                        f"Failed to send image to TRMNL: {response_data}"
                    )
                    return {
                        "success": False,
                        "error": f"TRMNL API error: {response_data}",
                    }
        except Exception as err:
            _LOGGER.error(f"Exception sending image to TRMNL: {err}")
            return {"success": False, "error": str(err)}

    async def send_merge_variables(
        self, variables: Dict[str, Any], merge_strategy: str = "deep_merge"
    ) -> Dict[str, Any]:
        """Send merge variables to TRMNL device (webhook-based)."""
        try:
            if not self.plugin_uuid:
                return {
                    "success": False,
                    "error": "Plugin UUID not configured.",
                }

            session = await self._get_session()

            payload = {
                "merge_variables": variables,
                "merge_strategy": merge_strategy,
            }

            async with session.post(
                f"{self.api_endpoint}/api/custom_plugins/{self.plugin_uuid}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                response_data = await resp.json()

                if resp.status == 200:
                    _LOGGER.debug(
                        f"Merge variables sent to TRMNL device {self.device_id}"
                    )
                    return {"success": True, "message": "Variables updated"}
                else:
                    _LOGGER.error(
                        f"Failed to send merge variables: {response_data}"
                    )
                    return {
                        "success": False,
                        "error": f"TRMNL API error: {response_data}",
                    }
        except Exception as err:
            _LOGGER.error(f"Exception sending merge variables: {err}")
            return {"success": False, "error": str(err)}

    async def get_device_status(self) -> Dict[str, Any]:
        """Get current device status from TRMNL server."""
        try:
            session = await self._get_session()
            headers = {
                "ID": self.device_id,
                "Access-Token": self.api_key,
            }

            async with session.get(
                f"{self.api_endpoint}/api/current_screen",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "status": "online",
                        "image_url": data.get("image_url"),
                        "refresh_rate": data.get("refresh_rate"),
                        "filename": data.get("filename"),
                    }
                else:
                    return {
                        "success": False,
                        "status": "offline",
                        "error": f"HTTP {resp.status}",
                    }
        except Exception as err:
            _LOGGER.error(f"Failed to get device status: {err}")
            return {"success": False, "status": "error", "error": str(err)}

    def set_plugin_uuid(self, uuid: str) -> None:
        """Set the webhook plugin UUID for sending images."""
        self.plugin_uuid = uuid
        _LOGGER.debug(f"Plugin UUID set to {uuid}")
