"""Image platform for NOAA Space Weather."""

import asyncio
import logging
import random
from datetime import datetime

from homeassistant.core import callback
from homeassistant.util import slugify
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, ICON, CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING, NAME_PREFIX
from .entity import NoaaSpaceWeatherImageEntity


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up NOAA Space Weather image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    animationmap = [
        {
            "name": "Animated SUVI Secondary 284 Angstroms",
            "product": "/products/animations/suvi-secondary-284.json",
            "device_class": "animation",
        },
        {
            "name": "Animated SUVI Primary 171 Angstroms",
            "product": "/products/animations/suvi-primary-171.json",
            "device_class": "animation",
        },
        {
            "name": "Animated SUVI Primary 304 Angstroms",
            "product": "/products/animations/suvi-primary-304.json",
            "device_class": "animation",
        },
        {
            "name": "Animated SUVI Thematic Map",
            "product": "/products/animations/suvi-primary-map.json",
            "device_class": "animation",
        },
        {
            "name": "Animated WFS Ionosphere",
            "product": "/products/animations/wam-ipe/wfs_ionosphere_new.json",
            "device_class": "animation",
        },
        {
            "name": "Animated Coronagraph CCOR1",
            "product": "/products/animations/ccor1/ccor1.json",
            "device_class": "animation",
        },
        {
            "name": "Animated Geospace Magnetosphere Velocity",
            "product": "/products/animations/geospace/velocity.json",
            "icon": "mdi:earth",
        },
        {
            "name": "Animated Geospace Magnetosphere Density",
            "product": "/products/animations/geospace/density.json",
            "icon": "mdi:earth",
        },
        {
            "name": "Animated Geospace Magnetosphere Pressure",
            "product": "/products/animations/geospace/pressure.json",
            "icon": "mdi:earth",
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
        {
            "name": "Animated Aurora Forecast North",
            "product": "/products/animations/ovation_north_24h.json",
            "icon": "mdi:aurora",
        },
        {
            "name": "Animated Aurora Forecast South",
            "product": "/products/animations/ovation_south_24h.json",
            "icon": "mdi:aurora",
        },
        {
            "name": "Animated Geoelectric Field US-Canada",
            "product": "/products/animations/geoelectric/US-Canada-1D.json",
            "icon": "mdi:earth",
        },
    ]

    imagemap = [
        {
            "name": "Ace Solar Wind 3 Hour",
            "image_url": "https://services.swpc.noaa.gov/images/ace-mag-swepam-2-hour.gif",
            "device_class": "graph",
        },
        {
            "name": "Todays Forcasted Aurora Viewline",
            "image_url": "https://services.swpc.noaa.gov/experimental/images/aurora_dashboard/tonights_static_viewline_forecast.png",
            "icon": "mdi:aurora",
        },
        {
            "name": "Tomorrows Forcasted Aurora Viewline",
            "image_url": "https://services.swpc.noaa.gov/experimental/images/aurora_dashboard/tomorrow_nights_static_viewline_forecast.png",
            "icon": "mdi:aurora",
        },
    ]

    _LOGGER.info(
        "Setting up %d images and %d animations", len(imagemap), len(animationmap)
    )

    entities = [
        *(NoaaSpaceWeatherImage(coordinator, entry, i) for i in imagemap),
        *(NoaaSpaceWeatherAnimation(coordinator, entry, i) for i in animationmap),
    ]
    async_add_entities(entities, update_before_add=True)

    # Kick off a background prefetch of all animations so they are ready shortly after setup
    try:
        products = [a.get("product", "") for a in animationmap if a.get("product")]
        if products:
            hass.loop.create_task(
                coordinator.api.async_prefetch_animations(
                    products, concurrency=3, per_item_timeout=90.0
                )
            )
            _LOGGER.debug(
                "Started background prefetch for %d animations", len(products)
            )
    except Exception as err:  # pragma: no cover - best effort
        _LOGGER.debug("Unable to start animation prefetch: %s", err)


class NoaaSpaceWeatherAnimation(NoaaSpaceWeatherImageEntity):
    """Animated image entity built from product frames."""

    def __init__(self, coordinator, entry, image):
        self.image_data = image
        self.entry = entry
        self.coordinator = coordinator
        super().__init__(coordinator, entry)

        # Prefer attribute fields to avoid overriding typed properties on Entity
        self._attr_unique_id = f"swpc {self.image_data.get('name')}"
        base = self.image_data.get("name")
        # Keep display name human-friendly; entity_id will be prefixed via suggested_object_id
        self._attr_name = base
        self._attr_device_class = (
            f"noaa_space_weather__{self.image_data.get('device_class', 'image')}"
        )
        self._attr_icon = self.image_data.get("icon", ICON)

        self._jitter = random.uniform(2, 30)
        self._raw_bytes = None

    async def async_update(self):
        """Fetch/refresh animation bytes."""
        image_bytes = b""
        if not self._raw_bytes:
            # If a background prefetch has already warmed this animation, use it immediately
            try:
                cached = self.coordinator.api.get_cached_animation(
                    self.image_data.get("product", "")
                )
            except Exception:
                cached = None
            if cached:
                self._set_cached(cached)
                return cached
            _LOGGER.debug("%s: fetching first frame", self.name)
            try:
                image_bytes = await self.coordinator.api.async_get_first_frame(
                    self.image_data.get("product", "")
                )
                self._set_cached(image_bytes)
                # build full animation in background
                self.hass.loop.create_task(self._build_animation_with_jitter())
            except Exception as err:  # pragma: no cover - best effort
                _LOGGER.error("%s: initial animation fetch failed: %s", self.name, err)
                raise
            return image_bytes

        try:
            _LOGGER.debug("%s: refreshing full animation", self.name)
            image_bytes = await self.coordinator.api.async_load_animation(
                self.image_data.get("product", "")
            )
            self._set_cached(image_bytes)
        except Exception as err:  # pragma: no cover - best effort
            _LOGGER.error("%s: animation refresh failed: %s", self.name, err)
            raise
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
        except Exception as err:  # pragma: no cover - best effort
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
        self._raw_bytes = image_bytes
        self.image_last_updated = datetime.now()
        self._attr_image_last_updated = self.image_last_updated
        try:
            self._attr_content_type = self._detect_mime(image_bytes)
        except Exception:  # pragma: no cover - best effort
            self._attr_content_type = "application/octet-stream"

    @callback
    def _handle_coordinator_update(self):
        self.image_last_updated = datetime.now()
        self._attr_image_last_updated = self.image_last_updated
        self.hass.loop.create_task(self._build_animation_with_jitter())
        self.async_write_ha_state()

    async def async_image(self):
        return self._raw_bytes or await self.async_update()

    @property
    def suggested_object_id(self) -> str:
        base = slugify(self.image_data.get("name") or "image")
        legacy = self.config_entry.options.get(
            CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
        )
        return base if legacy else f"{NAME_PREFIX}{base}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        legacy = self.config_entry.options.get(
            CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
        )
        if legacy:
            return
        registry = er.async_get(self.hass)
        entry = registry.async_get(self.entity_id)
        if not entry:
            return
        object_id = entry.entity_id.split(".", 1)[1]
        if object_id.startswith(NAME_PREFIX):
            return
        new_object_id = self.suggested_object_id
        new_entity_id = f"{entry.domain}.{new_object_id}"
        if registry.async_get(new_entity_id) is None:
            registry.async_update_entity(entry.entity_id, new_entity_id=new_entity_id)


class NoaaSpaceWeatherImage(NoaaSpaceWeatherImageEntity):
    """Static image entity served directly from remote URL."""

    def __init__(self, coordinator, entry, image):
        self.image_data = image
        self.entry = entry
        self.coordinator = coordinator
        super().__init__(coordinator, entry)

        self._attr_unique_id = f"swpc {self.image_data.get('name')}"
        base = self.image_data.get("name")
        # Keep display name human-friendly; entity_id will be prefixed via suggested_object_id
        self._attr_name = base
        self._attr_image_url = self.image_data.get("image_url")
        self._attr_device_class = (
            f"noaa_space_weather__{self.image_data.get('device_class', 'image')}"
        )
        self._attr_icon = self.image_data.get("icon", ICON)

    @callback
    def _handle_coordinator_update(self):
        self.image_last_updated = datetime.now()
        self._attr_image_last_updated = self.image_last_updated
        self.async_write_ha_state()

    @property
    def suggested_object_id(self) -> str:
        base = slugify(self.image_data.get("name") or "image")
        legacy = self.config_entry.options.get(
            CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
        )
        return base if legacy else f"{NAME_PREFIX}{base}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        legacy = self.config_entry.options.get(
            CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
        )
        if legacy:
            return
        registry = er.async_get(self.hass)
        entry = registry.async_get(self.entity_id)
        if not entry:
            return
        object_id = entry.entity_id.split(".", 1)[1]
        if object_id.startswith(NAME_PREFIX):
            return
        new_object_id = self.suggested_object_id
        new_entity_id = f"{entry.domain}.{new_object_id}"
        if registry.async_get(new_entity_id) is None:
            registry.async_update_entity(entry.entity_id, new_entity_id=new_entity_id)
