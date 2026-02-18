from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Technitium switch from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    async_add_entities([TechnitiumBlockingSwitch(coordinator, api, entry)])


class TechnitiumBlockingSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to toggle Technitium ad blocking."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, api, entry: ConfigEntry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = api
        self._entry = entry
        self._attr_name = "Ad Blocking"
        self._attr_unique_id = f"{entry.entry_id}_ad_blocking_switch"

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        return "mdi:shield-check" if self.is_on else "mdi:shield-off"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title or DEFAULT_NAME,
            manufacturer="Technitium",
            model="DNS Server",
            configuration_url=self._entry.data.get("host"),
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if blocking is enabled."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("ad_blocking_status")

    async def async_turn_on(self, **kwargs) -> None:
        """Enable ad blocking."""
        await self._api.enable_ad_blocking()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable ad blocking."""
        await self._api.disable_ad_blocking()
        await self.coordinator.async_request_refresh()
