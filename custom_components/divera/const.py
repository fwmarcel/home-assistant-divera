"""Constants for the Divera integration."""
from datetime import timedelta

DOMAIN = "divera"

INTEGRATION_FULL_NAME = "Divera 24/7"
INTEGRATION_SHORT_NAME = "Divera"
DIVERA_GMBH = "Divera GmbH"

ATTR_NAME = "state"
ATTR_LATEST_UPDATE = "latest_update_utc"
DIVERA_DATA = "divera_data"
DIVERA_COORDINATOR = "divera_coordinator"
USER_NAME = "user_name"

DEFAULT_TIMEOUT = 10
DIVERA_URL = "https://www.divera247.com/api/v2/pull/all"
DIVERA_STATUS_URL = "https://www.divera247.com/api/v2/statusgeber/set-status"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

CONF_ACCESSKEY = "accesskey"
CONF_FULLNAME = "fullname"
CONF_CLUSTERS = "clusters"
CONF_UCRS = "ucrs"

CLUSTER_NAME = "cluster_name"
ACCESSKEY = "accesskey"
UCR = "ucr"

VERSION_FREE = "Free"
VERSION_ALARM = "Alarm"
VERSION_PRO = "Pro"
VERSION_UNKNOWN = "Unknown"
