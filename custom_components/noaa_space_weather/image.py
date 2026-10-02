"""Image platform for NOAA Space Weather."""

import asyncio
import logging
import random

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import (
    CONF_ENABLE_ANIMATIONS,
    CONF_LEGACY_NAMING,
    DEFAULT_ENABLE_ANIMATIONS,
    DEFAULT_LEGACY_NAMING,
    DOMAIN,
    ICON,
    NAME_PREFIX,
)
from .entity import NoaaSpaceWeatherImageEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up NOAA Space Weather image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    animationmap = [
        {
            "name": "SUVI Secondary 284 Angstroms",
            "product": "/products/animations/suvi-secondary-284.json",
            "device_class": "animation",
        },
        {
            "name": "SUVI Primary 171 Angstroms",
            "product": "/products/animations/suvi-primary-171.json",
            "device_class": "animation",
        },
        {
            "name": "SUVI Primary 304 Angstroms",
            "product": "/products/animations/suvi-primary-304.json",
            "device_class": "animation",
        },
        {
            "name": "SUVI Thematic Map",
            "product": "/products/animations/suvi-primary-map.json",
            "device_class": "animation",
        },
        {
            "name": "WFS Ionosphere",
            "product": "/products/animations/wam-ipe/wfs_ionosphere_new.json",
            "device_class": "animation",
        },
        {
            "name": "Coronagraph CCOR1",
            "product": "/products/animations/ccor1/ccor1.json",
            "device_class": "animation",
        },
        {
            "name": "Geospace Magnetosphere Velocity",
            "product": "/products/animations/geospace/velocity.json",
            "icon": "mdi:earth",
        },
        {
            "name": "Geospace Magnetosphere Density",
            "product": "/products/animations/geospace/density.json",
            "icon": "mdi:earth",
        },
        {
            "name": "Geospace Magnetosphere Pressure",
            "product": "/products/animations/geospace/pressure.json",
            "icon": "mdi:earth",
        },
        {
            "name": "Lasco C2",
            "product": "/products/animations/lasco-c2.json",
            "device_class": "animation",
        },
        {
            "name": "Lasco C3",
            "product": "/products/animations/lasco-c3.json",
            "device_class": "animation",
        },
        {
            "name": "Aurora Forecast North",
            "product": "/products/animations/ovation_north_24h.json",
            "icon": "mdi:aurora",
        },
        {
            "name": "Aurora Forecast South",
            "product": "/products/animations/ovation_south_24h.json",
            "icon": "mdi:aurora",
        },
        {
            "name": "Geoelectric Field US-Canada",
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

    animations_enabled = entry.options.get(
        CONF_ENABLE_ANIMATIONS, DEFAULT_ENABLE_ANIMATIONS
    )
    _LOGGER.info(
        "Setting up %d images and %d animations",
        len(imagemap),
        len(animationmap) if animations_enabled else 0,
    )

    entities = [
        *(NoaaSpaceWeatherImage(coordinator, entry, i) for i in imagemap),
        *(NoaaSpaceWeatherAnimation(coordinator, entry, i) for i in animationmap),
    ]
    async_add_entities(entities, update_before_add=True)

    # Kick off a background prefetch of all animations so they are ready shortly after setup
    try:
        products = (
            [a.get("product", "") for a in animationmap if a.get("product")]
            if animations_enabled
            else []
        )
        if products:
            coordinator.animation_prefetch_task = hass.async_create_task(
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

        self._attr_unique_id = f"swpc {self.image_data.get('name')}"
        base = self.image_data.get("name")
        self._attr_name = base
        self._attr_device_class = (
            f"noaa_space_weather__{self.image_data.get('device_class', 'image')}"
        )
        self._attr_icon = self.image_data.get("icon", ICON)

        self._jitter = random.uniform(2, 30)
        self._raw_bytes = None
        self._min_refresh_seconds = 300  # 5 minutes
        self._build_task = None

    async def async_update(self):
        image_bytes = b""
        if not self._raw_bytes:
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
                if self.entry.options.get(
                    CONF_ENABLE_ANIMATIONS, DEFAULT_ENABLE_ANIMATIONS
                ):
                    self._schedule_build()
            except Exception as err:  # pragma: no cover
                _LOGGER.error("%s: initial animation fetch failed: %s", self.name, err)
                raise
            return image_bytes

        try:
            _LOGGER.debug("%s: refreshing full animation", self.name)
            if self.entry.options.get(
                CONF_ENABLE_ANIMATIONS, DEFAULT_ENABLE_ANIMATIONS
            ):
                image_bytes = await self.coordinator.api.async_load_animation(
                    self.image_data.get("product", ""), bypass_cache=True
                )
            else:
                image_bytes = await self.coordinator.api.async_get_first_frame(
                    self.image_data.get("product", "")
                )
            self._set_cached(image_bytes)
            self.async_write_ha_state()
        except Exception as err:  # pragma: no cover
            _LOGGER.error("%s: animation refresh failed: %s", self.name, err)
            raise
        return image_bytes

    async def _build_animation_with_jitter(self, *, refresh: bool = False):
        try:
            try:
                await asyncio.sleep(self._jitter)
            except asyncio.CancelledError:  # pragma: no cover
                _LOGGER.debug("%s: background animation build cancelled", self.name)
                return
            image_bytes = await self.coordinator.api.async_load_animation(
                self.image_data["product"], bypass_cache=refresh
            )
            if image_bytes:
                self._set_cached(image_bytes)
                self.async_write_ha_state()
            _LOGGER.debug(
                "%s: background animation ready (size=%d)", self.name, len(image_bytes)
            )
        except Exception as err:  # pragma: no cover
            _LOGGER.debug("%s: background animation failed: %s", self.name, err)
        finally:
            self._build_task = None

    def _schedule_build(self, *, refresh: bool = False):
        if self._build_task and not self._build_task.done():
            _LOGGER.debug(
                "%s: build already in progress; skipping new schedule", self.name
            )
            return
        self._build_task = self.hass.async_create_task(
            self._build_animation_with_jitter(refresh=refresh)
        )

    async def async_will_remove_from_hass(self) -> None:
        """Stop background work when this image entity is removed."""
        if self._build_task and not self._build_task.done():
            self._build_task.cancel()
            try:
                await self._build_task
            except asyncio.CancelledError:
                pass
        await super().async_will_remove_from_hass()

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
        if not image_bytes:
            return
        self._raw_bytes = image_bytes
        self.image_last_updated = dt_util.utcnow()
        self._attr_image_last_updated = self.image_last_updated
        try:
            self._attr_content_type = self._detect_mime(image_bytes)
        except Exception:  # pragma: no cover
            self._attr_content_type = "application/octet-stream"

    @callback
    def _handle_coordinator_update(self):
        # image_last_updated describes the bytes being served. A coordinator
        # tick alone does not make those bytes newer; fetch a refreshed GIF.
        if self.entry.options.get(CONF_ENABLE_ANIMATIONS, DEFAULT_ENABLE_ANIMATIONS):
            self._schedule_build(refresh=True)
        self.async_write_ha_state()

    async def async_image(self):
        if not self._raw_bytes:
            return await self.async_update()
        try:
            if self.image_last_updated:
                age = (dt_util.utcnow() - self.image_last_updated).total_seconds()
                if age >= self._min_refresh_seconds:
                    _LOGGER.debug(
                        "%s: image age %.1fs >= %ss threshold; refreshing",
                        self.name,
                        age,
                        self._min_refresh_seconds,
                    )
                    try:
                        refreshed = await self.async_update()
                    except Exception:
                        # Keep serving the last good frame/animation during an
                        # upstream outage instead of breaking the image entity.
                        _LOGGER.debug(
                            "%s: serving stale animation after refresh failure",
                            self.name,
                        )
                        return self._raw_bytes
                    return refreshed or self._raw_bytes
                else:
                    _LOGGER.debug(
                        "%s: image age %.1fs < %ss threshold; serving cached",
                        self.name,
                        age,
                        self._min_refresh_seconds,
                    )
        except Exception:  # pragma: no cover
            pass
        return self._raw_bytes

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
        self.image_last_updated = dt_util.utcnow()
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
