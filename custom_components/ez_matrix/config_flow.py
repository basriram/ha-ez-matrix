import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_API_URL, DEFAULT_API_URL

class EzMatrixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EZ Matrix."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # You could validate the connection here if you wanted
            return self.async_create_entry(title="EZ Matrix", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema
        )
