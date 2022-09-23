"""Sensor platform for NOAA Space Weather."""
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SENSOR
from .entity import NoaaSpaceWeatherEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensormap = [
        {'name': 'SFI', 'desc': 'Solar Flux Index', 'data': coordinator.data['sfi_data']['sfi']},
        {'name': 'KPI', 'desc': 'Planetary K-Index', 'data': coordinator.data['kp_index_data']['kp_index']},
        {'name': 'SSN', 'desc': 'Smoothed SSN', 'data': coordinator.data['smoothed_ssn_data']['last_ssn']['smoothed_ssn'] or coordinator.data['smoothed_ssn_data']['smoothed_ssn']},
        {'name': 'x1', 'icon': 'mdi:sun-wireless', 'desc': 'X-Class 1 Day Probability', 'data': coordinator.data['probabilities_data'][0]['x_class_1_day']},
        {'name': 'm1', 'icon': 'mdi:sun-wireless-outline', 'desc': 'M-Class 1 Day Probability', 'data': coordinator.data['probabilities_data'][0]['m_class_1_day']},
    ]
    async_add_devices(
        [
            NoaaSpaceWeatherSensor(coordinator, entry, sensor=s) for s in sensormap
        ]
    )


class NoaaSpaceWeatherSensor(NoaaSpaceWeatherEntity):
    """noaa_space_weather Sensor class."""
    def __init__(self, coordinator, entry, sensor):
        self.sensor = sensor
        super().__init__(coordinator, entry)

    @property
    def unique_id(self):
        return f"swpc {self.sensor['name']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.sensor['desc']

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.sensor['data']

    @property
    def available(self):
        """Return the state of the sensor."""
        return True

    @property
    def icon(self):
        """Return the icon of the sensor."""
        try:
            icon = self.sensor['icon']
        except KeyError:
            icon = ICON
        return icon

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "noaa_space_weather__custom_device_class"
