from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "technitium-block-pause"

async def async_setup(hass: HomeAssistant, config: dict):
    # Set up the Technitium Block Pause integration (no config needed)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Set up Technitium Block Pause from a config entry
    from .api import TechnitiumApi
    from .coordinator import TechnitiumBlockPauseDataUpdateCoordinator
    hass.data.setdefault(DOMAIN, {})
    host = entry.data["host"]
    api_key = entry.data["api_key"]
    options = entry.options
    update_interval = options.get("update_interval", 30)
    pause_min = options.get("pause_min", 1)
    pause_max = options.get("pause_max", 3600)
    api_timeout = options.get("api_timeout", 10)
    api = TechnitiumApi(host, api_key, api_timeout)
    coordinator = TechnitiumBlockPauseDataUpdateCoordinator(hass, api, update_interval)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {"api": api, "coordinator": coordinator, "pause_min": pause_min, "pause_max": pause_max}

    async def handle_pause_service(call):
        duration = call.data.get("duration")
        pause_min = hass.data[DOMAIN][entry.entry_id]["pause_min"]
        pause_max = hass.data[DOMAIN][entry.entry_id]["pause_max"]
        if not isinstance(duration, int) or not (pause_min <= duration <= pause_max):
            # Invalid duration, ignore the call
            return
        await api.pause_ad_blocking(duration)
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, "pause_ad_blocking", handle_pause_service
    )

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Unload a config entry and close aiohttp session
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    await api.close()
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
