"""The TRMNL E-Ink Display integration."""
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOMAIN: Final = "trmnl"
PLATFORMS: list[Platform] = []

# Integration version
VERSION: Final = "1.0.0"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TRMNL from a config entry."""
    _LOGGER.debug(f"Setting up TRMNL integration for {entry.title}")

    # Store the config entry data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_id": entry.data.get("device_id"),
        "implementation_type": entry.data.get("implementation_type", "standard"),
        "api_key": entry.data.get("api_key"),
        "api_endpoint": entry.data.get("api_endpoint"),
    }

    # Register services
    from .services import async_setup_services
    await async_setup_services(hass, entry)

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading TRMNL integration for {entry.title}")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
