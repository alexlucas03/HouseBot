from flask_sqlalchemy import SQLAlchemy
from dish import Dish
from person import Person

db = SQLAlchemy()

class PeopleModel(db.Model):
    __tablename__ = 'people'
    userid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    pickorder = db.Column(db.String)
    totalpoints = db.Column(db.Integer)

    @staticmethod
    def create_people_objects():
        global people_objects
        people_rows = PeopleModel.query.all()
        people_objects = []
        for row in people_rows:
            person_obj = Person(name=row.name, userID=row.userid, pickOrder=row.pickorder, totalPoints=row.totalpoints)
            people_objects.append(person_obj)

        people_objects.sort(key=lambda person: int(person.pickOrder))
        return {"people": [person.to_dict() for person in people_objects]}
    
    @staticmethod
    def calculate_points(person):
        points = int(person.totalPoints)
        for dish in dishes:
            if person.name == dish.owner:
                if dish.weekday == 'Sunday' and dish.type == 'dinner':
                    points -= 3
                elif (dish.type == 'lunch' or dish.type == 'dinner') and dish.weekday != 'Sunday':
                    points -= 2
                elif dish.type == 'x1':
                    points -= 1
        person.pointsNeeded = str(points)

class SeptemberModel(db.Model):
    __tablename__ = 'september'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

    @staticmethod
    def create_september_objects():
        dish_rows = SeptemberModel.query.all()
        september_objects = []
        for row in dish_rows:
            dish_obj = Dish(
                year=int(row.year),
                month=9,
                day=int(row.day),
                type=row.type,
                owner=row.owner,
                id=row.id
            )
            september_objects.append(dish_obj)
        september_objects.sort(key=lambda dish: int(dish.id))
        return september_objects

class OctoberModel(db.Model):
    __tablename__ = 'october'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

    @staticmethod
    def create_october_objects():
        dish_rows = OctoberModel.query.all()
        october_objects = []
        for row in dish_rows:
            dish_obj = Dish(
                year=int(row.year),
                month=10,
                day=int(row.day),
                type=row.type,
                owner=row.owner,
                id=row.id
            )
            october_objects.append(dish_obj)
        october_objects.sort(key=lambda dish: int(dish.id))
        return october_objects

class NovemberModel(db.Model):
    __tablename__ = 'november'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

    @staticmethod
    def create_november_objects():
        dish_rows = NovemberModel.query.all()
        november_objects = []
        for row in dish_rows:
            dish_obj = Dish(
                year=int(row.year),
                month=11,
                day=int(row.day),
                type=row.type,
                owner=row.owner,
                id=row.id
            )
            november_objects.append(dish_obj)
        november_objects.sort(key=lambda dish: int(dish.id))
        return november_objects

class DecemberModel(db.Model):
    __tablename__ = 'december'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

    @staticmethod
    def create_december_objects():
        dish_rows = DecemberModel.query.all()
        december_objects = []
        for row in dish_rows:
            dish_obj = Dish(
                year=int(row.year),
                month=12,
                day=int(row.day),
                type=row.type,
                owner=row.owner,
                id=row.id
            )
            december_objects.append(dish_obj)
        december_objects.sort(key=lambda dish: int(dish.id))
        return december_objects
