import datetime

class Dish:
    def __init__(self, year, month, day, type, owner, id):
        self.date_obj = datetime.date(year, month, day)
        self.month = month
        self.weekday = self.date_obj.strftime("%A")
        self.date_str = self.date_obj.strftime("%Y-%m-%d")
        self.type = type
        self.owner = owner
        self.id = id
        self.day = day

    def to_dict(self):
        return {
            'date_obj': self.date_obj,
            'date_str': self.date_str,
            'month': self.month,
            'type': self.type,
            'weekday': self.weekday,
            'owner': self.owner,
            'id': self.id
        }
