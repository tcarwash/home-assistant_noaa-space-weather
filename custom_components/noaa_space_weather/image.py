"""Camera platform for NOAA Space Weather."""

from .const import DOMAIN, ICON
import logging
from .entity import NoaaSpaceWeatherImageEntity, NoaaSpaceWeatherAnimationEntity
from homeassistant.core import callback
from datetime import datetime, timedelta


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup camera platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    animationmap = [
        {
            "name": "SUVI Secondary 284 Angstroms",
            "product": "/products/animations/suvi-secondary-284.json",
            "device_class": "animation",
        },
        {
            "name": "SUVI Primary 195 Angstroms",
            "product": "/products/animations/suvi-primary-195.json",
            "device_class": "animation",
        },
        {
            "name": "SUVI Primary 304 Angstroms",
            "product": "/products/animations/suvi-primary-304.json",
            "device_class": "animation",
        },
    ]
    imagemap = [
        {
            "name": "Ace Solar Wind 3 Hour",
            "image_url": "https://services.swpc.noaa.gov/images/ace-mag-swepam-2-hour.gif",
            "device_class": "graph",
        },
        {
            "name": "Aurora Forecast North",
            "image_url": "https://services.swpc.noaa.gov/images/animations/ovation/north/latest.jpg",
            "icon": "mdi:aurora",
        },
        {
            "name": "Aurora Forecast South",
            "image_url": "https://services.swpc.noaa.gov/images/animations/ovation/south/latest.jpg",
            "icon": "mdi:aurora",
        },
        {
            "name": "GOES 195 Angstroms",
            "image_url": "https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png",
        },
        {
            "name": "Coronal Mass Ejection",
            "image_url": "https://services.swpc.noaa.gov/images/animations/lasco-c3/latest.jpg",
            "icon": "mdi:sun-wireless",
        },
    ]
    async_add_devices(
        [NoaaSpaceWeatherImage(coordinator, entry, image=i) for i in imagemap]
    )
    async_add_devices(
        [NoaaSpaceWeatherAnimation(coordinator, entry, image=i) for i in animationmap]
    )


class NoaaSpaceWeatherAnimation(NoaaSpaceWeatherAnimationEntity):
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
    def device_class(self):
        """Return the device class of the image."""
        return f"noaa_space_weather__{self.image_data.get('device_class', 'image')}"

    @property
    def icon(self):
        """Return the icon of the image."""
        try:
            icon = self.image_data["icon"]
        except KeyError:
            icon = ICON
        return icon

    async def async_image(self):
        if not self.image_last_updated or (
            self.image_last_updated > datetime.now() + timedelta(minutes=5)
        ):
            _LOGGER.debug("updating async image")
            self.image_last_updated = datetime.now()
            self._attr_image_last_updated = self.image_last_updated
            self.async_write_ha_state()
            image_bytes = await self.coordinator.api.async_load_animation(
                self.image_data["product"]
            )
            self._cached_image = image_bytes
            self.async_write_ha_state()
            return image_bytes
        else:
            _LOGGER.debug("returning cached image")
            return self._cached_image


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

    @property
    def icon(self):
        """Return the icon of the image."""
        try:
            icon = self.image_data["icon"]
        except KeyError:
            icon = ICON
        return icon

    @callback
    def _handle_coordinator_update(self):
        self.image_last_updated = datetime.now()
        self._attr_image_last_updated = self.image_last_updated
        self._cached_image = None
        self.async_write_ha_state()
