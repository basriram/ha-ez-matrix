import logging
import asyncio
import async_timeout
import aiohttp
import json
from datetime import timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components import mqtt

from .const import DOMAIN, CONF_API_URL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "select"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component using YAML (deprecated but required hook)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up EZ Matrix from a config entry."""
    
    # 1. Get API URL from Config
    api_url = entry.data[CONF_API_URL]
    mqtt_topic = "serial/status" # This could also be a config option if desired

    session = aiohttp.ClientSession()
    
    # 2. Define the REST Polling Function
    async def async_update_data():
        """Fetch data from the REST API (Fallback/Sync)."""
        try:
            async with async_timeout.timeout(10):
                async with session.get(f"{api_url}/status") as response:
                    return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    # 3. Initialize Coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="ez_matrix_sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    # 4. Define MQTT Callback
    @callback
    def mqtt_message_received(msg):
        """Handle incoming MQTT status messages."""
        try:
            payload = json.loads(msg.payload)
            if "current_state" in payload:
                new_data = payload["current_state"]
                coordinator.async_set_updated_data(new_data)
                _LOGGER.debug(f"Updated EZ Matrix state via MQTT: {new_data}")
        except Exception as e:
            _LOGGER.error(f"Error processing EZ Matrix MQTT message: {e}")

    # 5. Subscribe to MQTT Topic
    # We store the unsubscribe callback so we can clean up later
    unsubscribe_mqtt = await mqtt.async_subscribe(hass, mqtt_topic, mqtt_message_received)

    # 6. Store data for platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "session": session,
        "api_url": api_url,
        "unsubscribe_mqtt": unsubscribe_mqtt
    }

    # 7. Forward setup to platforms (sensor, select)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        
        # Close aiohttp session
        await data["session"].close()
        
        # Unsubscribe from MQTT
        data["unsubscribe_mqtt"]()

    return unload_ok
