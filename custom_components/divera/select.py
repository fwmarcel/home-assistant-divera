"""Sensor for Divera 24/7 service."""

import logging

from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.components.select import SelectEntity

from .const import (
    DEFAULT_SHORT_NAME,
    DIVERA_NAME,
    DOMAIN,
    DIVERA_COORDINATOR,
    DIVERA_DATA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_entities
) -> None:
    """Set up the Divera sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    async_add_entities(
        [DiveraStatusSelect(hass_data)],
        False,
    )


class DiveraStatusSelect(SelectEntity):
    """Implementation of a Divera sensor."""

    def __init__(self, hass_data):
        """Initialize the sensor."""
        self._connector = hass_data[DIVERA_DATA]
        self._coordinator = hass_data[DIVERA_COORDINATOR]

        self._name = f"{DEFAULT_SHORT_NAME} User Status"
        self._unique_id = f"{DOMAIN}_{hass_data[DIVERA_NAME]}_user_status"

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.info("Option: %s", option)
        id = self._connector.get_state_if_from_name(option)
        _LOGGER.info("ID: %s", id)
        self._connector.set_status(id)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def options(self):
        """Return the state of the sensor."""
        return self._connector.get_all_states()

    @property
    def current_option(self):
        return self._connector.get_state()

    @property
    def icon(self):
        """Return the icon for the entity card."""
        return "mdi:clock-time-nine-outline"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        return self._connector.get_state_attributes()

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
