"""Camera platform for NOAA Space Weather."""

from .const import DOMAIN, ICON
import logging
import asyncio
from .entity import NoaaSpaceWeatherImageEntity, NoaaSpaceWeatherAnimationEntity
from homeassistant.core import callback
from datetime import datetime, timedelta


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup camera platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    animationmap = [
        {
            "name": "Animated SUVI Secondary 284 Angstroms",
            "product": "/products/animations/suvi-secondary-284.json",
            "device_class": "animation",
        },
        {
            "name": "Animated SUVI Primary 195 Angstroms",
            "product": "/products/animations/suvi-primary-195.json",
            "device_class": "animation",
        },
        {
            "name": "Animated SUVI Primary 304 Angstroms",
            "product": "/products/animations/suvi-primary-304.json",
            "device_class": "animation",
        },
        {
            "name": "Animated WFS Ionosphere",
            "product": "/products/animations/wam-ipe/wfs_ionosphere_new.json",
            "device_class": "animation",
        },
        {
            "name": "Animated Lasco C2",
            "product": "/products/animations/lasco-c2.json",
            "device_class": "animation",
        },
        {
            "name": "Animated Lasco C3",
            "product": "/products/animations/lasco-c3.json",
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
        [NoaaSpaceWeatherImage(coordinator, entry, image=i) for i in imagemap],
        update_before_add=True,
    )
    async_add_devices(
        [NoaaSpaceWeatherAnimation(coordinator, entry, image=i) for i in animationmap],
        update_before_add=True,
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

    async def async_update(self):
        if not self._cached_image:
            _LOGGER.debug("returning still")
            image_bytes = await self.coordinator.api.async_get_first_frame(
                self.image_data["product"]
            )
            self._cached_image = image_bytes
            self.image_last_updated = datetime.now() - timedelta(days=1)
            loop = asyncio.get_event_loop()
            loop.create_task(self.async_update())
        else:
            self.image_last_updated = datetime.now()
            self._attr_image_last_updated = self.image_last_updated
            image_bytes = await self.coordinator.api.async_load_animation(
                self.image_data["product"]
            )
            _LOGGER.debug(f"Updated animation for {self.name}, caching image")
            self._cached_image = image_bytes

    async def async_image(self):
        if not self._cached_image or (
            self.image_last_updated < datetime.now() - timedelta(minutes=5)
        ):
            loop = asyncio.get_event_loop()
            loop.create_task(self.async_update())
        else:
            _LOGGER.debug(f"returning cached image for: {self.name}")
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
