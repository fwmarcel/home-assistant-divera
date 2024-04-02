"""constants for divera integration."""
import logging
from datetime import timedelta

LOGGER = logging.getLogger(__package__)

DOMAIN: str = "divera"

INTEGRATION_FULL_NAME: str = "Divera 24/7"
INTEGRATION_SHORT_NAME: str = "Divera"
DIVERA_GMBH: str = "Divera GmbH"

ATTR_NAME: str = "state"
ATTR_LATEST_UPDATE: str = "latest_update_utc"
DIVERA_DATA: str = "divera_data"
DATA_DIVERA_COORDINATOR: str = "divera_coordinator"
USER_NAME: str = "user_name"

DIVERA_BASE_URL: str = "https://www.divera247.com"
DIVERA_API_PULL_PATH: str = "/api/v2/pull/all"
DIVERA_API_STATUS_PATH: str = "/api/v2/statusgeber/set-status"

DEFAULT_UPDATE_INTERVAL: timedelta = timedelta(minutes=1)

DATA_ACCESSKEY: str = "accesskey"
DATA_UCRS: str = "ucrs"

CONF_CLUSTERS: str = "clusters"
CONF_ACCESSKEY: str = "accesskey"

PARAM_ACCESSKEY: str = "accesskey"
PARAM_UCR: str = "ucr"

VERSION_FREE: str = "Free"
VERSION_ALARM: str = "Alarm"
VERSION_PRO: str = "Pro"
VERSION_UNKNOWN: str = "Unknown"

CONF_FLOW_VERSION: int = 3
CONF_FLOW_MINOR_VERSION: int = 1
CONF_FLOW_NAME_UCR: str = "user_cluster_relation"
CONF_FLOW_NAME_ACCESSKEY: str = "accesskey"

ERROR_AUTH = "authentication"
ERROR_CONNECTION = "cannot_connect"
