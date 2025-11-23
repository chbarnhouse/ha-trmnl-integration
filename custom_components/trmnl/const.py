"""Constants for TRMNL E-Ink Display integration."""
from typing import Final

DOMAIN: Final = "trmnl"
VERSION: Final = "1.0.0"

# Implementation types
IMPL_STANDARD: Final = "standard"
IMPL_TERMINUS: Final = "terminus"
IMPL_GENERIC_BYOS: Final = "generic_byos"

# Service names
SERVICE_SEND_IMAGE: Final = "send_image"
SERVICE_SEND_MERGE_VARIABLES: Final = "send_merge_variables"

# API Endpoints
TRMNL_API_BASE_URL: Final = "https://usetrmnl.com"
TRMNL_API_DISPLAY_ENDPOINT: Final = "/api/display"
TRMNL_API_CURRENT_SCREEN_ENDPOINT: Final = "/api/current_screen"
TRMNL_API_CUSTOM_PLUGINS_ENDPOINT: Final = "/api/custom_plugins"

# Rate limiting defaults
DEFAULT_RATE_LIMIT_STANDARD: Final = 12  # requests per hour
DEFAULT_RATE_LIMIT_PREMIUM: Final = 30  # requests per hour

# Timeouts
REQUEST_TIMEOUT: Final = 30  # seconds
