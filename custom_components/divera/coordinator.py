"""Coordinator Module for Divera Integration."""

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.divera.const import LOGGER, DEFAULT_UPDATE_INTERVAL
from custom_components.divera.divera import DiveraClient, DiveraConnectionError, DiveraAuthError


class DiveraCoordinator(DataUpdateCoordinator):
    """Coordinator for updating Divera data.

    This coordinator manages the update process for Divera data.

    Parameters:
        DataUpdateCoordinator: The base class for data update coordinators.

    """

    def __init__(self, hass, accesskey: str, ucr_id: str = None) -> None:
        """Initialize DiveraCoordinator.

        Args:
            hass: Home Assistant instance.
            accesskey (str): Access key for accessing Divera data.
            ucr_id (str, optional): Unique identifier for the organization. Defaults to None.

        """
        super().__init__(
            hass,
            LOGGER,
            name=f"Divera Coordinator {ucr_id}",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.divera_client = DiveraClient(accesskey=accesskey, ucr_id=ucr_id)

    async def _async_update_data(self):
        try:
            await self.divera_client.pull_data()
            return self.divera_client
        except DiveraAuthError as err:
            raise ConfigEntryAuthFailed from err
        except DiveraConnectionError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
