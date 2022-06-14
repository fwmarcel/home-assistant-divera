
class Vehicle:
    def __init__(self, data):
        self.data = data

    def get_name(self):
        return self.data["name"]

    def get_location(self):
        return (self.data["lat"], self.data["lng"])

    def get_fms_state(self):
        return self.data["fmsstatus_id"]

class StateNotFoundError(Exception):
    pass
