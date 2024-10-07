from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import text
import datetime
from datetime import timedelta
from dish import Dish
from person import Person
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://default:mk2aS9URHwOf@ep-falling-fire-a4ke12jz.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

dishes = []
people_objects = []
start_date_str = "2024-09-24"
end_date_str = "2024-12-13"
start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
test_today = datetime.datetime.now()

@app.route('/')
def index():
    global lunch_owner, dinner_owner, x1_owner, people_objects, dishes, september_objects, october_objects, november_objects, december_objects

    if 'user' not in session:
        return redirect(url_for('login'))
    
    create_september_objects()
    create_october_objects()
    create_november_objects()
    create_december_objects()
    dishes = september_objects + october_objects + november_objects + december_objects
    create_people_objects()

    user = session['user']
    person = None
    for people in people_objects:
        if people.name == user:
            person = people

    today = datetime.date.today()

    if today.strftime("%A") == 'Saturday':
        today += timedelta(days=1)

    if start_date.date() <= today <= end_date.date():
        today_lunch = None
        today_dinner = None
        today_x1 = None

        for dish in dishes:
            if dish.date_obj == today:
                if dish.weekday != 'Sunday' and dish.type == "lunch":
                    today_lunch = dish
                elif dish.type == "dinner":
                    today_dinner = dish
                elif dish.type == "x1":
                    today_x1 = dish

        lunch_owner = today_lunch.owner if today_lunch and today_lunch.owner else 'Not Assigned'
        dinner_owner = today_dinner.owner if today_dinner and today_dinner.owner else 'Not Assigned'
        x1_owner = today_x1.owner if today_x1 and today_x1.owner else 'Not Assigned'

    if user != 'admin':
        calculate_points(person)
    else:
        for person in people_objects:
            calculate_points(person)
    return render_template('index.html', september_objects=september_objects, october_objects=october_objects, november_objects=november_objects, december_objects=december_objects, user=user, person=person, people_objects=people_objects, test_today=test_today)

@app.route('/client')
def client():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    create_september_objects()
    create_october_objects()
    create_november_objects()
    create_december_objects()
    dishes = september_objects + october_objects + november_objects + december_objects
    my_dishes = []
    create_people_objects()
    user = session['user']
    person = None
    for people in people_objects:
        if people.name == user:
            person = people

    for dish in dishes:
        if dish.owner == person.name:
            my_dishes.append(dish)

    return render_template('client.html', my_dishes=my_dishes, person=person)

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    create_september_objects()
    create_october_objects()
    create_november_objects()
    create_december_objects()
    dishes = september_objects + october_objects + november_objects + december_objects
    create_people_objects()

    for person in people_objects:
        calculate_points(person)

    return render_template('admin.html', people_objects=people_objects)

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/change-owner', methods=['POST'])
def change_owner():
    data = request.get_json()
    month = data.get('month')
    id = data.get('id')
    owner = data.get('owner')

    if owner is None:
        owner_value = 'NULL'
    else:
        owner_value = f"'{owner}'"

    db.session.execute(
        text(f"UPDATE {month} SET owner = {owner_value} WHERE id = '{id}'")
    )
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Dish owner updated successfully'}), 200
    
@app.route('/send-messages', methods=['POST'])
def send_groupme_messages():
    lunch_userid = None
    for person in people_objects:
        if person.name == lunch_owner:
            lunch_userid = person.userID
    dinner_userid = None
    for person in people_objects:
        if person.name == dinner_owner:
            dinner_userid = person.userID
    x1_userid = None
    for person in people_objects:
        if person.name == x1_owner:
            x1_userid = person.userID
    
    url = "https://api.groupme.com/v3/bots/post"

    def send_message(message, owner, owner_userid, owner_loci_start, owner_loci_end):
        data = {
            "text": message,
            "bot_id": "c9ed078f3de7c89547308a050a",
        }
        if owner != 'Not Assigned':
            data["attachments"] = [
                {
                    "type": "mentions",
                    "user_ids": [owner_userid],
                    "loci": [[owner_loci_start, owner_loci_end]]
                }
            ]
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        return response

    # Send lunch message
    lunch_message = f"Lunch: @{lunch_owner}"
    send_message(lunch_message, lunch_owner, lunch_userid, 7, 7 + len(lunch_owner))

    # Send dinner message
    dinner_message = f"Dinner: @{dinner_owner}"
    send_message(dinner_message, dinner_owner, dinner_userid, 8, 8 + len(dinner_owner))

    # Send x1 message
    x1_message = f"x1: @{x1_owner}"
    send_message(x1_message, x1_owner, x1_userid, 4, 4 + len(x1_owner))

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username == 'admin':
            session['user'] = username
            return redirect(url_for('admin'))
        else:
            person = PeopleModel.query.filter_by(name=username).first()
            if person:
                session['user'] = username
                return redirect(url_for('client'))
            else:
                return render_template('login.html', error="User not found")
    return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/initdish', methods=['POST', 'GET'])
def initdish():
    db.session.execute(
        text("DELETE FROM september")
    )
    db.session.commit
    db.session.execute(
        text("DELETE FROM october")
    )
    db.session.commit
    db.session.execute(
        text("DELETE FROM november")
    )
    db.session.commit
    db.session.execute(
        text("DELETE FROM december")
    )
    db.session.commit

    types = ['lunch', 'dinner', 'x1']
    type_index = 0
    i = 0

    delta = datetime.timedelta(days=1)
    current_date = start_date

    while current_date <= end_date:
        day_of_week = current_date.strftime("%A")
        
        if day_of_week != "Saturday":
            if day_of_week == "Sunday" and type_index == 0:
                type_index = 1
            db.session.execute(
                text(f"INSERT INTO {current_date.strftime('%B')} (year, day, id, owner, type) "
                    f"VALUES ({current_date.year}, {current_date.day}, {i}, null, '{types[type_index]}')")
            )
            db.session.commit()
            i += 1
            
            if types[type_index] == 'x1':
                current_date += delta
            
            type_index = (type_index + 1) % len(types)
    
        else:
            current_date += delta
    
    return jsonify({'success': True, 'message': 'Dishes initialized successfully'})

class PeopleModel(db.Model):
    __tablename__ = 'people'
    userid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    pickorder = db.Column(db.String)
    totalpoints = db.Column(db.Integer)

class SeptemberModel(db.Model):
    __tablename__ = 'september'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)
    
class OctoberModel(db.Model):
    __tablename__ = 'october'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

class NovemberModel(db.Model):
    __tablename__ = 'november'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

class DecemberModel(db.Model):
    __tablename__ = 'december'
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

@app.route("/people_objects")
def create_people_objects():
    global people_objects
    people_rows = PeopleModel.query.all()
    people_objects = []
    for row in people_rows:
        person_obj = Person(name=row.name, userID=row.userid, pickOrder=row.pickorder, totalPoints=row.totalpoints)
        people_objects.append(person_obj)

    people_objects.sort(key=lambda person: int(person.pickOrder))
    return {"people": [person.to_dict() for person in people_objects]}

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

def create_september_objects():
    global september_objects
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

def create_october_objects():
    global october_objects
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

def create_november_objects():
    global november_objects
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

def create_december_objects():
    global december_objects
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
