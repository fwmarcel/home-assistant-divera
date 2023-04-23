"""The Divera component."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .connector import DiveraData
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DIVERA_STATE_SERVICE,
    DOMAIN,
    DIVERA_COORDINATOR,
    DIVERA_DATA,
    DIVERA_NAME,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Divera as config entry."""

    # Load values from settings
    api_key = entry.data[CONF_API_KEY]
    site_name = entry.data[CONF_NAME]

    divera_data = DiveraData(hass, api_key)

    # Update data initially
    await divera_data.async_update()
    if not divera_data.success:
        raise ConfigEntryNotReady()

    # Coordinator checks for new updates
    divera_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Divera Coordinator for {site_name}",
        update_method=divera_data.async_update,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    # Save the data
    divera_hass_data = hass.data.setdefault(DOMAIN, {})
    divera_hass_data[entry.entry_id] = {
        DIVERA_DATA: divera_data,
        DIVERA_COORDINATOR: divera_coordinator,
        DIVERA_NAME: site_name,
    }

    # Fetch initial data so we have data when entities subscribe
    await divera_coordinator.async_refresh()
    if not divera_data.success:
        raise ConfigEntryNotReady()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        # new[CONF_UPDATE_INTERVAL] = 24
        config_entry.data = {**new}
        config_entry.version = 2

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True


async def async_update(self):
    """Async wrapper for update method."""
    return await self._hass.async_add_executor_job(self._update)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, DIVERA_STATE_SERVICE)

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
