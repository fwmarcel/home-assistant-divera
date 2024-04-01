"""divera component."""

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant

from .const import (
    DATA_UCRS,
    DOMAIN,
    DATA_DIVERA_COORDINATOR,
    CONF_FLOW_VERSION,
    CONF_FLOW_MINOR_VERSION, LOGGER, DATA_ACCESSKEY
)
from .coordinator import DiveraCoordinator
from .divera import DiveraClient, DiveraError

PLATFORMS = [
    Platform.SELECT,
    Platform.SENSOR
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Divera as config entry.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The config entry for Divera.

    """
    accesskey: str = entry.data[DATA_ACCESSKEY]
    ucr_ids = entry.data[DATA_UCRS]

    divera_hass_data = hass.data.setdefault(DOMAIN, {})
    divera_hass_data[entry.entry_id] = {}

    for ucr_id in ucr_ids:
        divera_coordinator = DiveraCoordinator(hass, accesskey, ucr_id)
        divera_hass_data[entry.entry_id][ucr_id] = {
            DATA_DIVERA_COORDINATOR: divera_coordinator
        }

        await divera_coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


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

    LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version > CONF_FLOW_VERSION or config_entry.minor_version > CONF_FLOW_MINOR_VERSION:
        # This means the user has downgraded from a future version
        LOGGER.debug("Migration to version %s.%s failed. Downgraded ", config_entry.version,
                     config_entry.minor_version)
        return False

    new = {**config_entry.data}
    if config_entry.version < 3:
        accesskey: str = new.get(CONF_API_KEY)
        new.pop(CONF_API_KEY)
        new[DATA_ACCESSKEY] = accesskey
        new.pop(CONF_NAME)

        divera_client: DiveraClient = DiveraClient(accesskey=accesskey)
        try:
            await divera_client.pull_data()
        except DiveraError:
            LOGGER.debug("Migration to version %s.%s failed.", config_entry.version, config_entry.minor_version)
            return False
        ucr_id = divera_client.get_active_ucr()
        new[DATA_UCRS] = [ucr_id]

    hass.config_entries.async_update_entry(config_entry, data=new, minor_version=CONF_FLOW_MINOR_VERSION,
                                           version=CONF_FLOW_VERSION)
    LOGGER.debug("Migration to version %s.%s successful", config_entry.version, config_entry.minor_version)
    return True
