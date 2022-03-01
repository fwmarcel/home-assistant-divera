"""Connector class to retrieve data, which is use by the weather and sensor enities."""
import logging
from datetime import datetime
import requests

from .const import DEFAULT_TIMEOUT, DIVERA_URL
from .data import Vehicle

_LOGGER = logging.getLogger(__name__)


class DiveraData:
    """Data object for Divera"""

    def __init__(self, hass, api_key):
        """Initialize the data object."""
        self._hass = hass

        self.success = False
        self.latest_update = None

        self.data = None

        if api_key != "":
            self.api_key = api_key

    async def async_update(self):
        """Async wrapper for update method."""
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Get the latest data from Divera"""
        timestamp = datetime.now()
        # Only update on the hour and when not updated yet

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
                _LOGGER.error("Error: {}".format(str(ex)))
                self.success = False
            else:
                self.latest_update = timestamp
            _LOGGER.debug("Values updated at %s", self.latest_update)

    def get_user(self):
        """Returns Information of user"""
        data = {}
        data["firstname"] = self.data["data"]["user"]["firstname"]
        data["lastname"] = self.data["data"]["user"]["lastname"]
        data["fullname"] = data["firstname"] + " " + data["lastname"]
        data["email"] = self.data["data"]["user"]["email"]
        return data

    def get_state(self):
        """returns state of divera"""
        id = self.data["data"]["status"]["status_id"]
        state_name = self.data["data"]["cluster"]["status"][str(id)]["name"]
        return state_name

    def get_state_attributes(self):
        """return aditional information of state"""
        data = {}
        timestamp = self.data["data"]["status"]["status_set_date"]
        data["timestamp"] = datetime.fromtimestamp(timestamp)
        data["id"] = self.data["data"]["status"]["status_id"]
        return data

    def get_last_alarm_attributes(self):
        """return aditional information of last alarm"""
        last_alarm_id = self.data["data"]["alarm"]["sorting"][0]
        alarm = self.data["data"]["alarm"]["items"][str(last_alarm_id)]

        groups = map(self.__search_group, alarm["group"])
        return {
            "text": alarm["text"],
            "date": datetime.fromtimestamp(alarm["date"]),
            "address": alarm["address"],
            "lat": str(alarm["lat"]),
            "lng": str(alarm["lng"]),
            "groups": list(groups),
            "priority": alarm["priority"],
            "closed": alarm["closed"],
            "new": alarm["new"],
        }

    def get_last_alarm(self):
        """return informations of last alarm"""
        last_alarm_id = self.data["data"]["alarm"]["sorting"][0]
        alarm = self.data["data"]["alarm"]["items"][str(last_alarm_id)]
        return alarm["title"]

    def __search_group(self, group_id):
        group = self.data["data"]["cluster"]["group"][str(group_id)]
        return group["name"]

    def get_vehicles(self):
        """return list of vehicles"""
        raw_vehicles = self.data["data"]["cluster"]["vehicle"]
        vehicles = []
        for id in raw_vehicles:
            v = raw_vehicles[id]
            vehicles.append(Vehicle(v))
        return vehicles

    def get_id(self):
        """return if of user"""
        return list(self.data["data"]["ucr"])[0]
