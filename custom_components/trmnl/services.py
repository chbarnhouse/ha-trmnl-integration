"""Services for TRMNL E-Ink Display integration."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SERVICE_SEND_IMAGE, SERVICE_SEND_MERGE_VARIABLES
from .clients.trmnl_client import TRMNLClientFactory
from .rate_limiter import RateLimiterManager

_LOGGER = logging.getLogger(__name__)

# Global rate limiter manager
rate_limiter_manager = RateLimiterManager()

# Service schemas
SEND_IMAGE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): str,
        vol.Required("image_url"): str,
        vol.Optional("refresh_rate"): int,
    }
)

SEND_MERGE_VARIABLES_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): str,
        vol.Required("variables"): dict,
        vol.Optional("merge_strategy", default="deep_merge"): vol.In(
            ["deep_merge", "stream"]
        ),
    }
)


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up services for TRMNL integration."""

    async def handle_send_image(call: ServiceCall) -> None:
        """Handle send_image service call."""
        device_id = call.data.get("device_id")
        image_url = call.data.get("image_url")
        refresh_rate = call.data.get("refresh_rate")

        # Get client for the device
        client_config = hass.data[DOMAIN].get(entry.entry_id)
        if not client_config:
            raise HomeAssistantError(f"Device {device_id} not found in integration")

        if client_config.get("device_id") != device_id:
            raise HomeAssistantError(
                f"Device {device_id} does not match configured device"
            )

        # Check rate limiting
        rate_limit = entry.options.get("rate_limit_requests_per_hour", 12)
        enable_rate_limiting = entry.options.get("enable_rate_limiting", True)

        limiter = rate_limiter_manager.get_limiter(
            device_id=device_id,
            requests_per_hour=rate_limit,
            enabled=enable_rate_limiting,
        )

        if not limiter.can_make_request():
            wait_time = limiter.get_wait_time()
            remaining_time = int(wait_time)
            raise HomeAssistantError(
                f"Rate limit exceeded for {device_id}. "
                f"Please wait {remaining_time} seconds before retry."
            )

        # Create client
        client = TRMNLClientFactory.create_client(
            implementation_type=client_config.get("implementation_type"),
            device_id=device_id,
            api_key=client_config.get("api_key", ""),
            api_endpoint=client_config.get("api_endpoint"),
        )

        if not client:
            raise HomeAssistantError(
                f"Could not create client for device {device_id}"
            )

        try:
            result = await client.send_image(image_url, refresh_rate)
            if not result.get("success"):
                raise HomeAssistantError(
                    f"Failed to send image: {result.get('error')}"
                )

            # Record successful request
            limiter.record_request()
            limiter.log_status()
            _LOGGER.debug(f"Image sent to {device_id}: {image_url}")
        finally:
            await client.close()

    async def handle_send_merge_variables(call: ServiceCall) -> None:
        """Handle send_merge_variables service call."""
        device_id = call.data.get("device_id")
        variables = call.data.get("variables")
        merge_strategy = call.data.get("merge_strategy", "deep_merge")

        # Get client for the device
        client_config = hass.data[DOMAIN].get(entry.entry_id)
        if not client_config:
            raise HomeAssistantError(f"Device {device_id} not found in integration")

        if client_config.get("device_id") != device_id:
            raise HomeAssistantError(
                f"Device {device_id} does not match configured device"
            )

        # Check rate limiting
        rate_limit = entry.options.get("rate_limit_requests_per_hour", 12)
        enable_rate_limiting = entry.options.get("enable_rate_limiting", True)

        limiter = rate_limiter_manager.get_limiter(
            device_id=device_id,
            requests_per_hour=rate_limit,
            enabled=enable_rate_limiting,
        )

        if not limiter.can_make_request():
            wait_time = limiter.get_wait_time()
            remaining_time = int(wait_time)
            raise HomeAssistantError(
                f"Rate limit exceeded for {device_id}. "
                f"Please wait {remaining_time} seconds before retry."
            )

        # Create client
        client = TRMNLClientFactory.create_client(
            implementation_type=client_config.get("implementation_type"),
            device_id=device_id,
            api_key=client_config.get("api_key", ""),
            api_endpoint=client_config.get("api_endpoint"),
        )

        if not client:
            raise HomeAssistantError(
                f"Could not create client for device {device_id}"
            )

        try:
            result = await client.send_merge_variables(variables, merge_strategy)
            if not result.get("success"):
                raise HomeAssistantError(
                    f"Failed to send variables: {result.get('error')}"
                )

            # Record successful request
            limiter.record_request()
            limiter.log_status()
            _LOGGER.debug(
                f"Merge variables sent to {device_id}: {variables}"
            )
        finally:
            await client.close()

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_IMAGE,
        handle_send_image,
        schema=SEND_IMAGE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_MERGE_VARIABLES,
        handle_send_merge_variables,
        schema=SEND_MERGE_VARIABLES_SCHEMA,
    )

    _LOGGER.debug("TRMNL services registered")
