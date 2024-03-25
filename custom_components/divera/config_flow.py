"""Config flow for Divera 24/7 integration."""

import logging
from typing import Any, Optional, Dict

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers.selector import selector

from .connector import DiveraData
from .const import (
    DOMAIN,
    CONF_UCRS, CONF_ACCESSKEY, CONF_CLUSTERS, CONF_FULLNAME,
)

_LOGGER = logging.getLogger(__name__)


class DiveraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Divera integration."""

    VERSION = 3
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    data: Optional[Dict[str, Any]]

    divera_data: DiveraData

    async def check_uniquie_id(self):
        uid = self.divera_data.get_email()
        await self.async_set_unique_id(uid)
        self._abort_if_unique_id_configured()

    def create_entry(self):
        return self.async_create_entry(
            title=self.divera_data.get_full_name(), data=self.data
        )

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await self.validate_accesskey(user_input[CONF_ACCESSKEY], self.hass)
            except ValueError:
                errors["base"] = "auth"

            await self.check_uniquie_id()

            if not errors:
                self.data = user_input
                self.data[CONF_ACCESSKEY] = self.divera_data.get_accesskey()
                self.data[CONF_FULLNAME] = self.divera_data.get_full_name()
                self.data[CONF_CLUSTERS] = {}
                ucr_ids = self.divera_data.get_all_ucrs()
                for ucr_id in ucr_ids:
                    self.data[CONF_CLUSTERS][ucr_id] = self.divera_data.get_cluster_name_from_ucr(ucr_id)

                if self.divera_data.get_ucr_count() > 1:
                    return await self.async_step_user_cluster_relation()
                else:
                    self.data[CONF_UCRS] = [self.divera_data.get_default_ucr()]
                    return self.create_entry()

        accesskey_schema = vol.Schema(
            {
                vol.Required(CONF_ACCESSKEY, default=""): str,
            },
        )
        return self.async_show_form(step_id="user", data_schema=accesskey_schema, errors=errors)

    async def async_step_user_cluster_relation(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}

        clusters = self.divera_data.get_all_ucr_names()

        if user_input is not None:
            if not errors:
                self.data[CONF_UCRS] = self.divera_data.get_ucr_ids(user_input[CONF_CLUSTERS])
                return self.create_entry()

        cluster_schema = {
            vol.Required(CONF_CLUSTERS): selector({
                "select": {
                    "options": clusters,
                    "multiple": True
                }
            })
        }

        return self.async_show_form(
            step_id="user_cluster_relation", data_schema=vol.Schema(cluster_schema), errors=errors
        )

    async def validate_accesskey(self, access_token: str, hass: core.HomeAssistant) -> None:
        """Validates a Divera access key.
        Raises a ValueError if the access key is invalid.
        """
        self.divera_data = DiveraData(hass, access_token)
        await self.divera_data.async_update()
        if not self.divera_data.success:
            raise ValueError()
        return


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
