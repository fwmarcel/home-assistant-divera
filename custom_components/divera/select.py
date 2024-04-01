"""Select Module for Divera Integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import DiveraCoordinator
from .const import DOMAIN, DATA_UCRS, DATA_DIVERA_COORDINATOR
from .divera import DiveraClient, DiveraError
from .entity import DiveraEntity, DiveraEntityDescription


@dataclass(frozen=True, kw_only=True)
class DiveraSelectEntityDescription(DiveraEntityDescription, SelectEntityDescription):
    """Description of a selectable Divera entity.

    Inherits from both DiveraEntityDescription and SelectEntityDescription.

    Attributes:
        current_option_fn (Callable[[DiveraClient], StateType]):
            Function that returns the current selected option.
        options_fn (Callable[[DiveraClient], list[str]]):
            Function that returns the list of available options.
        select_option_fn (Callable[[DiveraClient, str], Any]):
            Function that selects an option.

    """

    current_option_fn: Callable[[DiveraClient], StateType]
    options_fn: Callable[[DiveraClient], list[str]]
    select_option_fn: Callable[[DiveraClient, str], Any]


SENSORS: tuple[DiveraSelectEntityDescription, ...] = (
    DiveraSelectEntityDescription(
        key="user_status",
        translation_key="user_status",
        icon="mdi:clock-time-nine-outline",
        current_option_fn=lambda divera: divera.get_user_state(),
        options_fn=lambda divera: divera.get_all_state_name(),
        attribute_fn=lambda divera: divera.get_user_state_attributes(),
        select_option_fn=lambda divera, option: divera.set_user_state_by_name(option),
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback, ) -> None:
    """Set up Divera select entities.

    Args:
        hass (HomeAssistant): Home Assistant instance.
        entry (ConfigEntry): Configuration entry for the integration.
        async_add_entities (AddEntitiesCallback): Function to add entities.

    """
    ucr_ids: list[int] = entry.data[DATA_UCRS]

    entities: list[DiveraSelectEntity] = []

    for ucr_id in ucr_ids:
        coordinator = hass.data[DOMAIN][entry.entry_id][ucr_id][DATA_DIVERA_COORDINATOR]

        entities.extend(
            [DiveraSelectEntity(coordinator, description) for description in SENSORS],
        )

    async_add_entities(entities, False)


class DiveraSelectEntity(DiveraEntity, SelectEntity):
    """Represents a selectable Divera entity.

    Inherits from both DiveraEntity and SelectEntity.

    Attributes:
        entity_description (DiveraSelectEntityDescription):
            Description of the selectable entity.

    """

    entity_description: DiveraSelectEntityDescription

    def __init__(
            self,
            coordinator: DiveraCoordinator,
            description: DiveraSelectEntityDescription,
    ) -> None:
        """Initialize DiveraSelectEntity.

        Args:
            coordinator (DiveraCoordinator): The coordinator managing this entity.
            description (DiveraSelectEntityDescription): Description of the selectable entity.

        """
        super().__init__(coordinator, description)

    def _divera_update(self) -> None:
        option = self.entity_description.current_option_fn(self.coordinator.data)
        self._attr_current_option = option

        options = self.entity_description.options_fn(self.coordinator.data)
        self._attr_options = options

        attributes = self.entity_description.attribute_fn(self.coordinator.data)
        self._attr_extra_state_attributes = attributes

    async def async_select_option(self, option: str) -> None:
        """Select an option asynchronously.

        Args:
            option (str): The option to select.

        Raises:
            HomeAssistantError: If an error occurs while selecting the option.

        """
        try:
            await self.entity_description.select_option_fn(self.coordinator.data, option)
        except DiveraError as exc:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="user_state_error",
                translation_placeholders={
                    "cluster_name": self.cluster_name,
                },
            ) from exc
