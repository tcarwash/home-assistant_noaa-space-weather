"""Camera platform for NOAA Space Weather."""

from .const import DOMAIN
import logging
from .entity import NoaaSpaceWeatherImageEntity
from homeassistant.core import callback
from datetime import datetime


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup camera platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    imagemap = [
        {
            "name": "Ace Solar Wind 3 Hour",
            "image_url": "https://services.swpc.noaa.gov/images/ace-mag-swepam-2-hour.gif",
            "device_class": "graph",
        },
        {
            "name": "Aurora Forecast North",
            "image_url": "https://services.swpc.noaa.gov/images/animations/ovation/north/latest.jpg",
        },
        {
            "name": "Aurora Forecast South",
            "image_url": "https://services.swpc.noaa.gov/images/animations/ovation/south/latest.jpg",
        },
        {
            "name": "GOES 195 Angstroms",
            "image_url": "https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png",
        },
        {
            "name": "Coronal Mass Ejection",
            "image_url": "https://services.swpc.noaa.gov/images/animations/lasco-c3/latest.jpg",
        },
    ]
    async_add_devices(
        [NoaaSpaceWeatherImage(coordinator, entry, image=i) for i in imagemap]
    )


class NoaaSpaceWeatherImage(NoaaSpaceWeatherImageEntity):
    """noaa_space_weather Image class."""

    def __init__(self, coordinator, entry, image):
        self.image_data = image
        self.entry = entry
        self.coordinator = coordinator
        super().__init__(coordinator, entry)

    @property
    def unique_id(self):
        return f"swpc {self.image_data['name']}"

    @property
    def name(self):
        return self.image_data.get("name")

    @property
    def state(self):
        if self._cached_image:
            return "available"
        else:
            return "available"

    @property
    def image_url(self):
        return self.image_data.get("image_url")

    @property
    def device_class(self):
        """Return the device class of the image."""
        return f"noaa_space_weather__{self.image_data.get('device_class', 'image')}"

    @callback
    def _handle_coordinator_update(self):
        self.image_last_updated = datetime.now()
        self._cached_image = None
        self.async_write_ha_state()
