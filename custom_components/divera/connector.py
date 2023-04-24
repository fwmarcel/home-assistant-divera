"""Connector Class for Divera Data."""

from datetime import datetime
import logging
import json
import requests

from homeassistant.const import STATE_UNKNOWN
from .const import DEFAULT_TIMEOUT, DIVERA_STATUS_URL, DIVERA_URL

_LOGGER = logging.getLogger(__name__)


class DiveraData:
    """helper class for centrally querying the data from Divera."""

    def __init__(self, hass, api_key):
        """Initiate necessary data for the helper class."""
        self._hass = hass

        self.success = False
        self.latest_update = None

        self.data = None

        if api_key != "":
            self.api_key = api_key

    async def async_update(self):
        """Asynchronous update for all Divera entities."""
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Update for all Divera entities."""
        timestamp = datetime.now()

        if not self.api_key:
            _LOGGER.exception("No update possible")
        else:
            params = {"accesskey": self.api_key}
            try:
                response = requests.get(
                    DIVERA_URL, params=params, timeout=DEFAULT_TIMEOUT
                )
                self.data = response.json()
                self.success = response.status_code == 200
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)
                self.success = False
            else:
                self.latest_update = timestamp
            _LOGGER.debug("Values updated at %s", self.latest_update)

    def get_user(self):
        """Return information about the user."""
        data = {}
        data["firstname"] = self.data["data"]["user"]["firstname"]
        data["lastname"] = self.data["data"]["user"]["lastname"]
        data["fullname"] = data["firstname"] + " " + data["lastname"]
        data["email"] = self.data["data"]["user"]["email"]
        return data

    def get_state_id_by_name(self, name):
        """Return the state_id of the given name."""
        for state_id in self.data["data"]["cluster"]["statussorting"]:
            state_name = self.data["data"]["cluster"]["status"][str(state_id)]["name"]
            if state_name == name:
                return id
        return None

    def get_all_state_name(self):
        """Return the list of all available names of the states."""
        states = []
        for state_id in self.data["data"]["cluster"]["statussorting"]:
            state_name = self.data["data"]["cluster"]["status"][str(state_id)]["name"]
            states.append(state_name)
        return states

    def get_user_state(self):
        """Give the name of the current status of the user."""
        status_id = self.data["data"]["status"]["status_id"]
        state_name = self.data["data"]["cluster"]["status"][str(status_id)]["name"]
        return state_name

    def get_user_state_attributes(self):
        """Return aditional information of state."""
        data = {}
        timestamp = self.data["data"]["status"]["status_set_date"]
        data["timestamp"] = datetime.fromtimestamp(timestamp)
        data["id"] = self.data["data"]["status"]["status_id"]
        return data

    def get_last_alarm_attributes(self):
        """Return aditional information of last alarm."""
        sorting_list = self.data["data"]["alarm"]["sorting"]
        if len(sorting_list) > 0:
            last_alarm_id = sorting_list[0]
            alarm = self.data["data"]["alarm"]["items"][str(last_alarm_id)]
            groups = map(self.get_group_name_by_id, alarm["group"])
            return {
                "id": alarm["id"],
                "text": alarm["text"],
                "date": datetime.fromtimestamp(alarm["date"]),
                "address": alarm["address"],
                "latitude": str(alarm["lat"]),
                "longitude": str(alarm["lng"]),
                "groups": list(groups),
                "priority": alarm["priority"],
                "closed": alarm["closed"],
                "new": alarm["new"],
                "self_addressed": alarm["ucr_self_addressed"],
            }
        else:
            return {}

    def get_last_alarm(self):
        """Return informations of last alarm."""
        sorting_list = self.data["data"]["alarm"]["sorting"]
        if len(sorting_list) > 0:
            last_alarm_id = sorting_list[0]
            alarm = self.data["data"]["alarm"]["items"][str(last_alarm_id)]
            return alarm["title"]
        else:
            return STATE_UNKNOWN

    def get_group_name_by_id(self, group_id):
        """Return the name from the given group id."""
        try:
            group = self.data["data"]["cluster"]["group"][str(group_id)]
            return group["name"]
        except KeyError:
            return None

    def get_id(self):
        """Return id of user."""
        return list(self.data["data"]["ucr"])[0]

    def set_state(self, state_id):
        """Set the state of the user to the given id."""
        payload = json.dumps({"Status": {"id": state_id}})
        headers = {"Content-Type": "application/json"}

        if not self.api_key:
            _LOGGER.exception("state can not be set. api-key is missing")
        else:
            params = {"accesskey": self.api_key}
            try:
                response = requests.post(
                    DIVERA_STATUS_URL,
                    params=params,
                    headers=headers,
                    timeout=DEFAULT_TIMEOUT,
                    data=payload,
                )
                if response.status_code != 200:
                    _LOGGER.error("Error while setting the state")
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)
