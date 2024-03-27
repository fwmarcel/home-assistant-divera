"""constants for divera integration."""

from datetime import timedelta

DOMAIN: str = "divera"

INTEGRATION_FULL_NAME: str = "Divera 24/7"
INTEGRATION_SHORT_NAME: str = "Divera"
DIVERA_GMBH: str = "Divera GmbH"

ATTR_NAME: str = "state"
ATTR_LATEST_UPDATE: str = "latest_update_utc"
DIVERA_DATA: str = "divera_data"
DIVERA_COORDINATOR: str = "divera_coordinator"
USER_NAME: str = "user_name"

DEFAULT_TIMEOUT = 10
DIVERA_URL: str = "https://www.divera247.com/api/v2/pull/all"
DIVERA_STATUS_URL: str = "https://www.divera247.com/api/v2/statusgeber/set-status"

DEFAULT_SCAN_INTERVAL: timedelta = timedelta(minutes=1)

CONF_ACCESSKEY: str = "accesskey"
CONF_FULLNAME: str = "fullname"
CONF_CLUSTERS: str = "clusters"
CONF_UCRS: str = "ucrs"

CLUSTER_NAME: str = "cluster_name"
ACCESSKEY: str = "accesskey"
UCR: str = "ucr"

VERSION_FREE: str = "Free"
VERSION_ALARM: str = "Alarm"
VERSION_PRO: str = "Pro"
VERSION_UNKNOWN: str = "Unknown"

CONF_FLOW_VERSION: int = 3
CONF_FLOW_MINOR_VERSION: int = 1
