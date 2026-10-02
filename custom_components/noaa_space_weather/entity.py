"""NoaaSpaceWeatherEntity class"""

from homeassistant.components.image import ImageEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class NoaaSpaceWeatherImageEntity(CoordinatorEntity, ImageEntity):  # type: ignore[misc]
    """NOAA Space Weather Image Entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        ImageEntity.__init__(self, coordinator.hass)
        self.coordinator = coordinator
        self.config_entry = config_entry

    # Avoid overriding cached properties for attributes to satisfy type checkers.


class NoaaSpaceWeatherEntity(CoordinatorEntity):
    """NOAA Space Weather Entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
