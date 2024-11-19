class Laundry:
    def __init__(self, name, appliance, rank):
        self.name = name
        self.appliance = appliance
        self.rank = rank

    def to_dict(self):
        return {
            'name': self.name,
            'userID': self.appliance,
            'pickOrder': self.rank,
        }
