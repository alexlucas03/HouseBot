class Chore:
    def __init__(self, name, description, importance, frequency, done, person, day):
        self.name = name
        self.description = description
        self.importance = importance
        self.frequency = frequency
        self.done = done
        self.person = person
        self.day = day

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'importance': self.importance,
            'frequency': self.frequency,
            'done': self.done,
            'person': self.person,
            'day': self.day
        }
