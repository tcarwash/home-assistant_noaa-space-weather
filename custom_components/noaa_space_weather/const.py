"""Constants for NOAA Space Weather."""

# Base component constants
NAME = "NOAA Space Weather"
DOMAIN = "noaa_space_weather"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "2.2.0-beta"

ATTRIBUTION = "Data provided by https://services.swpc.noaa.gov"
ISSUE_URL = "https://github.com/tcarwash/home-assistant_noaa-space-weather/issues/"

# Icons
ICON = "mdi:weather-sunny"

# Device classes
# BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
# Load both sensors and images
PLATFORMS = [SENSOR, "image"]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_LEGACY_NAMING = "legacy_naming"
CONF_ENABLE_ANIMATIONS = "enable_animations"
NAME_PREFIX = "noaasw_"

# Defaults
DEFAULT_NAME = "NOAA Space Weather"
DEFAULT_LEGACY_NAMING = False
DEFAULT_ENABLE_ANIMATIONS = False


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues, open one at
{ISSUE_URL}
-------------------------------------------------------------------
"""
