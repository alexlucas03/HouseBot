class Person:
    def __init__(self, name, userID, pickOrder, totalPoints):
        self.name = name
        self.userID = userID
        self.pickOrder = pickOrder
        self.totalPoints = totalPoints
        self.pointsNeeded = totalPoints

    def to_dict(self):
        return {
            'name': self.name,
            'userID': self.userID,
            'pickOrder': self.pickOrder,
            'pointsNeeded': self.pointsNeeded,
        }
