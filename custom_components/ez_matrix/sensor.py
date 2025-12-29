import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Select platform from a Config Entry."""
    data = hass.data[DOMAIN][entry.entry_id] # Access data via entry_id
    coordinator = data["coordinator"]
    api_url = data["api_url"]

    async_add_entities([
        EzCascadeSensor(coordinator, "Cascade Mode"),
        EzStatusSensor(coordinator, "Device Status")
    ])

class EzCascadeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = "ez_cascade_mode"

    @property
    def state(self):
        return self.coordinator.data.get("cascade_mode", "Unknown")

class EzStatusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = "ez_device_status"

    @property
    def state(self):
        return self.coordinator.data.get("device_status", "Unknown")
