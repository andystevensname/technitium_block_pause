from homeassistant.components.sensor import SensorEntity
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
    """Set up Technitium sensor from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([TechnitiumBlockingStatusSensor(coordinator, entry)])


class TechnitiumBlockingStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing Technitium blocking status."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "Blocking Status"
        self._attr_unique_id = f"{entry.entry_id}_blocking_status"

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        if self.state == "enabled":
            return "mdi:shield-check"
        elif self.state == "paused":
            return "mdi:shield-half-full"
        return "mdi:shield-off"

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
    def state(self) -> str:
        """Return the blocking status."""
        if self.coordinator.data is None:
            return "unknown"
        
        enable_blocking = self.coordinator.data.get("enable_blocking", True)
        temp_disable_till = self.coordinator.data.get("temp_disable_till")
        
        if not enable_blocking:
            return "disabled"
        elif temp_disable_till:
            return "paused"
        return "enabled"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        
        return {
            "enable_blocking": self.coordinator.data.get("enable_blocking"),
            "temporary_disable_until": self.coordinator.data.get("temp_disable_till"),
        }
