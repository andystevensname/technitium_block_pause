
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv


class TechnitiumBlockPauseOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        options = self._config_entry.options
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional("update_interval", default=options.get("update_interval", 30)): vol.All(int, vol.Range(min=5, max=3600)),
            vol.Optional("pause_min", default=options.get("pause_min", 1)): vol.All(int, vol.Range(min=1, max=3600)),
            vol.Optional("pause_max", default=options.get("pause_max", 3600)): vol.All(int, vol.Range(min=1, max=86400)),
            vol.Optional("api_timeout", default=options.get("api_timeout", 10)): vol.All(int, vol.Range(min=1, max=60)),
        })
        return self.async_show_form(step_id="init", data_schema=data_schema)
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_KEY
from .const import DOMAIN

class TechnitiumBlockPauseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    @staticmethod
    def async_get_options_flow(config_entry):
        return TechnitiumBlockPauseOptionsFlowHandler(config_entry)
    async def async_step_user(self, user_input=None):
        # Validate user input for host and API key
        import re
        from urllib.parse import urlparse
        errors = {}
        if user_input is not None:
            host = user_input.get(CONF_HOST, "")
            api_key = user_input.get(CONF_API_KEY, "")
            parsed = urlparse(host)
            if not (parsed.scheme in ("http", "https") and parsed.netloc):
                errors[CONF_HOST] = "invalid_host"
            if not api_key or not re.match(r"^[A-Za-z0-9-_]+$", api_key):
                errors[CONF_API_KEY] = "invalid_api_key"
            if not errors:
                return self.async_create_entry(title="Technitium Block Pause", data=user_input)
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_API_KEY): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
