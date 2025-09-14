"""Sensor platform for NOAA Space Weather."""

from .const import (
    DOMAIN,
    ICON,
    CONF_LEGACY_NAMING,
    DEFAULT_LEGACY_NAMING,
    NAME_PREFIX,
)
from .entity import NoaaSpaceWeatherEntity
from homeassistant.util import slugify


def sfi_return(coordinator):
    if not coordinator.data.get("sfi_data") is None:
        return coordinator.data.get("sfi_data").get("sfi")


def ai_return(coordinator):
    if not coordinator.data.get("a_index_data") is None:
        return coordinator.data.get("a_index_data", {}).get("a_index")


def ai_2d_return(coordinator):
    if not coordinator.data.get("a_index_data") is None:
        return coordinator.data.get("a_index_data", {}).get("a_2_day_index")


def ai_3d_return(coordinator):
    if not coordinator.data.get("a_index_data") is None:
        return coordinator.data.get("a_index_data", {}).get("a_3_day_index")


def kpi_return(coordinator):
    if not coordinator.data.get("kp_index_data") is None:
        kp = coordinator.data.get("kp_index_data", {})
        # Prefer fractional estimated Kp (e.g., 2.67) when available;
        # fall back to integer Kp if that's all we have.
        return (
            kp.get("estimated_kp")
            if kp.get("estimated_kp") is not None
            else kp.get("kp_index")
        )


def ssn_return(coordinator):
    if not coordinator.data.get("ssn_data") is None:
        return coordinator.data.get("ssn_data", {}).get("ssn")


def x1_return(coordinator):
    if not coordinator.data.get("probabilities_data") is None:
        return float(
            coordinator.data.get("probabilities_data", [{}])[0].get("x_class_1_day")
        )


def m1_return(coordinator):
    if not coordinator.data.get("probabilities_data") is None:
        return coordinator.data.get("probabilities_data", [{}])[0].get("m_class_1_day")


def polar_cap_absorption_return(coordinator):
    if not coordinator.data.get("probabilities_data") is None:
        return coordinator.data.get("probabilities_data", [{}])[0].get(
            "polar_cap_absorption"
        )


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensormap = [
        {
            "name": "SFI",
            "desc": "Solar Flux Index",
            "data": sfi_return,
        },
        {
            "name": "AI",
            "desc": "A Index",
            "data": ai_return,
        },
        {
            "name": "AI2D",
            "desc": "A Index 2 Day",
            "data": ai_2d_return,
        },
        {
            "name": "AI3D",
            "desc": "A Index 3 Day",
            "data": ai_3d_return,
        },
        {
            "name": "KPI",
            "desc": "Planetary K-Index",
            "data": kpi_return,
        },
        {
            "name": "SSN",
            "desc": "Sunspot Number",
            "data": ssn_return,
        },
        {
            "name": "PolarCapAbsorption",
            "desc": "Polar Cap Absorption",
            "data": polar_cap_absorption_return,
            "state_class": None,
            "icon": "mdi:sign-pole",
            "unit": None,
        },
        {
            "name": "x1",
            "icon": "mdi:sun-wireless",
            "desc": "X-Class 1 Day Probability",
            "data": x1_return,
            "unit": "%",
        },
        {
            "name": "m1",
            "icon": "mdi:sun-wireless-outline",
            "desc": "M-Class 1 Day Probability",
            "data": m1_return,
            "unit": "%",
        },
    ]
    async_add_devices(
        [NoaaSpaceWeatherSensor(coordinator, entry, sensor=s) for s in sensormap]
    )


class NoaaSpaceWeatherSensor(NoaaSpaceWeatherEntity):
    """noaa_space_weather Sensor class."""

    def __init__(self, coordinator, entry, sensor):
        self.sensor = sensor
        super().__init__(coordinator, entry)
        # unique id using existing scheme
        self._attr_unique_id = f"swpc {self.sensor['name']}"
        # Keep display name unchanged (legacy/human-friendly)
        self._attr_name = self.sensor["desc"]
        self._attr_icon = self.sensor.get("icon", ICON)
        self._attr_device_class = self.sensor.get(
            "device_class", "noaa_space_weather__custom_device_class"
        )

    @property
    def state_class(self):
        return self.sensor.get("state_class", "measurement")

    # Hass core expects _attr_native_unit_of_measurement or legacy unit_of_measurement;
    # keep property but suppress type issues via dynamic behavior
    @property
    def unit_of_measurement(self):  # type: ignore[override]
        return self.sensor.get("unit", "")

    @property
    def options(self):
        return self.sensor.get("options", None)

    @property
    def state(self):  # type: ignore[override]
        """Return the state of the sensor."""
        if self.coordinator.data:
            data = self.sensor["data"](self.coordinator)
            return data
        else:
            return None

    # unique_id and name provided via _attr_* in __init__

    @property
    def suggested_object_id(self) -> str:  # guides entity_id creation
        base = slugify(self.sensor["desc"]) or slugify(self.sensor["name"]) or "sensor"
        legacy = self.config_entry.options.get(
            CONF_LEGACY_NAMING, DEFAULT_LEGACY_NAMING
        )
        return base if legacy else f"{NAME_PREFIX}{base}"

    @property
    def available(self):  # type: ignore[override]
        """Always available if coordinator is present."""
        return True

    @property
    def icon(self):  # type: ignore[override]
        return self._attr_icon

    @property
    def device_class(self):  # type: ignore[override]
        return self._attr_device_class
