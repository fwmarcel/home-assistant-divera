"""Connector Class for Divera Data."""

import json
import logging
from datetime import datetime

import requests
from homeassistant.const import STATE_UNKNOWN

from .const import DEFAULT_TIMEOUT, DIVERA_STATUS_URL, DIVERA_URL, ACCESSKEY, UCR, VERSION_UNKNOWN, VERSION_ALARM, \
    VERSION_FREE, VERSION_PRO

_LOGGER = logging.getLogger(__name__)


class DiveraData:
    """helper class for centrally querying the data from Divera."""

    def __init__(self, hass, accesskey, ucr_id=None):
        self._hass = hass

        self.success = False
        self.latest_update = None

        self.data = None

        self.accesskey = accesskey

        self.ucr_id = ucr_id

    async def async_update(self):
        """Asynchronous update for all Divera entities."""
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Update for all Divera entities."""
        timestamp = datetime.now()

        if not self.accesskey:
            _LOGGER.exception("No update possible")
        else:
            params = {ACCESSKEY: self.accesskey}
            if self.ucr_id is not None:
                params["ucr"] = self.ucr_id
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

    def get_full_name(self):
        firstname = self.data["data"]["user"]["firstname"]
        lastname = self.data["data"]["user"]["lastname"]
        return firstname + ' ' + lastname

    def get_user(self):
        """Return information about the user."""
        data = {}
        data["firstname"] = self.data["data"]["user"]["firstname"]
        data["lastname"] = self.data["data"]["user"]["lastname"]
        data["fullname"] = self.get_full_name()
        data["email"] = self.get_email()
        return data

    def get_state_id_by_name(self, name):
        """Return the state_id of the given name."""
        for state_id in self.data["data"]["cluster"]["statussorting"]:
            state_name = self.data["data"]["cluster"]["status"][str(state_id)]["name"]
            if state_name == name:
                return state_id
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
        return self.get_state_name_by_id(status_id)

    def get_state_name_by_id(self, status_id):
        """Return the name of the state of the user by given id."""
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
                "answered": self.get_answered_state(alarm)
            }
        else:
            return {}

    def get_answered_state(self, alarm):
        """Return the state of the user answered the alarm."""
        answered = alarm["ucr_answered"]
        id = self.get_id()
        for answer_state in answered:
            try:
                state = answered[str(answer_state)]
            except TypeError:
                for state_id in answer_state:
                    state = answer_state[str(state_id)]
                    break
            if id in state:
                return self.get_state_name_by_id(answer_state)
        return "not answered"

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

    def get_default_ucr(self):
        return self.data["data"]["ucr_default"]

    def get_active_ucr(self):
        return self.data["data"]["ucr_active"]

    def get_default_ucr_name(self):
        ucr_id = self.get_default_ucr()
        return self.data["data"]["ucr"][str(ucr_id)]["name"]

    def get_ucr_count(self):
        return len(self.get_all_ucrs())

    def get_all_ucr_names(self):
        ucrs = list(self.data["data"]["ucr"])
        ucr_names = []
        for ucr_id in ucrs:
            ucr_name = self.data["data"]["ucr"][str(ucr_id)]["name"]
            ucr_names.append(ucr_name)
        return ucr_names

    def get_all_ucrs(self):
        return list(self.data["data"]["ucr"])

    def get_cluster_name_from_ucr(self, ucr_id):
        return self.data["data"]["ucr"][str(ucr_id)]["name"]

    def get_cluster_id_from_ucr(self, ucr_id):
        return self.data["data"]["ucr"][str(ucr_id)]["cluster_id"]

    def get_ucr_ids(self, ucr_names):
        ucrs = list(self.data["data"]["ucr"])
        ucr_ids = []
        for ucr_id in ucrs:
            ucr_name = self.data["data"]["ucr"][str(ucr_id)]["name"]
            if ucr_name in ucr_names:
                ucr_ids.append(ucr_id)
        return ucr_ids

    def get_id(self):
        """Return id of user."""
        return list(self.data["data"]["ucr"])[0]

    def get_accesskey(self):
        return self.data["data"]["user"]["accesskey"]

    def get_email(self):
        return self.data["data"]["user"]["email"]

    def set_state(self, state_id):
        """Set the state of the user to the given id."""
        payload = json.dumps({"Status": {"id": state_id}})
        headers = {"Content-Type": "application/json"}

        if not self.accesskey:
            _LOGGER.exception("state can not be set. accesskey is missing or wrong.")
        else:
            params = {
                ACCESSKEY: self.accesskey,
                UCR: self.ucr_id
            }
            try:
                response = requests.post(
                    DIVERA_STATUS_URL,
                    params=params,
                    headers=headers,
                    timeout=DEFAULT_TIMEOUT,
                    data=payload,
                )
                if response.status_code != 200:
                    _LOGGER.error("error while setting the state %s", response.status_code)
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)

    def get_cluster_version(self):
        version = self.data["data"]["cluster"]["version_id"]
        match version:
            case 1:
                return VERSION_FREE
            case 2:
                return VERSION_ALARM
            case 2:
                return VERSION_PRO
            case _:
                return VERSION_UNKNOWN
