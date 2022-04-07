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
    VEHICLE_ICON,
    VEHICLE_ENABLED_DEFAULT,
)
from .data import Vehicle

_LOGGER = logging.getLogger(__name__)

# Sensor types are defined as:
#   variable -> [0]title, [1]device_class, [2]units, [3]icon, [4]enabled_by_default
SENSOR_TYPES = {
    "last_alarm": [
        "Alarm",
        "mdi:message-text",
        True,
    ],
    "state": [
        "State",
        "mdi:phone-forward",
        True,
    ],
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_entities
) -> None:
    """Set up the Divera sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    async_add_entities(
        [DiveraSensor(hass_data, sensor_type) for sensor_type in SENSOR_TYPES],
        False,
    )
    # await async_setup_vehicle_entry(async_setup_entry)

class DiveraVehicleSensor(Entity):
    """ TODO Beschreibung """

    def __init__(self, hass_data, vehicle: Vehicle):
        """Initialize the sensor."""
        self._connector = hass_data[DIVERA_DATA]
        self._coordinator = hass_data[DIVERA_COORDINATOR]

        self._name = vehicle.get_name()
        self._unique_id = f"{DOMAIN}_{hass_data[DIVERA_NAME]}_{vehicle.get_name()}"
        self._state = vehicle.get_fms_state()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        """Return the icon for the entity card."""
        return VEHICLE_ICON

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
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return VEHICLE_ENABLED_DEFAULT

    @property
    def available(self):
        """Return if state is available."""
        return self._connector.success and self._connector.latest_update is not None


class DiveraSensor(Entity):
    """Implementation of a Divera sensor."""

    def __init__(self, hass_data, sensor_type):
        """Initialize the sensor."""
        self._connector = hass_data[DIVERA_DATA]
        self._coordinator = hass_data[DIVERA_COORDINATOR]

        self._type = sensor_type
        self._name = f"{DEFAULT_SHORT_NAME} {SENSOR_TYPES[self._type][0]}"
        self._unique_id = (
            f"{DOMAIN}_{hass_data[DIVERA_NAME]}_{SENSOR_TYPES[self._type][0]}"
        )

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
        result = ""
        if self._type == "last_alarm":
            result = self._connector.get_last_alarm()
        elif self._type == "state":
            result = self._connector.get_state()
        return result

    @property
    def icon(self):
        """Return the icon for the entity card."""
        value = SENSOR_TYPES[self._type][1]
        return value

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        attributes = {}
        if self._type == "last_alarm":
            attributes = self._connector.get_last_alarm_attributes()
        elif self._type == "state":
            attributes = self._connector.get_state_attributes()

        return attributes

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
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return SENSOR_TYPES[self._type][2]

    @property
    def available(self):
        """Return if state is available."""
        return self._connector.success and self._connector.latest_update is not None
