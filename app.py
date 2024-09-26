#todo:
#gcal
#oop
#auto send msgs
#db integration

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from collections import defaultdict
from dish import Dish
from person import Person
import requests
import json
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://default:************@ep-falling-fire-a4ke12jz.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

dishes = []
people_objects = []
start_date_str = "2024-09-24"
end_date_str = "2024-12-13"
start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

types = ['lunch', 'dinner', 'x1']
type_index = 0

delta = datetime.timedelta(days=1)
current_date = start_date
today = datetime.date.today().strftime('%Y-%m-%d')

while current_date <= end_date:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1
        
        dish = Dish(date=current_date, type=types[type_index])
        dishes.append(dish)
        
        if types[type_index] == 'x1':
            current_date += delta
        
        type_index = (type_index + 1) % len(types)
 
    else:
        current_date += delta

grouped_dishes = defaultdict(lambda: defaultdict(list))
for dish in dishes:
    month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
    day = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%d")
    grouped_dishes[month][day].append(dish)

@app.route('/')
def index():
    global lunch_owner, dinner_owner, x1_owner, people_objects

    if 'user' not in session:
        return redirect(url_for('login'))
    
    create_people_objects()
    user = session['user']
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    if start_date.strftime('%Y-%m-%d') <= today <= end_date.strftime('%Y-%m-%d'):
        for person in people_objects:
            for dish in person.dishes:
                dish_month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
                dish_day = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%d")
                for specific_dish in grouped_dishes[dish_month][dish_day]:
                    if specific_dish.type == dish.type:
                        specific_dish.owner == person.name

        today_lunch = None
        today_dinner = None
        today_x1 = None

        for dish in dishes:
            if dish.date == today:
                if dish.type == "lunch":
                    today_lunch = dish
                elif dish.type == "dinner":
                    today_dinner = dish
                elif dish.type == "x1":
                    today_x1 = dish
        
        lunch_owner = today_lunch.owner if today_lunch and today_lunch.owner else 'Not Assigned'
        dinner_owner = today_dinner.owner if today_dinner and today_dinner.owner else 'Not Assigned'
        x1_owner = today_x1.owner if today_x1 and today_x1.owner else 'Not Assigned'

        for person in people_objects:
            person.CalculatePoints()

    return render_template('index.html', grouped_dishes=grouped_dishes, user=user, people_objects=people_objects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        person = PeopleModel.query.filter_by(name=username).first()
        if person or username == 'admin':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="User not found")    
    return render_template('login.html')

@app.route('/change-owner', methods=['POST'])
def change_owner():
    data = request.get_json()
    dish_date = data.get('date')
    dish_type = data.get('type')

    current_user = session.get('user', None)
    person = PeopleModel.query.filter_by(name=current_user).first()
    new_dish = f"{dish_date},{dish_type}"

    db.session.execute(
        "UPDATE people SET dishes = array_append(dishes, :new_dish) WHERE userid = :user_id",
        {"new_dish": new_dish, "user_id": person.userid}
    )
    db.session.commit()

    return jsonify({'success': True, 'message': 'Dish added successfully'}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/people_objects")
def create_people_objects():
    global people_objects
    people_rows = PeopleModel.query.all()

    for row in people_rows:
        person_obj = Person(name=row.name, userID=row.userid, pickOrder=0, totalPoints=row.totalpoints, dishes=row.dishes)
        people_objects.append(person_obj)

    people_objects.sort(key=lambda person: person.pickOrder)
    return {"people": [person.to_dict() for person in people_objects]}

class PeopleModel(db.Model):
    __tablename__ = 'people'
    userid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    totalpoints = db.Column(db.Integer)
    dishes = db.Column(db.Array)

@app.route('/send-messages', methods=['POST'])
def send_groupme_messages():
    lunch = PeopleModel.query.filter_by(name=lunch_owner).first()
    lunch_userid = lunch.userID
    dinner = PeopleModel.query.filter_by(name=dinner_owner).first()
    dinner_userid = lunch.userID
    x1 = PeopleModel.query.filter_by(name=x1_owner).first()
    x1_userid = lunch.userID
    
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