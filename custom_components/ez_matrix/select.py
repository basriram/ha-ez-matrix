import logging
import aiohttp
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Options available in the dropdowns
SOURCE_OPTIONS = ["Input 1", "Input 2", "Input 3", "Input 4"]
EDID_OPTIONS = [str(i) for i in range(17)] # "0" to "16"

async def async_setup_entry(hass, entry, async_add_entities):

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api_url = data["api_url"]
    session = data["session"]

    entities = []

    # --- Output Source Selectors ---
    entities.append(EzOutputSelect(coordinator, api_url, session, 1, "Output 1 Source"))
    entities.append(EzOutputSelect(coordinator, api_url, session, 2, "Output 2 Source"))
    # --- Input EDID Selectors ---
    entities.append(EzEdidSelect(coordinator, api_url, session, 1, "Input 1 EDID Index"))
    entities.append(EzEdidSelect(coordinator, api_url, session, 2, "Input 2 EDID Index"))
    entities.append(EzEdidSelect(coordinator, api_url, session, 3, "Input 3 EDID Index"))
    entities.append(EzEdidSelect(coordinator, api_url, session, 4, "Input 4 EDID Index"))

    async_add_entities(entities)


class EzOutputSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Video Output Source selector."""

    def __init__(self, coordinator, api_url, session, output_num, name):
        super().__init__(coordinator)
        self._api_url = api_url
        self._session = session
        self._output_num = output_num
        self._attr_name = name
        self._attr_unique_id = f"ez_output_{output_num}_source"
        self._attr_options = SOURCE_OPTIONS

    @property
    def current_option(self):
        """Return the current selected option based on coordinator data."""
        # Data structure from your python script: 
        # {"outputs": {"output_1_source": "Input 1", ...}}
        key = f"output_{self._output_num}_source"
        val = self.coordinator.data.get("outputs", {}).get(key, "Unknown")
        
        # Ensure format matches options (e.g., "Input 1")
        return val if val in SOURCE_OPTIONS else None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Parse "Input 1" -> 1
        input_num = int(option.split(" ")[-1])
        
        payload = {"output_number": self._output_num, "input_number": input_num}
        
        try:
            async with self._session.post(f"{self._api_url}/output/switch", json=payload) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to switch output")
                else:
                    # Trigger an immediate update to reflect state
                    await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Error sending command: {e}")


class EzEdidSelect(CoordinatorEntity, SelectEntity):
    """Representation of an Input EDID selector."""

    def __init__(self, coordinator, api_url, session, input_num, name):
        super().__init__(coordinator)
        self._api_url = api_url
        self._session = session
        self._input_num = input_num
        self._attr_name = name
        self._attr_unique_id = f"ez_input_{input_num}_edid"
        self._attr_options = EDID_OPTIONS

    @property
    def current_option(self):
        """Return the current selected option."""
        # Data structure: {"inputs_edid_index": {"input_1_edid_index": "2", ...}}
        key = f"input_{self._input_num}_edid_index"
        val = self.coordinator.data.get("inputs_edid_index", {}).get(key, "0")
        return str(val)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        edid_index = int(option)
        
        payload = {"input_number": self._input_num, "edid_index": edid_index}
        
        try:
            async with self._session.post(f"{self._api_url}/edid/set", json=payload) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to set EDID")
                else:
                    await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Error sending command: {e}")
