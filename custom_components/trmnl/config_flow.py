"""Config flow for TRMNL E-Ink Display integration."""
import logging
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .clients.trmnl_client import TRMNLClientFactory

_LOGGER = logging.getLogger(__name__)

IMPLEMENTATION_TYPES = {
    "standard": "Standard TRMNL (usetrmnl.com)",
    "terminus": "Terminus BYOS",
    "generic_byos": "Generic BYOS",
}


class TRMNLConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TRMNL."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Validate the input
            if user_input["implementation_type"] == "standard":
                return await self.async_step_standard()
            elif user_input["implementation_type"] == "terminus":
                return await self.async_step_terminus()
            elif user_input["implementation_type"] == "generic_byos":
                return await self.async_step_generic_byos()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("implementation_type"): vol.In(IMPLEMENTATION_TYPES),
                }
            ),
            errors=errors,
            description_placeholders={
                "implementations": ", ".join(IMPLEMENTATION_TYPES.values())
            },
        )

    async def async_step_standard(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle Standard TRMNL setup - API key entry."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            account_api_key = user_input.get("account_api_key", "").strip()
            if not account_api_key:
                errors["base"] = "invalid_api_key"
            else:
                # Store API key and move to device selection
                self.api_key = account_api_key
                return await self.async_step_standard_device()

        return self.async_show_form(
            step_id="standard",
            data_schema=vol.Schema(
                {
                    vol.Required("account_api_key"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "docs": "https://docs.usetrmnl.com",
            },
        )

    async def async_step_standard_device(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle Standard TRMNL device selection."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                device_mac = user_input.get("device_mac", "").strip()
                if not device_mac:
                    errors["base"] = "invalid_device"
                else:
                    await self.async_set_unique_id(f"trmnl-standard-{device_mac}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"TRMNL {device_mac}",
                        data={
                            "device_id": device_mac,
                            "implementation_type": "standard",
                            "api_key": self.api_key,
                            "api_endpoint": "https://usetrmnl.com",
                        },
                    )
            except Exception as err:
                _LOGGER.error(f"Error in standard device setup: {err}")
                errors["base"] = "unknown"

        # Try to fetch devices from API
        devices = await self._fetch_trmnl_devices(self.api_key)

        if devices:
            # Create a dropdown with device options
            device_options = {mac: f"{mac}" for mac in devices}
            if len(devices) == 1:
                # Auto-select if only one device
                single_mac = list(devices)[0]
                await self.async_set_unique_id(f"trmnl-standard-{single_mac}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"TRMNL {single_mac}",
                    data={
                        "device_id": single_mac,
                        "implementation_type": "standard",
                        "api_key": self.api_key,
                        "api_endpoint": "https://usetrmnl.com",
                    },
                )

            return self.async_show_form(
                step_id="standard_device",
                data_schema=vol.Schema(
                    {
                        vol.Required("device_mac"): vol.In(device_options),
                    }
                ),
                errors=errors,
            )
        else:
            # Fallback to manual entry if auto-discovery fails
            return self.async_show_form(
                step_id="standard_device",
                data_schema=vol.Schema(
                    {
                        vol.Required("device_mac"): str,
                    }
                ),
                errors=errors,
                description_placeholders={
                    "info": "Could not automatically detect devices. Please enter your device MAC address manually."
                },
            )

    async def _fetch_trmnl_devices(self, api_key: str) -> Dict[str, str]:
        """Fetch available TRMNL devices for the given API key."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Access-Token": api_key}
                # Try the devices endpoint
                async with session.get(
                    "https://usetrmnl.com/api/devices",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list):
                            # If response is a list of devices
                            devices = {}
                            for device in data:
                                if isinstance(device, dict) and "uuid" in device:
                                    devices[device["uuid"]] = device.get("name", device["uuid"])
                            return devices
                        elif isinstance(data, dict) and "devices" in data:
                            # If response has a devices key
                            devices = {}
                            for device in data["devices"]:
                                if isinstance(device, dict) and "uuid" in device:
                                    devices[device["uuid"]] = device.get("name", device["uuid"])
                            return devices
        except Exception as err:
            _LOGGER.debug(f"Could not fetch TRMNL devices: {err}")

        return {}

    async def async_step_terminus(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle Terminus BYOS setup."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                device_mac = user_input.get("device_mac", "").strip()
                api_endpoint = user_input.get("api_endpoint", "").strip()
                account_api_key = user_input.get("account_api_key", "").strip()

                if not device_mac or not api_endpoint:
                    errors["base"] = "invalid_input"
                else:
                    await self.async_set_unique_id(f"trmnl-terminus-{device_mac}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"TRMNL Terminus {device_mac}",
                        data={
                            "device_id": device_mac,
                            "implementation_type": "terminus",
                            "api_key": account_api_key,
                            "api_endpoint": api_endpoint,
                        },
                    )
            except Exception as err:
                _LOGGER.error(f"Error in Terminus setup: {err}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="terminus",
            data_schema=vol.Schema(
                {
                    vol.Required("device_mac"): str,
                    vol.Required("api_endpoint"): str,
                    vol.Optional("account_api_key"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_generic_byos(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle generic BYOS setup."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                device_mac = user_input.get("device_mac", "").strip()
                api_endpoint = user_input.get("api_endpoint", "").strip()

                if not device_mac or not api_endpoint:
                    errors["base"] = "invalid_input"
                else:
                    await self.async_set_unique_id(f"trmnl-byos-{device_mac}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"TRMNL BYOS {device_mac}",
                        data={
                            "device_id": device_mac,
                            "implementation_type": "generic_byos",
                            "api_key": user_input.get("account_api_key", ""),
                            "api_endpoint": api_endpoint,
                        },
                    )
            except Exception as err:
                _LOGGER.error(f"Error in generic BYOS setup: {err}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="generic_byos",
            data_schema=vol.Schema(
                {
                    vol.Required("device_mac"): str,
                    vol.Required("api_endpoint"): str,
                    vol.Optional("account_api_key"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this config entry."""
        return TRMNLOptionsFlow(config_entry)


class TRMNLOptionsFlow(config_entries.OptionsFlow):
    """Handle options for TRMNL."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "rate_limit_requests_per_hour",
                    default=self.config_entry.options.get(
                        "rate_limit_requests_per_hour", 12
                    ),
                ): int,
                vol.Optional(
                    "enable_rate_limiting",
                    default=self.config_entry.options.get(
                        "enable_rate_limiting", True
                    ),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
