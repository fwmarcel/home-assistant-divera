"""divera component."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_API_KEY, CONF_NAME
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
    CLUSTER_NAME,
    CONF_ACCESSKEY,
    CONF_FULLNAME,
    CONF_CLUSTERS,
    CONF_FLOW_VERSION,
    CONF_FLOW_MINOR_VERSION
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Divera as config entry.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The config entry for Divera.

    """
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
            CLUSTER_NAME: cluster_name,
        }

        # Fetch initial data so we have data when entities subscribe
        await divera_coordinator.async_refresh()
        if not divera_data.success:
            raise ConfigEntryNotReady()

    for component in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, component))

    return True

async def async_update(self):
    """Asynchronously updates the state of the object.

    This method uses Home Assistant's event loop to asynchronously execute the
    `_update` method within a separate thread.

    Returns:
        Awaitable: A future representing the result of the update operation.

    Notes:
        This method is intended to be used in asynchronous contexts.

    """
    return await self._hass.async_add_executor_job(self._update)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Divera config entry.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The config entry to unload.

    Returns:
        bool: True if unloading was successful, False otherwise.

    """
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, component) for component in PLATFORMS]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        config_entry (ConfigEntry): The config entry to migrate.

    Returns:
        bool: True if migration was successful, False otherwise.

    """

    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version > CONF_FLOW_VERSION or config_entry.minor_version > CONF_FLOW_MINOR_VERSION:
        # This means the user has downgraded from a future version
        _LOGGER.debug("Migration to version %s.%s failed. Downgraded ", config_entry.version,
                      config_entry.minor_version)
        return False

    new = {**config_entry.data}
    if config_entry.version < 3:
        accesskey: str = new.get(CONF_API_KEY)
        new.pop(CONF_API_KEY)
        new[CONF_ACCESSKEY] = accesskey

        fullname: str = new[CONF_NAME]
        new.pop(CONF_NAME)
        new[CONF_FULLNAME] = fullname

        divera_data: DiveraData = DiveraData(hass, accesskey)
        await divera_data.async_update()
        if not divera_data.success:
            _LOGGER.debug("Migration to version %s.%s failed.", config_entry.version, config_entry.minor_version)
            return False
        ucr_id = divera_data.get_active_ucr()
        new[CONF_UCRS] = [ucr_id]
        new[CONF_CLUSTERS] = {}
        new[CONF_CLUSTERS][ucr_id] = divera_data.get_cluster_name_from_ucr(ucr_id)

    hass.config_entries.async_update_entry(config_entry, data=new, minor_version=CONF_FLOW_MINOR_VERSION,
                                           version=CONF_FLOW_VERSION)
    _LOGGER.debug("Migration to version %s.%s successful", config_entry.version, config_entry.minor_version)
    return True
