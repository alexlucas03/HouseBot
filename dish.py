import datetime

class Dish:
    def __init__(self, date, type, owner=None):
        self.weekday = date.strftime("%A")
        self.date = date.strftime("%Y-%m-%d")
        self.type = type
        self.owner = owner

    def to_dict(self):
        return {
            'date': self.date,
            'type': self.type,
            'weekday': self.weekday,
            'owner': self.owner
        }