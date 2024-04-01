"""Config flow for Divera 24/7 integration."""

from typing import Any

from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from voluptuous import Required, Schema

from .const import (
    DOMAIN, DATA_UCRS, CONF_FLOW_VERSION, CONF_FLOW_MINOR_VERSION, ERROR_AUTH, ERROR_CONNECTION,
    DATA_ACCESSKEY, CONF_CLUSTERS, CONF_ACCESSKEY
)
from .divera import DiveraClient, DiveraAuthError, DiveraConnectionError

ACCESSKEY_SCHEMA = Schema(
    {
        Required(CONF_ACCESSKEY, default=""): str,
    },
)


class DiveraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Divera integration.

    This class manages the configuration flow for setting up the Divera integration.

    """

    VERSION = CONF_FLOW_VERSION
    MINOR_VERSION = CONF_FLOW_MINOR_VERSION

    data: dict[str, Any] | None

    divera_client: DiveraClient

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        errors: dict[str, str] = {}

        if user_input is not None:

            self.divera_client = DiveraClient(accesskey=user_input.get(CONF_ACCESSKEY))

            try:
                await self.divera_client.pull_data()
            except DiveraAuthError:
                errors["base"] = ERROR_AUTH
            except DiveraConnectionError:
                errors["base"] = ERROR_CONNECTION

            if not errors:
                await self.check_unique_id()
                self.data = user_input
                self.data[DATA_ACCESSKEY] = self.divera_client.get_accesskey()
                if self.divera_client.get_ucr_count() > 1:
                    return await self.async_step_user_cluster_relation()
                else:
                    ucr_id: int = self.divera_client.get_default_ucr()
                    self.set_cluster_data([ucr_id])
                    return self.create_entry()

        return self.async_show_form(step_id="user", data_schema=ACCESSKEY_SCHEMA, errors=errors)

    async def async_step_user_cluster_relation(self, user_input: dict[str, Any] | None = None):
        """Second step in config flow to select the cluster of the user.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        errors: dict[str, str] = {}

        clusters = self.divera_client.get_all_cluster_names()

        if user_input is not None:
            if not errors:
                cluster_names = user_input[CONF_CLUSTERS]
                ucr_ids = self.divera_client.get_ucr_ids(cluster_names)
                self.set_cluster_data(ucr_ids)
                return self.create_entry()

        cluster_schema = {
            Required(CONF_CLUSTERS): selector(
                {
                    "select": {
                        "options": clusters,
                        "multiple": True
                    }
                }
            )
        }

        return self.async_show_form(
            step_id="user_cluster_relation", data_schema=Schema(cluster_schema), errors=errors
        )

    async def check_unique_id(self):
        """Check the uniqueness of the unique ID.

        This method retrieves the unique ID based on the user's email,
        sets it as the unique ID for the config entry, and aborts the
        configuration if the unique ID is already configured.

        """
        uid = self.divera_client.get_email()
        await self.async_set_unique_id(uid)
        self._abort_if_unique_id_configured()

    def set_cluster_data(self, ucr_ids: list):
        """Set cluster data for the Divera instance.

        Args:
            ucr_ids (list): List of unique cluster IDs.

        """
        self.data[DATA_UCRS] = ucr_ids

    def create_entry(self):
        """Create a config entry.

        Returns:
            ConfigEntry: The created config entry.

        """
        return self.async_create_entry(title=self.divera_client.get_full_name(), data=self.data)
