"""Sensor platform for NOAA Space Weather."""
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SENSOR
from .entity import NoaaSpaceWeatherEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            NoaaSpaceWeatherSensor(coordinator, entry),
        ]
    )


class NoaaSpaceWeatherSensor(NoaaSpaceWeatherEntity):
    """noaa_space_weather Sensor class."""

    @property
    def unique_id(self):
        return "swpc SFI"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Solar Flux Index"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data["sfi_data"]["sfi"]

    @property
    def available(self):
        """Return the state of the sensor."""
        return True

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "noaa_space_weather__custom_device_class"
