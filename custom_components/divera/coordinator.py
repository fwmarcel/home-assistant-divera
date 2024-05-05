"""Coordinator Module for Divera Integration."""

from datetime import timedelta

from aiohttp import ClientSession

from custom_components.divera.const import DEFAULT_SCAN_INTERVAL, LOGGER
from custom_components.divera.divera import (
    DiveraAuthError,
    DiveraClient,
    DiveraConnectionError,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


class DiveraCoordinator(DataUpdateCoordinator):
    """Coordinator for updating Divera data.

    This coordinator manages the update process for Divera data.

    Parameters:
        DataUpdateCoordinator: The base class for data update coordinators.

    """

    def __init__(
        self,
        hass,
        session: ClientSession,
        accesskey: str,
        base_url: str,
        ucr_id: str,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize DiveraCoordinator.

        Args:
            hass: Home Assistant instance.
            session (ClientSession): Client session for making HTTP requests.
            accesskey (str): Access key for accessing Divera data.
            base_url (str): Base URL for Divera API.
            ucr_id (str): Unique identifier for the organization.
            update_interval (int | None, optional): Interval in seconds for updating data. Defaults to DEFAULT_SCAN_INTERVAL.

        """
        super().__init__(
            hass,
            LOGGER,
            name=f"Divera Coordinator {ucr_id}",
            update_interval=timedelta(seconds=update_interval),
        )
        self.divera_client = DiveraClient(
            session, accesskey=accesskey, base_url=base_url, ucr_id=ucr_id
        )

    async def _async_update_data(self):
        try:
            await self.divera_client.pull_data()
        except DiveraAuthError as err:
            raise ConfigEntryAuthFailed from err
        except DiveraConnectionError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from None
        else:
            return self.divera_client
