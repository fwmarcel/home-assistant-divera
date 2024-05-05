"""Config flow for Divera 24/7 integration."""

from typing import Any

from voluptuous import Optional, Required, Schema

from homeassistant.config_entries import HANDLERS, ConfigEntry, ConfigFlow
from homeassistant.data_entry_flow import FlowHandler
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_ACCESSKEY,
    CONF_BASE_URL,
    CONF_CLUSTERS,
    CONF_FLOW_MINOR_VERSION,
    CONF_FLOW_NAME_API,
    CONF_FLOW_NAME_UCR,
    CONF_FLOW_VERSION,
    DATA_ACCESSKEY,
    DATA_BASE_URL,
    DATA_UCRS,
    DIVERA_BASE_URL,
    DOMAIN,
    ERROR_AUTH,
    ERROR_CONNECTION,
)
from .divera import DiveraAuthError, DiveraClient, DiveraConnectionError


class DiveraFlow(FlowHandler):
    """Flow handler for Divera integration."""

    def __init__(self, config_entry: ConfigEntry = None):
        """Initialize DiveraFlow.

        Args:
            config_entry (ConfigEntry, optional): Configuration entry for Divera integration. Defaults to None.

        """
        self._config_entry: ConfigEntry | None = config_entry
        self._divera_client: DiveraClient | None = None
        self._data: dict[str, Any] = {}

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

    async def _show_api_form(self, errors):
        api_schema = Schema(
            {
                Required(CONF_ACCESSKEY, default=""): str,
                Optional(
                    CONF_BASE_URL, description={"suggested_value": DIVERA_BASE_URL}
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
            },
        )
        return self.async_show_form(
            step_id=CONF_FLOW_NAME_API, data_schema=api_schema, errors=errors
        )

    def create_entry(self, ucr_ids: list[int]):
        """Create a config entry.

        Returns:
            ConfigEntry: The created config entry.

        """
        self._data[DATA_UCRS] = ucr_ids
        self._data[DATA_BASE_URL] = self._divera_client.get_base_url()
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
        """Initialize DiveraConfigFlow."""
        super().__init__()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step.

        Args:
            user_input (dict): User input.

        Returns:
            dict: The next step or form to present to the user.

        """
        return await self.async_step_api(user_input)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Add reconfigure step to allow to reconfigure a config entry."""
        return await self.async_step_user_cluster_relation(user_input)

    async def async_step_api(self, user_input: dict[str, Any] | None = None):
        """Handle the API step of the config flow.

        Args:
            user_input (dict[str, Any], optional): User input. Defaults to None.

        Returns:
            Dict[str, Any]: Dictionary of step results.

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            accesskey = user_input.get(CONF_ACCESSKEY)
            base_url = user_input.get(CONF_BASE_URL)
            # await self.set_divera_client(accesskey, base_url, errors)

            websession = async_get_clientsession(self.hass)
            self._divera_client = DiveraClient(websession, accesskey, base_url)
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
                ucr_id: int = self._divera_client.get_default_ucr()
                return self.create_entry([ucr_id])

        return await self._show_api_form(errors)

    async def async_step_user_cluster_relation(
        self, user_input: dict[str, Any] | None = None
    ):
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

        return await self._show_clusters_form(
            active_cluster_names, cluster_names, errors
        )

    async def check_unique_id(self):
        """Check the uniqueness of the unique ID.

        This method retrieves the unique ID based on the user's email,
        sets it as the unique ID for the config entry, and aborts the
        configuration if the unique ID is already configured.

        """
        uid = self._divera_client.get_email()
        await self.async_set_unique_id(uid)
        self._abort_if_unique_id_configured()
