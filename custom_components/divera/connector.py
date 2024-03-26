"""Connector Class for Divera Data."""

import json
import logging
from datetime import datetime

import requests
from homeassistant.const import STATE_UNKNOWN

from .const import (
    DEFAULT_TIMEOUT,
    DIVERA_STATUS_URL,
    DIVERA_URL,
    ACCESSKEY,
    UCR,
    VERSION_UNKNOWN,
    VERSION_ALARM,
    VERSION_FREE,
    VERSION_PRO,
)

_LOGGER = logging.getLogger(__name__)


class DiveraData:
    """Class for managing Divera data.

    Attributes:
        _hass: Home Assistant instance.
        success (bool): Indicates if data retrieval was successful.
        latest_update: Timestamp of the latest update.
        data: Data retrieved from Divera.
        accesskey (str): Access key for authentication.
        ucr_id (Optional[int]): ID of the User Cluster Relation (UCR).

    """

    def __init__(self, hass, accesskey, ucr_id=None) -> None:
        """Initialize DiveraData with Home Assistant instance and access key.

        Args:
            hass: Home Assistant instance.
            accesskey (str): Access key for authentication.
            ucr_id (Optional[int]): ID of the User Cluster Relation (UCR).

        """
        self._hass = hass
        self.success = False
        self.latest_update = None
        self.data = None
        self.accesskey = accesskey
        self.ucr_id = ucr_id

    async def async_update(self):
        """Asynchronously update all Divera entities.

        Returns:
            Any: The result of the asynchronous update operation.

        Note:
            This method uses asynchronous execution for the update operation.

        """
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Update for all Divera entities.

        Updates the data by making a request to the Divera API.

        """
        timestamp = datetime.now()

        if not self.accesskey:
            _LOGGER.exception("No update possible")
        else:
            params = {ACCESSKEY: self.accesskey}
            if self.ucr_id is not None:
                params["ucr"] = self.ucr_id
            try:
                response = requests.get(DIVERA_URL, params=params, timeout=DEFAULT_TIMEOUT)
                self.data = response.json()
                self.success = response.status_code == 200
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)
                self.success = False
            else:
                self.latest_update = timestamp
            _LOGGER.debug("Values updated at %s", self.latest_update)

    def get_full_name(self) -> str:
        """Retrieve the full name of the user associated with the data.

        Returns:
            str: The full name of the user, combining the first name and last name.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        firstname = self.data["data"]["user"]["firstname"]
        lastname = self.data["data"]["user"]["lastname"]
        return firstname + " " + lastname

    def get_user(self) -> dict:
        """Return information about the user.

        Returns:
            dict: A dictionary containing information about the user including first name, last name,
                  full name, and email.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        data = {}
        data["firstname"] = self.data["data"]["user"]["firstname"]
        data["lastname"] = self.data["data"]["user"]["lastname"]
        data["fullname"] = self.get_full_name()
        data["email"] = self.get_email()
        return data

    def get_state_id_by_name(self, name):
        """Return the state_id of the given state name.

        Args:
            name (str): The name of the state.

        Returns:
            int or None: The state_id corresponding to the given state name,
                         or None if the state name is not found.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        for state_id in self.data["data"]["cluster"]["statussorting"]:
            state_name = self.data["data"]["cluster"]["status"][str(state_id)]["name"]
            if state_name == name:
                return state_id
        # TODO: raise Error instead of None
        return None

    def get_all_state_name(self) -> list:
        """Return the list of all available names of the states.

        Returns:
            list: A list containing all the names of the states.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        states = []
        for state_id in self.data["data"]["cluster"]["statussorting"]:
            state_name = self.data["data"]["cluster"]["status"][str(state_id)]["name"]
            states.append(state_name)
        return states

    def get_user_state(self) -> str:
        """Give the name of the current status of the user.

        Returns:
            str: The name of the current status of the user.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        status_id = self.data["data"]["status"]["status_id"]
        return self.get_state_name_by_id(status_id)

    def get_state_name_by_id(self, status_id) -> str:
        """Return the name of the state of the user by given id.

        Args:
            status_id (int): The ID of the status.

        Returns:
            str: The name of the state corresponding to the given ID.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        state_name = self.data["data"]["cluster"]["status"][str(status_id)]["name"]
        return state_name

    def get_user_state_attributes(self) -> dict:
        """Return additional information of the user's state.

        Returns:
            dict: A dictionary containing additional information of the user's state,
                  including timestamp and ID.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        data = {}
        timestamp = self.data["data"]["status"]["status_set_date"]
        data["timestamp"] = datetime.fromtimestamp(timestamp)
        data["id"] = self.data["data"]["status"]["status_id"]
        return data

    def get_last_alarm_attributes(self) -> dict:
        """Return additional information of the last alarm.

        Returns information about the most recent alarm, including its attributes like ID,
        text, date, address, location coordinates, groups involved, priority, closed status,
        new status, self-addressed status, and answered status.

        Returns:
            dict: A dictionary containing information about the last alarm.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        sorting_list = self.data["data"]["alarm"]["sorting"]
        if not sorting_list:
            return {}

        last_alarm_id = sorting_list[0]
        alarm = self.data["data"]["alarm"]["items"].get(str(last_alarm_id), {})

        groups = [self.get_group_name_by_id(group_id) for group_id in alarm.get("group", [])]

        return {
            "id": alarm.get("id"),
            "text": alarm.get("text"),
            "date": datetime.fromtimestamp(alarm.get("date")),
            "address": alarm.get("address"),
            "latitude": str(alarm.get("lat")),
            "longitude": str(alarm.get("lng")),
            "groups": groups,
            "priority": alarm.get("priority"),
            "closed": alarm.get("closed"),
            "new": alarm.get("new"),
            "self_addressed": alarm.get("ucr_self_addressed"),
            "answered": self.get_answered_state(alarm),
        }

    def get_answered_state(self, alarm):
        """Return the state of the user who answered the alarm.

        Args:
            alarm (dict): The alarm data.

        Returns:
            str: The state of the user who answered the alarm.

        """
        answered = alarm.get("ucr_answered", {})
        ucr_id = self.get_active_ucr()

        for answer_state in answered.values():
            if isinstance(answer_state, dict):
                if ucr_id in answer_state:
                    return self.get_state_name_by_id(answer_state)
            elif isinstance(answer_state, list):
                for state_id in answer_state:
                    state = answer_state.get(str(state_id), {})
                    if ucr_id in state:
                        return self.get_state_name_by_id(answer_state)
        return "not answered"

    def get_last_alarm(self) -> dict:
        """Return information of the last alarm.

        Returns:
            str: The title of the last alarm, or 'unknown' if no alarm exists.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        sorting_list = self.data["data"]["alarm"]["sorting"]
        if sorting_list:
            last_alarm_id = sorting_list[0]
            alarm = self.data["data"]["alarm"]["items"].get(str(last_alarm_id), {})
            return alarm.get("title", STATE_UNKNOWN)
        else:
            return STATE_UNKNOWN

    def get_group_name_by_id(self, group_id):
        """Return the name from the given group id.

        Args:
            group_id (int): The ID of the group.

        Returns:
            str or None: The name of the group corresponding to the given ID,
                         or None if the group ID is not found.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        try:
            group = self.data["data"]["cluster"]["group"][str(group_id)]
            return group["name"]
        except KeyError:
            return None

    def get_default_ucr(self) -> int:
        """Retrieve the default User Cluster Relation (UCR) associated with the data.

        Returns:
            int: The default UCR representing the relation between a user and a cluster.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return self.data["data"]["ucr_default"]

    def get_active_ucr(self) -> int:
        """Retrieve the active User Cluster Relation (UCR) associated with the data.

        Returns:
            int: The active UCR representing the current relation between a user and a cluster.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return self.data["data"]["ucr_active"]

    def get_default_cluster_name(self) -> str:
        """Retrieve the name of the default cluster associated with the data.

        Returns:
            str: The name of the default cluster.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        ucr_id = self.get_default_ucr()
        return self.get_cluster_name_from_ucr(ucr_id)

    def get_ucr_count(self) -> int:
        """Return the count of User Cluster Relations (UCRs) associated with the data.

        Returns:
            int: The count of UCRs.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return len(self.get_all_ucrs())

    def get_all_cluster_names(self) -> list:
        """Return a list of all cluster names associated with the data.

        Returns:
            list: A list containing all the cluster names.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        ucr_ids = list(self.data["data"]["ucr"])
        cluster_names = []
        for ucr_id in ucr_ids:
            ucr_name = self.get_cluster_name_from_ucr(ucr_id)
            cluster_names.append(ucr_name)
        return cluster_names

    def get_all_ucrs(self) -> list:
        """Retrieve a list of all User Cluster Relations (UCRs) associated with the data.

        Returns:
            list: A list containing all the UCR IDs.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return list(self.data["data"]["ucr"])

    def get_cluster_name_from_ucr(self, ucr_id) -> str:
        """Retrieve the name of the cluster associated with the given User Cluster Relation (UCR) ID.

        Args:
            ucr_id (int): The ID of the User Cluster Relation (UCR) to retrieve the cluster name for.

        Returns:
            str: The name of the cluster associated with the specified UCR ID.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return self.data["data"]["ucr"][str(ucr_id)]["name"]

    def get_cluster_id_from_ucr(self, ucr_id) -> int:
        """Retrieve the ID of the cluster associated with the given User Cluster Relation (UCR) ID.

        Args:
            ucr_id (int): The ID of the User Cluster Relation (UCR) to retrieve the cluster ID for.

        Returns:
            int: The ID of the cluster associated with the specified UCR ID.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return self.data["data"]["ucr"][str(ucr_id)]["cluster_id"]

    def get_ucr_ids(self, ucr_names) -> list:
        """Retrieve the IDs of User Cluster Relations (UCRs) associated with the given names.

        Args:
            ucr_names (list): A list of UCR names.

        Returns:
            list: A list containing the IDs of the UCRs with the specified names.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        ucr_ids = list(self.data["data"]["ucr"])
        ucr_name_ids = []
        for ucr_id in ucr_ids:
            ucr_name = self.get_cluster_name_from_ucr(ucr_id)
            if ucr_name in ucr_names:
                ucr_name_ids.append(ucr_id)
        return ucr_name_ids

    def get_accesskey(self) -> str:
        """Retrieve the access key of the user associated with the data.

        Returns:
            str: The access key of the user.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return self.data["data"]["user"]["accesskey"]

    def get_email(self) -> str:
        """Retrieve the email of the user associated with the data.

        Returns:
            str: The email address of the user.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        """
        return self.data["data"]["user"]["email"]

    def set_state(self, state_id):
        """Set the state of the user to the given id."""
        payload = json.dumps({"Status": {"id": state_id}})
        headers = {"Content-Type": "application/json"}

        if not self.accesskey:
            _LOGGER.exception("state can not be set. accesskey is missing or wrong.")
        else:
            params = {ACCESSKEY: self.accesskey, UCR: self.ucr_id}
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

    def get_cluster_version(self) -> str:
        """Retrieve the version of the cluster.

        Returns:
            str: The version of the cluster, indicating whether it's a free version,
                an alarm version, a pro version, or unknown.

        Raises:
            KeyError: If the required keys are not found in the data dictionary.

        Note:
            The version_id is extracted from the 'data' dictionary attribute of the instance.

        """
        version = self.data["data"]["cluster"]["version_id"]
        match version:
            case 1:
                return VERSION_FREE
            case 2:
                return VERSION_ALARM
            case 3:
                return VERSION_PRO
            case _:
                return VERSION_UNKNOWN
