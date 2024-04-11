"""Camera platform for NOAA Space Weather."""
from .const import DOMAIN
from .const import ATTRIBUTION
from .entity import NoaaSpaceWeatherImageEntity
from homeassistant.components.image import ImageEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup camera platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    imagemap = [
        {
            "name": "aurora_forecast_north",
            "image_url": "https://services.swpc.noaa.gov/images/animations/ovation/north/latest.jpg",
        },
        {
            "name": "aurora_forecast_south",
            "image_url": "https://services.swpc.noaa.gov/images/animations/ovation/south/latest.jpg",
        },
        {
            "name": "goes_195_angstroms",
            "image_url": "https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png",
        },
        {
            "name": "cme",
            "image_url": "https://services.swpc.noaa.gov/images/animations/lasco-c3/latest.jpg",
        },
    ]
    async_add_devices(
        [NoaaSpaceWeatherImage(coordinator, entry, image=i) for i in imagemap]
    )


class NoaaSpaceWeatherImage(NoaaSpaceWeatherImageEntity):
    """noaa_space_weather Image class."""

    def __init__(self, coordinator, entry, image):
        self.image = image
        self.entry = entry
        self.coordinator = coordinator
        super().__init__(coordinator, entry)

    @property
    def name(self):
        return self.image.get("name")

    @property
    def image_url(self):
        return self.image.get("image_url")