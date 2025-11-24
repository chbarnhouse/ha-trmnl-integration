"""The TRMNL E-Ink Display integration."""
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

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
    device_mac = entry.data.get("device_id")
    implementation_type = entry.data.get("implementation_type", "standard")
    api_key = entry.data.get("api_key")
    api_endpoint = entry.data.get("api_endpoint")

    hass.data[DOMAIN][entry.entry_id] = {
        "device_id": device_mac,
        "implementation_type": implementation_type,
        "api_key": api_key,
        "api_endpoint": api_endpoint,
    }

    # Try to fetch device name from API
    device_name = entry.title  # Default to entry title
    if implementation_type == "standard":
        try:
            from .clients.standard_trmnl import StandardTRMNLClient
            client = StandardTRMNLClient(
                device_id=device_mac,
                api_key=api_key,
                api_endpoint=api_endpoint,
            )
            devices = await client.fetch_devices()
            await client.close()

            # Get the name of our specific device
            if device_mac in devices:
                device_name = devices[device_mac]
                _LOGGER.debug(f"Fetched device name from API: {device_name}")
        except Exception as err:
            _LOGGER.warning(f"Could not fetch device name from API: {err}")
            # Fall back to entry title

    # Register device in device registry
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, device_mac)},
        manufacturer="TRMNL",
        model=implementation_type.replace("_", " ").title(),
        name=device_name,
    )
    _LOGGER.debug(f"Registered device: {device.name} ({device_mac})")

    # Update config entry title if we got a better name from API
    if device_name != entry.title:
        hass.config_entries.async_update_entry(entry, title=device_name)
        _LOGGER.debug(f"Updated config entry title to: {device_name}")

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
