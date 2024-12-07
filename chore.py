class Chore:
    def __init__(self, name, description, importance, frequency, done, person, day1, day2, day3):
        self.name = name
        self.description = description
        self.importance = importance
        self.frequency = frequency
        self.done = done
        self.person = person
        self.day1 = day1
        self.day2 = day2
        self.day3 = day3

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'importance': self.importance,
            'frequency': self.frequency,
            'done': self.done,
            'person': self.person,
            'day1': self.day1,
            'day2': self.day2,
            'day3': self.day3
        }
