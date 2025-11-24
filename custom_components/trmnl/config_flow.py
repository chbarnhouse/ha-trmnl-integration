"""Config flow for TRMNL E-Ink Display integration."""
import logging
from typing import Any, Dict, Optional

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
        """Handle Standard TRMNL setup."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate device_mac and account_api_key
                device_mac = user_input.get("device_mac", "").strip()
                account_api_key = user_input.get("account_api_key", "").strip()

                if not device_mac or not account_api_key:
                    errors["base"] = "invalid_input"
                else:
                    # Create a unique ID for this config entry
                    await self.async_set_unique_id(f"trmnl-standard-{device_mac}")
                    self._abort_if_unique_id_configured()

                    # Return the config entry
                    return self.async_create_entry(
                        title=f"TRMNL {device_mac}",
                        data={
                            "device_id": device_mac,
                            "implementation_type": "standard",
                            "api_key": account_api_key,
                            "api_endpoint": "https://usetrmnl.com",
                        },
                    )
            except Exception as err:
                _LOGGER.error(f"Error in standard setup: {err}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="standard",
            data_schema=vol.Schema(
                {
                    vol.Required("device_mac"): str,
                    vol.Required("account_api_key"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "docs": "https://docs.usetrmnl.com",
            },
        )

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
