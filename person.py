class Person:
    def __init__(self, name, user_id, points):
        self.name = name
        self.user_id = user_id
        self.points = points

    def to_dict(self):
        return {
            'name': self.name,
            'user_id': self.user_id,
            'points': self.points
        }
