class Person:
    def __init__(self, name, userID, pickOrder, totalPoints):
        self.name = name
        self.userID = userID
        self.pickOrder = pickOrder
        self.totalPoints = totalPoints
        self.pointsNeeded = totalPoints
        self.dishes = []

    def to_dict(self):
        return {
            'name': self.date,
            'userID': self.userID,
            'pickOrder': self.pickOrder,
            'pointsNeeded': self.pointsNeeded,
            'dishes': self.dishes
        }
    
    def CalculatePoints(self):
        self.pointsNeeded = self.totalPoints
        for dish in self.dishes:
            if dish.weekday == 'Sunday' and dish.type == 'dinner':
                self.pointsNeeded -= 3
            elif dish.weekday != 'Sunday' and dish.type == 'dinner' or dish.type == 'lunch':
                self.pointsNeeded -= 2
            elif dish.type == 'x1':
                self.pointsNeeded -= 1
