from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class EzMatrixEntity(CoordinatorEntity):
    """Base class for EZ Matrix entities."""

    def __init__(self, coordinator, entry_id, api_url):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._api_url = api_url

    @property
    def device_info(self):
        """Return information to link this entity with the device."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "EZ Matrix Controller",
            "manufacturer": "Custom DIY",
            "model": "Serial MQTT Matrix",
            "sw_version": "1.2.0",
            "configuration_url": self._api_url,
        }
