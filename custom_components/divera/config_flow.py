"""Config flow for Divera 24/7 integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers.selector import selector

from .connector import DiveraData
from .const import (
    DOMAIN,
    CONF_UCRS,
    CONF_ACCESSKEY,
    CONF_CLUSTERS,
    CONF_FULLNAME, CONF_FLOW_VERSION, CONF_FLOW_MINOR_VERSION,
)

_LOGGER = logging.getLogger(__name__)


class DiveraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Divera integration.

    This class manages the configuration flow for setting up the Divera integration.

    """

    VERSION = CONF_FLOW_VERSION
    MINOR_VERSION = CONF_FLOW_MINOR_VERSION
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    data: dict[str, Any] | None

    divera_data: DiveraData

    async def check_unique_id(self):
        """Check the uniqueness of the unique ID.

        This method retrieves the unique ID based on the user's email,
        sets it as the unique ID for the config entry, and aborts the
        configuration if the unique ID is already configured.

        """
        uid = self.divera_data.get_email()
        await self.async_set_unique_id(uid)
        self._abort_if_unique_id_configured()

    def create_entry(self):
        """Create a config entry.

        Returns:
            ConfigEntry: The created config entry.

        """
        return self.async_create_entry(title=self.divera_data.get_full_name(), data=self.data)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self.validate_accesskey(user_input[CONF_ACCESSKEY], self.hass)
            except ValueError:
                errors["base"] = "auth"

            await self.check_unique_id()

            if not errors:
                self.data = user_input
                self.data[CONF_ACCESSKEY] = self.divera_data.get_accesskey()
                self.data[CONF_FULLNAME] = self.divera_data.get_full_name()
                if self.divera_data.get_ucr_count() > 1:
                    return await self.async_step_user_cluster_relation()
                else:
                    ucr_id: int = self.divera_data.get_default_ucr()
                    self.setClusterData([ucr_id])
                    return self.create_entry()

        accesskey_schema = vol.Schema(
            {
                vol.Required(CONF_ACCESSKEY, default=""): str,
            },
        )
        return self.async_show_form(step_id="user", data_schema=accesskey_schema, errors=errors)

    async def async_step_user_cluster_relation(self, user_input: dict[str, Any] | None = None):
        """Second step in config flow to select the cluster of the user.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        errors: dict[str, str] = {}

        clusters = self.divera_data.get_all_cluster_names()

        if user_input is not None:
            if not errors:
                ucr_ids = self.divera_data.get_ucr_ids(user_input[CONF_CLUSTERS])
                self.setClusterData(ucr_ids)
                return self.create_entry()

        cluster_schema = {vol.Required(CONF_CLUSTERS): selector({"select": {"options": clusters, "multiple": True}})}

        return self.async_show_form(
            step_id="user_cluster_relation", data_schema=vol.Schema(cluster_schema), errors=errors
        )

    async def validate_accesskey(self, access_token: str, hass: core.HomeAssistant) -> None:
        """Validate a Divera access key.

        Args:
            access_token (str): The access token to validate.
            hass (core.HomeAssistant): The Home Assistant instance.

        Raises:
            ValueError: If the access key is invalid.

        """
        self.divera_data = DiveraData(hass, access_token)
        await self.divera_data.async_update()
        if not self.divera_data.success:
            raise ValueError()
            # TODO raise alternative Error, which is a HomeAssistantError
        return

    def setClusterData(self, ucr_ids: list):
        """
        Set cluster data for the Divera instance.

        Parameters:
            ucr_ids (list): List of unique cluster IDs.

        """
        self.data[CONF_UCRS] = ucr_ids
        self.data[CONF_CLUSTERS] = {}
        for ucr_id in ucr_ids:
            self.data[CONF_CLUSTERS][ucr_id] = self.divera_data.get_cluster_name_from_ucr(ucr_id)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
