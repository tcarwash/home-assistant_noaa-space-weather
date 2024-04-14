"""NoaaSpaceWeatherEntity class"""

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.image import ImageEntity

from .const import ATTRIBUTION
from .const import DOMAIN


class NoaaSpaceWeatherImageEntity(CoordinatorEntity, ImageEntity):
    """NOAA Space Weather Image Entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        ImageEntity.__init__(self, coordinator.hass)
        self.coordinator = coordinator
        self.config_entry = config_entry

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
            "last_updated": self.image_last_updated,
        }


class NoaaSpaceWeatherEntity(CoordinatorEntity):
    """NOAA Space Weather Entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
