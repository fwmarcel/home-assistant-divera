"""Config flow for Divera 24/7 integration."""

from typing import Any, Dict

from homeassistant.config_entries import OptionsFlow, ConfigFlow, ConfigEntry, HANDLERS
from homeassistant.data_entry_flow import FlowHandler
from homeassistant.helpers.selector import SelectSelectorConfig, SelectSelector
from voluptuous import Required, Schema

from .const import (
    DOMAIN, DATA_UCRS, CONF_FLOW_VERSION, CONF_FLOW_MINOR_VERSION, ERROR_AUTH, ERROR_CONNECTION,
    DATA_ACCESSKEY, CONF_CLUSTERS, CONF_ACCESSKEY, CONF_FLOW_NAME_UCR, CONF_FLOW_NAME_ACCESSKEY
)
from .divera import DiveraClient, DiveraAuthError, DiveraConnectionError, DiveraError


class DiveraFlow(FlowHandler):

    def __init__(self):
        self._divera_client: DiveraClient | None = None
        self._data: Dict[str, Any] = {}

    async def _show_clusters_form(self, active_cluster_names, cluster_names, errors):
        cluster_schema = Schema(
            {
                Required(CONF_CLUSTERS, default=active_cluster_names): SelectSelector(
                    SelectSelectorConfig(options=cluster_names, multiple=True)
                ),
            }
        )
        return self.async_show_form(
            step_id=CONF_FLOW_NAME_UCR, data_schema=cluster_schema, errors=errors
        )

    def create_entry(self, ucr_ids: list[int]):
        """Create a config entry.

        Returns:
            ConfigEntry: The created config entry.

        """
        self._data[DATA_UCRS] = ucr_ids
        self._data[DATA_ACCESSKEY] = self._divera_client.get_accesskey()

        title = self._divera_client.get_full_name()
        return self.async_create_entry(title=title, data=self._data)


@HANDLERS.register(DOMAIN)
class DiveraConfigFlow(DiveraFlow, ConfigFlow):
    """Handle a config flow for Divera integration.

    This class manages the configuration flow for setting up the Divera integration.

    """

    VERSION = CONF_FLOW_VERSION
    MINOR_VERSION = CONF_FLOW_MINOR_VERSION

    def __init__(self):
        super().__init__()

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
    #     return DiveraOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        return await self.async_step_accesskey(user_input)

    async def async_step_accesskey(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            accesskey = user_input.get(CONF_ACCESSKEY)
            self._divera_client = DiveraClient(accesskey)
            try:
                await self._divera_client.pull_data()
            except DiveraAuthError:
                errors["base"] = ERROR_AUTH
            except DiveraConnectionError:
                errors["base"] = ERROR_CONNECTION

            if not errors:
                await self.check_unique_id()
                if self._divera_client.get_ucr_count() > 1:
                    return await self.async_step_user_cluster_relation()
                else:
                    ucr_id: int = self._divera_client.get_default_ucr()
                    return self.create_entry([ucr_id])

        return await self._show_accesskey_form(errors)

    async def _show_accesskey_form(self, errors):
        accesskey_schema = Schema(
            {
                Required(CONF_ACCESSKEY, default=""): str,
            },
        )
        return self.async_show_form(
            step_id=CONF_FLOW_NAME_ACCESSKEY, data_schema=accesskey_schema, errors=errors
        )

    async def async_step_user_cluster_relation(self, user_input: dict[str, Any] | None = None):
        """Second step in config flow to select the cluster of the user.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            if not errors:
                selected_cluster_names = user_input[CONF_CLUSTERS]
                ucr_ids = self._divera_client.get_ucr_ids(selected_cluster_names)
                return self.create_entry(ucr_ids)

        cluster_names = self._divera_client.get_all_cluster_names()
        active_cluster_names = [cluster_names[0]]

        return await self._show_clusters_form(active_cluster_names, cluster_names, errors)

    async def check_unique_id(self):
        """Check the uniqueness of the unique ID.

        This method retrieves the unique ID based on the user's email,
        sets it as the unique ID for the config entry, and aborts the
        configuration if the unique ID is already configured.

        """
        uid = self._divera_client.get_email()
        await self.async_set_unique_id(uid)
        self._abort_if_unique_id_configured()


class DiveraOptionsFlowHandler(OptionsFlow, DiveraFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_user_cluster_relation(user_input)

    async def async_step_user_cluster_relation(self, user_input: dict[str, Any] | None = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                selected_cluster_names = user_input[CONF_CLUSTERS]
                ucr_ids = self._divera_client.get_ucr_ids(selected_cluster_names)
                return self.create_entry(ucr_ids)

        accesskey = self._config_entry.data[DATA_ACCESSKEY]
        self._divera_client = DiveraClient(accesskey=accesskey)

        try:
            await self._divera_client.pull_data()
        except DiveraError:
            pass

        cluster_names = self._divera_client.get_all_cluster_names()

        active_ucr_ids = self._config_entry.data[DATA_UCRS]
        active_cluster_names = self._divera_client.get_cluster_names_from_ucrs(active_ucr_ids)

        return await self._show_clusters_form(active_cluster_names, cluster_names, errors)
