"""Entity Module for Divera Integration."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DIVERA_GMBH, DIVERA_BASE_URL
from .coordinator import DiveraCoordinator
from .divera import DiveraClient


@dataclass(frozen=True, kw_only=True)
class DiveraEntityDescription(EntityDescription):
    """Description of a Divera entity.

    Attributes:
        attribute_fn (Callable[[DiveraClient], MutableMapping[str, Any]]):
            Function that returns a mapping of attributes for the entity,
            based on a DiveraClient instance.

    """

    attribute_fn: Callable[[DiveraClient], MutableMapping[str, Any]]


class DiveraEntity(CoordinatorEntity[DiveraCoordinator]):
    """Represents a Divera entity.

    Attributes:
        entity_description (DiveraEntityDescription):
            Description of the entity.

    """

    _attr_has_entity_name = True
    entity_description: DiveraEntityDescription

    def __init__(
            self,
            coordinator: DiveraCoordinator,
            description: DiveraEntityDescription
    ) -> None:
        """Initialize DiveraEntity.

        Args:
            coordinator (DiveraCoordinator): The coordinator managing this entity.
            description (DiveraEntityDescription): Description of the entity.

        """
        super().__init__(coordinator)
        self.entity_description = description

        self._ucr_id = self.coordinator.data.get_active_ucr()
        self._cluster_name = self.coordinator.data.get_cluster_name_from_ucr(self._ucr_id)

        self._attr_unique_id = "_".join(
            [
                DOMAIN,
                self._ucr_id,
                description.key,
            ]
        )

        self._divera_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._divera_update()
        self.async_write_ha_state()

    def _divera_update(self) -> None:
        raise NotImplementedError

    @property
    def device_info(self) -> DeviceInfo:
        """Device information property.

        Returns:
            DeviceInfo: Device information object.

        """
        # TODO Configuration Url anpassen je nach Divera Server #108
        config_url = DIVERA_BASE_URL
        version = self.coordinator.data.get_cluster_version()
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    str(self._ucr_id),
                )
            },
            manufacturer=DIVERA_GMBH,
            name=self._cluster_name,
            model=version,
            configuration_url=config_url,
        )
