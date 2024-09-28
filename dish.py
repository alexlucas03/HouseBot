import datetime

class Dish:
    def __init__(self, year, month, day, dish_type, owner, id):
        self.date_obj = datetime.date(year, month, day)
        self.weekday = self.date_obj.strftime("%A")
        self.date_str = self.date_obj.strftime("%Y-%m-%d")
        self.type = dish_type
        self.owner = owner
        self.id - id

    def to_dict(self):
        return {
            'date': self.date,
            'type': self.type,
            'weekday': self.weekday,
            'owner': self.owner,
            'id': self.id
        }
