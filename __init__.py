from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TechnitiumApi
from .coordinator import TechnitiumBlockPauseDataUpdateCoordinator
from .const import (
    DOMAIN,
    PLATFORMS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_PAUSE_MIN,
    DEFAULT_PAUSE_MAX,
    DEFAULT_API_TIMEOUT,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Technitium Block Pause integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Technitium Block Pause from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data["host"]
    api_key = entry.data["api_key"]
    options = entry.options

    update_interval = options.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    pause_min = options.get("pause_min", DEFAULT_PAUSE_MIN)
    pause_max = options.get("pause_max", DEFAULT_PAUSE_MAX)
    api_timeout = options.get("api_timeout", DEFAULT_API_TIMEOUT)

    session = async_get_clientsession(hass)
    api = TechnitiumApi(host, api_key, session, api_timeout)
    coordinator = TechnitiumBlockPauseDataUpdateCoordinator(hass, api, update_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "pause_min": pause_min,
        "pause_max": pause_max,
    }

    async def handle_pause_service(call):
        duration = call.data.get("duration")
        pause_min = hass.data[DOMAIN][entry.entry_id]["pause_min"]
        pause_max = hass.data[DOMAIN][entry.entry_id]["pause_max"]
        if not isinstance(duration, int) or not (pause_min <= duration <= pause_max):
            # Invalid duration, ignore the call
            return
        await api.pause_ad_blocking(duration)
        await coordinator.async_request_refresh()

    async def handle_enable_service(call):
        await api.enable_ad_blocking()
        await coordinator.async_request_refresh()

    async def handle_disable_service(call):
        await api.disable_ad_blocking()
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "pause_ad_blocking", handle_pause_service)
    hass.services.async_register(DOMAIN, "enable_ad_blocking", handle_enable_service)
    hass.services.async_register(DOMAIN, "disable_ad_blocking", handle_disable_service)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove services if this is the last config entry
        if len(hass.data[DOMAIN]) == 1:
            hass.services.async_remove(DOMAIN, "pause_ad_blocking")
            hass.services.async_remove(DOMAIN, "enable_ad_blocking")
            hass.services.async_remove(DOMAIN, "disable_ad_blocking")

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
