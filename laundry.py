class Laundry:
    def __init__(self, name, appliance, rank, checksleft):
        self.name = name
        self.appliance = appliance
        self.rank = rank
        self.checksleft = checksleft

    def to_dict(self):
        return {
            'name': self.name,
            'userID': self.appliance,
            'pickOrder': self.rank,
            'checksleft': self.checksleft
        }
