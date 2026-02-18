import re
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TechnitiumApi
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_PAUSE_MIN,
    DEFAULT_PAUSE_MAX,
    DEFAULT_API_TIMEOUT,
)


class TechnitiumBlockPauseOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Technitium Block Pause."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        options = self._config_entry.options
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(
                "update_interval",
                default=options.get("update_interval", DEFAULT_UPDATE_INTERVAL),
            ): vol.All(int, vol.Range(min=5, max=3600)),
            vol.Optional(
                "pause_min",
                default=options.get("pause_min", DEFAULT_PAUSE_MIN),
            ): vol.All(int, vol.Range(min=1, max=3600)),
            vol.Optional(
                "pause_max",
                default=options.get("pause_max", DEFAULT_PAUSE_MAX),
            ): vol.All(int, vol.Range(min=1, max=86400)),
            vol.Optional(
                "api_timeout",
                default=options.get("api_timeout", DEFAULT_API_TIMEOUT),
            ): vol.All(int, vol.Range(min=1, max=60)),
        })
        return self.async_show_form(step_id="init", data_schema=data_schema)


class TechnitiumBlockPauseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Technitium Block Pause."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TechnitiumBlockPauseOptionsFlowHandler:
        """Get the options flow for this handler."""
        return TechnitiumBlockPauseOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input.get(CONF_HOST, "").rstrip("/")
            api_key = user_input.get(CONF_API_KEY, "")

            # Validate URL format
            parsed = urlparse(host)
            if not (parsed.scheme in ("http", "https") and parsed.netloc):
                errors[CONF_HOST] = "invalid_host"

            # Validate API key format
            if not api_key or not re.match(r"^[A-Za-z0-9-_]+$", api_key):
                errors[CONF_API_KEY] = "invalid_api_key"

            # Test connection if no format errors
            if not errors:
                session = async_get_clientsession(self.hass)
                api = TechnitiumApi(host, api_key, session, DEFAULT_API_TIMEOUT)
                result = await api.get_status()

                if result.get("ad_blocking_status") is None:
                    errors["base"] = "cannot_connect"
                else:
                    # Normalize the host (remove trailing slash)
                    user_input[CONF_HOST] = host
                    return self.async_create_entry(
                        title=DEFAULT_NAME,
                        data=user_input,
                    )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_API_KEY): str,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
