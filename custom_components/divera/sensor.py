"""Sensor for Divera 24/7 service."""

import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import (
    DEFAULT_SHORT_NAME,
    DOMAIN,
    DIVERA_COORDINATOR,
    DIVERA_DATA,
    DIVERA_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_entities
) -> None:
    """Set up the Divera sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    async_add_entities(
        [DiveraSensor(hass_data)],
        False,
    )


class DiveraSensor(Entity):
    """Implementation of a Divera sensor."""

    def __init__(self, hass_data):
        """Initialize the sensor."""
        self._connector = hass_data[DIVERA_DATA]
        self._coordinator = hass_data[DIVERA_COORDINATOR]

        self._name = f"{DEFAULT_SHORT_NAME} Alarm"
        self._unique_id = f"{DOMAIN}_{hass_data[DIVERA_NAME]}_alarm"
        self._icon = "mdi:message-text"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_last_alarm()

    @property
    def icon(self):
        """Return the icon for the entity card."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        return self._connector.get_last_alarm_attributes()

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    @property
    def available(self):
        """Return if state is available."""
        return self._connector.success and self._connector.latest_update is not None
