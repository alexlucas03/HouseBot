class Choreperson:
    def __init__(self, name, userID, day, lates, fines):
        self.name = name
        self.userID = userID
        self.day = day
        self.lates = lates
        self.fines = fines

    def to_dict(self):
        return {
            'name': self.name,
            'userID': self.userID,
            'day': self.day,
            'lates': self.lates,
            'fines': self.fines,
        }
