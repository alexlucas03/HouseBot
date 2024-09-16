class Dish:
    def __init__(self, date, type, owner):
        self.date = date
        self.type = type
        self.owner = owner

    def to_dict(self):
        return {
            'date': self.date,
            'type': self.type,
            'owner': self.owner
        }