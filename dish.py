class Dish:
    def __init__(self, date, time, owner):
        self.date = date
        self.time = time
        self.owner = owner

    def to_dict(self):
        return {
            'date': self.date,
            'time': self.time,
            'owner': self.owner
        }