"""Image platform for NOAA Space Weather."""

from .const import DOMAIN, ICON
from .entity import NoaaSpaceWeatherImageEntity
import logging
import asyncio
from homeassistant.core import callback
from datetime import datetime
import random


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up NOAA Space Weather image platform."""
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
    )


class NoaaSpaceWeatherAnimation(NoaaSpaceWeatherImageEntity):
    """noaa_space_weather Image class."""

    def __init__(self, coordinator, entry, image):
        self.image_data = image
        self.entry = entry
        self.coordinator = coordinator

        super().__init__(coordinator, entry)
        self._jitter = random.uniform(2, 15)
        self._cached_image = None

    @property
    def unique_id(self):
        return f"swpc {self.image_data['name']}"

    @property
    def name(self):
        return self.image_data.get("name")

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
        """Refresh the cached image bytes; lazy-build full animation."""
        if not self._cached_image:
            _LOGGER.debug("%s: fetching first frame", self.name)
            image_bytes = await self.coordinator.api.async_get_first_frame(
                self.image_data["product"]
            )
            self._set_cached(image_bytes)
            # Build full animation in background with jitter
            self.hass.loop.create_task(self._build_animation_with_jitter())
            return image_bytes

        _LOGGER.debug("%s: refreshing full animation", self.name)
        image_bytes = await self.coordinator.api.async_load_animation(
            self.image_data["product"]
        )
        self._set_cached(image_bytes)
        return image_bytes

    async def _build_animation_with_jitter(self):
        try:
            await asyncio.sleep(self._jitter)
            image_bytes = await self.coordinator.api.async_load_animation(
                self.image_data["product"]
            )
            self._set_cached(image_bytes)
            self.async_write_ha_state()
            _LOGGER.debug("%s: background animation ready", self.name)
        except Exception as err:
            _LOGGER.debug("%s: background animation failed: %s", self.name, err)

    def _detect_mime(self, data: bytes) -> str:
        if len(data) >= 4:
            if data[:3] == b"GIF":
                return "image/gif"
            if data[:4] == b"\x89PNG":
                return "image/png"
            if data[:2] == b"\xff\xd8":
                return "image/jpeg"
        return "application/octet-stream"

    def _set_cached(self, image_bytes: bytes) -> None:
        self._cached_image = image_bytes
        self.image_last_updated = datetime.now()
        self._attr_image_last_updated = self.image_last_updated
        # Let HA know how to serve the bytes
        try:
            self._attr_content_type = self._detect_mime(image_bytes)
        except Exception:  # pragma: no cover - best effort
            self._attr_content_type = "application/octet-stream"

    @callback
    def _handle_coordinator_update(self):
        # Stagger refresh to avoid all entities downloading at once
        self.image_last_updated = datetime.now()
        self._attr_image_last_updated = self.image_last_updated
        self.hass.loop.create_task(self._build_animation_with_jitter())
        self.async_write_ha_state()

    async def async_image(self):
        return self._cached_image or await self.async_update()


class NoaaSpaceWeatherImage(NoaaSpaceWeatherImageEntity):
    """noaa_space_weather Image class."""

    def __init__(self, coordinator, entry, image):
        self.image_data = image
        self.entry = entry
        self.coordinator = coordinator

        super().__init__(coordinator, entry)
        self._cached_image = None

    @property
    def unique_id(self):
        return f"swpc {self.image_data['name']}"

    @property
    def name(self):
        return self.image_data.get("name")

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
