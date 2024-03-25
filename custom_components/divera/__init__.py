"""The Divera component."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .connector import DiveraData
from .const import (
    CONF_UCRS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    DIVERA_COORDINATOR,
    DIVERA_DATA,
    USER_NAME,
    CLUSTER_NAME, CONF_ACCESSKEY, CONF_FULLNAME, CONF_CLUSTERS
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Divera as config entry."""

    accesskey: str = entry.data[CONF_ACCESSKEY]
    fullname: str = entry.data[CONF_FULLNAME]
    clusters = entry.data[CONF_CLUSTERS]
    ucr_ids = entry.data[CONF_UCRS]

    divera_hass_data = hass.data.setdefault(DOMAIN, {})
    divera_hass_data[entry.entry_id] = {}

    for ucr_id in ucr_ids:
        cluster_name: str = clusters[str(ucr_id)]

        divera_data = DiveraData(hass, accesskey, ucr_id)
        divera_coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"Divera Coordinator for {fullname} - {cluster_name}",
            update_method=divera_data.async_update,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        divera_hass_data[entry.entry_id][ucr_id] = {
            DIVERA_DATA: divera_data,
            DIVERA_COORDINATOR: divera_coordinator,
            USER_NAME: fullname,
            CLUSTER_NAME: cluster_name
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
