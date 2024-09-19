import datetime

class Dish:
    def __init__(self, date, type, owner):
        self.date = date
        self.type = type
        self.owner = owner
        self.weekday = self.date.strftime("%A")

    def to_dict(self):
        return {
            'date': self.date,
            'type': self.type,
            'owner': self.owner,
            'weekday': self.weekday
        }