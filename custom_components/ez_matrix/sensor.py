import logging
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
from .entity import EzMatrixEntity

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Sensor platform from a Config Entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api_url = data["api_url"]

    # Pass entry.entry_id
    async_add_entities([
        EzCascadeSensor(coordinator, entry.entry_id, api_url, "Cascade Mode"),
        EzStatusSensor(coordinator, entry.entry_id, api_url, "Device Status")
    ])

class EzCascadeSensor(EzMatrixEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, api_url, name):
        super().__init__(coordinator, entry_id, api_url)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_cascade_mode"

    @property
    def state(self):
        return self.coordinator.data.get("cascade_mode", "Unknown")

class EzStatusSensor(EzMatrixEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, api_url, name):
        super().__init__(coordinator, entry_id, api_url)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_device_status"

    @property
    def state(self):
        return self.coordinator.data.get("device_status", "Unknown")
