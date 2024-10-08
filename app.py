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

def init(autosend):
    global start_date, end_date, test_today, lunch_owner, dinner_owner, x1_owner, person, user, people_objects, dishes, person
    start_date = datetime.datetime(2024, 9, 24)
    end_date = datetime.datetime(2024, 12, 13)
    test_today = datetime.datetime.now()

    create_all_month_objects()
    dishes = september_objects + october_objects + november_objects + december_objects
    create_people_objects()
    person = None
    if not autosend:
        user = session['user']
        for people in people_objects:
            if people.name == user:
                person = people
                break

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

    if not autosend and user != 'admin':
        person = calculate_points(person)
    elif not autosend:
        for i, person in enumerate(people_objects):
            people_objects[i] = calculate_points(person)

@app.route('/', methods=['GET', 'POST'])
def login():
    create_people_objects()
    session.clear()
    if request.method == 'POST':
        username= request.form['username']
        if username == 'admin':
            session['user'] = username
            return redirect(url_for('admin'))
        else:
            person = None
            for people in people_objects:
                if people.name == username:
                    person = people
                    break
            if person:
                session['user'] = username
                return redirect(url_for('client'))
            else:
                return render_template('login.html', error="User not found")
    return render_template('login.html')

@app.route('/all')
def index():
    global lunch_owner, dinner_owner, x1_owner, people_objects, dishes, september_objects, october_objects, november_objects, december_objects

    if 'user' not in session:
        return redirect('/')
    init(False)
    return render_template('index.html', september_objects=september_objects, october_objects=october_objects, november_objects=november_objects, december_objects=december_objects, user=user, person=person, people_objects=people_objects, test_today=test_today)

@app.route('/client')
def client():
    if 'user' not in session:
        return redirect('/')
    init(False)
    my_dishes = []
    for dish in dishes:
        if dish.owner == person.name:
            my_dishes.append(dish)

    return render_template('client.html', my_dishes=my_dishes, person=person)

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/')
    init(False)
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
    
@app.route('/send-messages', methods=['GET'])
def send_groupme_messages():
    # Ensure global variables are initialized
    init(True)

    # Find the lunch, dinner, and x1 owners
    lunch_userid = next((person.userID for person in people_objects if person.name == lunch_owner), None)
    dinner_userid = next((person.userID for person in people_objects if person.name == dinner_owner), None)
    x1_userid = next((person.userID for person in people_objects if person.name == x1_owner), None)
    
    url = "https://api.groupme.com/v3/bots/post"

    def send_message(message, owner, owner_userid, owner_loci_start, owner_loci_end):
        data = {
            "text": message,
            "bot_id": "c9ed078f3de7c89547308a050a",
        }
        if owner != 'Not Assigned' and owner_userid:
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

    return jsonify({'success': True, 'message': 'Messages sent successfully'}), 200

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

class BaseModel(db.Model):
    __abstract__ = True
    year = db.Column(db.String)
    day = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    owner = db.Column(db.String)
    type = db.Column(db.String)

months = ['September', 'October', 'November', 'December']

for month in months:
    tablename = month.lower()  # e.g., 'september', 'october'
    globals()[f'{month}Model'] = type(f'{month}Model', (BaseModel,), {
        '__tablename__': tablename
    })

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
    return person
def create_month_objects(month, model, global_objects):
    dish_rows = model.query.all()
    global_objects.clear()  # Clear the existing objects, if any
    for row in dish_rows:
        dish_obj = Dish(
            year=int(row.year),
            month=month,
            day=int(row.day),
            type=row.type,
            owner=row.owner,
            id=row.id
        )
        global_objects.append(dish_obj)
    global_objects.sort(key=lambda dish: int(dish.id))

def create_all_month_objects():
    global september_objects, october_objects, november_objects, december_objects

    month_data = [
        (9, SeptemberModel, september_objects),
        (10, OctoberModel, october_objects),
        (11, NovemberModel, november_objects),
        (12, DecemberModel, december_objects)
    ]

    for month, model, global_objects in month_data:
        create_month_objects(month, model, global_objects)
