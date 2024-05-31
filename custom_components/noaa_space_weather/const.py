"""Constants for NOAA Space Weather."""

# Base component constants
NAME = "NOAA Space Weather"
DOMAIN = "noaa_space_weather"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "2.1.0-beta"

ATTRIBUTION = "Data provided by https://services.swpc.noaa.gov"
ISSUE_URL = "https://github.com/tcarwash/home-assistant_noaa-space-weather/issues/"

# Icons
ICON = "mdi:weather-sunny"


# Platforms
PLATFORMS = ["sensor", "image"]


# Configuration and options
CONF_ENABLED = "enabled"

# Defaults
DEFAULT_NAME = "NOAA Space Weather"


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
