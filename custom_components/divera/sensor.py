"""Sensor for Divera 24/7 service."""

import logging

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import (
    DOMAIN,
    DIVERA_COORDINATOR,
    DIVERA_DATA,
    INTEGRATION_FULL_NAME,
    DIVERA_GMBH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigType, async_add_entities) -> None:
    """Set up the Divera sensor platform."""
    hass_data_all = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for index in hass_data_all:
        hass_data = hass_data_all[index]
        entities.append(DiveraAlarmSensor(hass_data))
    async_add_entities(
        entities,
        False,
    )


class DiveraAlarmSensor(Entity):
    """Implementation of a Divera Alarm Sensor.

    This class represents a sensor entity that retrieves data from Divera.

    """

    def __init__(self, hass_data):
        """Initialize the sensor.

        Args:
            hass_data (dict): Data from Home Assistant.

        """
        self._connector = hass_data[DIVERA_DATA]
        self._coordinator = hass_data[DIVERA_COORDINATOR]

        self._ucr_id = self._connector.get_active_ucr()
        self._cluster_name = self._connector.get_cluster_name_from_ucr(self._ucr_id)

        self._name = f"{self._cluster_name} Alarm"
        self._unique_id = f"{DOMAIN}_{self._ucr_id}_alarm"
        self._icon = "mdi:message-text"

    @property
    def name(self):
        """Return the name of the sensor.

        Returns:
            str: The name of the sensor.

        """
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor.

        Returns:
            str: The unique ID of the sensor.

        """
        return self._unique_id

    @property
    def state(self) -> str:
        """Return the state of the sensor.

        Returns:
            str: The state of the sensor.

        """
        return self._connector.get_last_alarm()

    @property
    def icon(self):
        """Return the icon for the entity card.

        Returns:
            str: The icon for the entity card.

        """
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device.

        Returns:
            dict: The state attributes of the device.

        """
        return self._connector.get_last_alarm_attributes()

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data.

        This method sets up a listener for state updates and loads data accordingly.

        """
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Schedule a custom update via the common entity update service.

        This method schedules a custom update by requesting a refresh through the coordinator.

        """
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Return whether entities should be polled.

        Returns:
            bool: False, as entities do not individually poll.

        """
        return False

    @property
    def available(self) -> bool:
        """Return whether the component is available.

        Returns:
            bool: True if the component is available, False otherwise.

        """
        return self._connector.success and self._connector.latest_update is not None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information.

        Returns:
            DeviceInfo: Device information object.

        """
        version = self._connector.get_cluster_version()
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._ucr_id))},
            serial_number=str(self._ucr_id),
            name=self._cluster_name,
            manufacturer=DIVERA_GMBH,
            model=INTEGRATION_FULL_NAME,
            sw_version=version,
        )
