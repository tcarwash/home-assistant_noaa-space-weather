"""Sensor platform for NOAA Space Weather."""

from .const import DOMAIN
from .const import ICON
from .entity import NoaaSpaceWeatherEntity


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
        return coordinator.data.get("kp_index_data", {}).get("kp_index")


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

    @property
    def state_class(self):
        return self.sensor.get("state_class", "measurement")

    @property
    def unit_of_measurement(self):
        return self.sensor.get("unit", "")

    @property
    def options(self):
        return self.sensor.get("options", None)

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            data = self.sensor["data"](self.coordinator)
            return data
        else:
            return None

    @property
    def unique_id(self):
        return f"swpc {self.sensor['name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.sensor["desc"]

    @property
    def available(self):
        """Return the state of the sensor."""
        return True

    @property
    def icon(self):
        """Return the icon of the sensor."""
        try:
            icon = self.sensor["icon"]
        except KeyError:
            icon = ICON
        return icon

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self.sensor.get(
            "device_class", "noaa_space_weather__custom_device_class"
        )
