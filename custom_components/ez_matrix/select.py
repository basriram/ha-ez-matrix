import logging
from homeassistant.components.select import SelectEntity
from .const import DOMAIN
from .entity import EzMatrixEntity  # Import the new base class

_LOGGER = logging.getLogger(__name__)

SOURCE_OPTIONS = ["IN1", "IN2", "IN3", "IN4"]
EDID_OPTIONS = [str(i) for i in range(17)]

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Select platform from a Config Entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api_url = data["api_url"]
    session = data["session"]

    entities = []

    # Pass entry.entry_id to the constructors so they can link to the device
    entities.append(EzOutputSelect(coordinator, entry.entry_id, api_url, session, 1, "Output 1 Source"))
    entities.append(EzOutputSelect(coordinator, entry.entry_id, api_url, session, 2, "Output 2 Source"))

    entities.append(EzEdidSelect(coordinator, entry.entry_id, api_url, session, 1, "Input 1 EDID Index"))
    entities.append(EzEdidSelect(coordinator, entry.entry_id, api_url, session, 2, "Input 2 EDID Index"))
    entities.append(EzEdidSelect(coordinator, entry.entry_id, api_url, session, 3, "Input 3 EDID Index"))
    entities.append(EzEdidSelect(coordinator, entry.entry_id, api_url, session, 4, "Input 4 EDID Index"))

    async_add_entities(entities)


class EzOutputSelect(EzMatrixEntity, SelectEntity):
    """Representation of a Video Output Source selector."""

    def __init__(self, coordinator, entry_id, api_url, session, output_num, name):
        super().__init__(coordinator, entry_id, api_url) # Init base class
        self._session = session
        self._output_num = output_num
        self._attr_name = name
        # Unique ID must be truly unique (combining entry_id helps if you have multiple devices)
        self._attr_unique_id = f"{entry_id}_output_{output_num}_source"
        self._attr_options = SOURCE_OPTIONS

    @property
    def current_option(self):
        key = f"output_{self._output_num}_source"
        val = self.coordinator.data.get("outputs", {}).get(key, "Unknown")
        return val if val in SOURCE_OPTIONS else None

    async def async_select_option(self, option: str) -> None:
        input_num = int(option.split(" ")[-1])
        payload = {"output_number": self._output_num, "input_number": input_num}
        try:
            async with self._session.post(f"{self._api_url}/output/switch", json=payload) as resp:
                if resp.status == 200:
                    await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Error sending command: {e}")


class EzEdidSelect(EzMatrixEntity, SelectEntity):
    """Representation of an Input EDID selector."""

    def __init__(self, coordinator, entry_id, api_url, session, input_num, name):
        super().__init__(coordinator, entry_id, api_url)
        self._session = session
        self._input_num = input_num
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_input_{input_num}_edid"
        self._attr_options = EDID_OPTIONS

    @property
    def current_option(self):
        key = f"input_{self._input_num}_edid_index"
        val = self.coordinator.data.get("inputs_edid_index", {}).get(key, "0")
        return str(val)

    async def async_select_option(self, option: str) -> None:
        payload = {"input_number": self._input_num, "edid_index": int(option)}
        try:
            async with self._session.post(f"{self._api_url}/edid/set", json=payload) as resp:
                if resp.status == 200:
                    await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Error sending command: {e}")
