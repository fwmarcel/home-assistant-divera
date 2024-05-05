"""Select Module for Divera Integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DATA_DIVERA_COORDINATOR, DATA_UCRS, DOMAIN
from .coordinator import DiveraCoordinator
from .divera import DiveraClient
from .entity import DiveraEntity, DiveraEntityDescription


@dataclass(frozen=True, kw_only=True)
class DiveraSensorEntityDescription(DiveraEntityDescription, SensorEntityDescription):
    """Description of a Divera sensor entity.

    Inherits from both DiveraEntityDescription and SensorEntityDescription.

    Attributes:
        value_fn (Callable[[DiveraClient], StateType]):
            Function that returns the value of the sensor.

    """

    value_fn: Callable[[DiveraClient], StateType]


SENSORS: tuple[DiveraSensorEntityDescription, ...] = (
    DiveraSensorEntityDescription(
        key="alarm",
        translation_key="alarm",
        icon="mdi:message-text",
        value_fn=lambda divera: divera.get_last_alarm(),
        attribute_fn=lambda divera: divera.get_last_alarm_attributes(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Divera sensor entities.

    Args:
        hass (HomeAssistant): Home Assistant instance.
        entry (ConfigEntry): Configuration entry for the integration.
        async_add_entities (AddEntitiesCallback): Function to add entities.

    """
    ucr_ids: list[int] = entry.data[DATA_UCRS]

    entities: list[DiveraSensorEntity] = []

    for ucr_id in ucr_ids:
        coordinator = hass.data[DOMAIN][entry.entry_id][ucr_id][DATA_DIVERA_COORDINATOR]

        entities.extend(
            [DiveraSensorEntity(coordinator, description) for description in SENSORS],
        )

    async_add_entities(entities, False)


class DiveraSensorEntity(DiveraEntity, SensorEntity):
    """Represents a Divera sensor entity.

    Inherits from both DiveraEntity and SensorEntity.

    Attributes:
        entity_description (DiveraSensorEntityDescription):
            Description of the sensor entity.

    """

    entity_description: DiveraSensorEntityDescription

    def __init__(
        self,
        coordinator: DiveraCoordinator,
        description: DiveraSensorEntityDescription,
    ) -> None:
        """Initialize DiveraSensorEntity.

        Args:
            coordinator (DiveraCoordinator): The coordinator managing this entity.
            description (DiveraSensorEntityDescription): Description of the sensor entity.

        """
        super().__init__(coordinator, description)

    def _divera_update(self) -> None:
        value = self.entity_description.value_fn(self.coordinator.data)
        self._attr_native_value = value
        attributes = self.entity_description.attribute_fn(self.coordinator.data)
        self._attr_extra_state_attributes = attributes
