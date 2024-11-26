from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import datetime
from datetime import timedelta
from dish import Dish
from person import Person
import requests
import json
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://default:mk2aS9URHwOf@ep-falling-fire-a4ke12jz.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

dishes = []
people_objects = []
months = []

def init(logged_in):
    global start_date, end_date, lunch_owner, dinner_owner, x1_owner, person, user, people_objects, dishes, person, months

    months.clear()

    start_date_row = db.session.execute(text("SELECT year, month, day FROM startend WHERE id = '1'")).fetchone()
    end_date_row = db.session.execute(text("SELECT year, month, day FROM startend WHERE id = '2'")).fetchone()

    start_year, start_month, start_day = start_date_row
    end_year, end_month, end_day = end_date_row

    start_date = datetime.datetime(int(start_year), int(start_month), int(start_day))
    end_date = datetime.datetime(int(end_year), int(end_month), int(end_day))
    current_date = start_date
    while current_date <= end_date:
        months.append(current_date.strftime("%B"))
        next_month = current_date.month % 12 + 1
        year = current_date.year + (current_date.month // 12)
        current_date = datetime.datetime(year, next_month, 1)

    for month in months:
        globals()[month.lower() + "_objects"] = []

    for month in months:
        model_name = f'{month}Model'
        tablename = month.lower()

        if model_name not in globals():
            globals()[model_name] = type(model_name, (BaseModel,), {
                '__tablename__': tablename
            })

    dishes.clear()
    create_all_month_objects()
    for month in months:
        dishes += globals()[f"{month.lower()}_objects"]
    create_people_objects()
    person = None
    if not logged_in:
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

    if not logged_in and user != 'admin':
        person = calculate_points(person)
    elif not logged_in:
        for i, person in enumerate(people_objects):
            people_objects[i] = calculate_points(person)

@app.route('/', methods=['GET', 'POST'])
def login():
    create_people_objects()
    session.clear()
    if request.method == 'POST':
        username= request.form['username']
        passw = request.form['password']
        if passw == "":
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
        else:
            if passw == 'alex':
                session['user'] = 'admin'
                return redirect(url_for('admin'))
            else:
                return render_template('login.html', error="Incorrect password")
            
    return render_template('login.html')

@app.route('/all')
def index():
    global lunch_owner, dinner_owner, x1_owner, people_objects, dishes
    if 'user' not in session:
        return redirect('/')
    init(False)
    
    month_objects = {month.lower(): globals()[f"{month.lower()}_objects"] for month in months}
    return render_template('index.html', months=months, month_objects=month_objects, user=user, person=person, people_objects=people_objects)

@app.route('/initquarter', methods=['POST', 'GET'])
def initquarter():
    if 'user' not in session:
        return redirect('/')
    init(False)

    return render_template('initquarter.html')

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
    
@app.route('/send-messages', methods=['POST', 'GET'])
def send_groupme_messages():
    init(True)

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

    if datetime.date.today().strftime("%A") != "Saturday" and datetime.date.today().strftime("%A") != "Sunday":
        lunch_message = f"Lunch: @{lunch_owner}"
        send_message(lunch_message, lunch_owner, lunch_userid, 7, 7 + len(lunch_owner))

    dinner_message = f"Dinner: @{dinner_owner}"
    send_message(dinner_message, dinner_owner, dinner_userid, 8, 8 + len(dinner_owner))

    x1_message = f"x1: @{x1_owner}"
    send_message(x1_message, x1_owner, x1_userid, 4, 4 + len(x1_owner))

    return jsonify({'success': True, 'message': 'Messages sent successfully'}), 200

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/initdish', methods=['POST', 'GET'])
def initdish():
    start_year = str(request.form['start_year'])
    start_month = str(request.form['start_month'])
    start_day = str(request.form['start_day'])
    end_year = str(request.form['end_year'])
    end_month = str(request.form['end_month'])
    end_day = str(request.form['end_day'])

    db.session.execute(
        text(f"UPDATE startend SET year = {start_year} WHERE id = '1'")
    )
    db.session.commit()
    db.session.execute(
        text(f"UPDATE startend SET month = {start_month} WHERE id = '1'")
    )
    db.session.commit()
    db.session.execute(
        text(f"UPDATE startend SET day = {start_day} WHERE id = '1'")
    )
    db.session.commit()
    db.session.execute(
        text(f"UPDATE startend SET year = {end_year} WHERE id = '2'")
    )
    db.session.commit()
    db.session.execute(
        text(f"UPDATE startend SET month = {end_month} WHERE id = '2'")
    )
    db.session.commit()
    db.session.execute(
        text(f"UPDATE startend SET day = {end_day} WHERE id = '2'")
    )
    db.session.commit()

    init(False)

    for month in months:
        db.session.execute(
            text(f"DELETE FROM {month.lower()}")
        )
        db.session.commit()

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

@app.route('/initpeople', methods=['POST', 'GET'])
def initpeople():
    init(True)
    db.session.execute(text(f"DELETE FROM people"))
    db.session.commit()
    people_data = request.form.getlist('name[]')
    userids = request.form.getlist('userid[]')
    totalPoints = calculate_total_points()
    i = 0
    for name, userid in zip(people_data, userids):
        db.session.execute(text(f"INSERT INTO people VALUES ('{name}', '{userid}', '{i}', '0')"))
        db.session.commit()
        i += 1
    round1ppp = int(totalPoints / (i))
    db.session.execute(text(f"UPDATE people SET totalpoints = '{round1ppp}'"))
    db.session.commit()
    remainder = totalPoints - (round1ppp * i)
    while remainder > 0:
        db.session.execute(text(f"UPDATE people SET totalpoints = '{round1ppp + 1}' WHERE pickorder = '{i - 1}'"))
        db.session.commit()
        i -= 1
        remainder -= 1
    return jsonify({'success': True, 'message': f"{remainder}"})

class PeopleModel(db.Model):
    __tablename__ = 'people'
    userid = db.Column(db.String, primary_key=True)
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

@app.route('/people_objects')
def create_people_objects():
    global people_objects
    people_rows = db.session.execute(text("SELECT * FROM people"))
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
    global_objects.clear()
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
    for month in months:
        model = globals()[f"{month}Model"]
        global_objects = globals()[f"{month.lower()}_objects"]
        month_int = time.strptime(month, "%B").tm_mon

        create_month_objects(month_int, model, global_objects)

class Lunch(db.Model):
    __tablename__ = 'lunch'
    name = db.Column(db.String, primary_key=True)

class Dinner(db.Model):
    __tablename__ = 'dinner'
    name = db.Column(db.String, primary_key=True)

@app.route('/lateplate_lunch', methods=['GET'])
def lateplate_lunch():
    lunch_items = [lunch.name for lunch in Lunch.query.all()]
    if lunch_items:
        lunch_message = "@g Lunch late plates: " + ", ".join(lunch_items)
    else:
        lunch_message = "@g No lunch late plates"

    db.session.execute(text("DELETE FROM lunch"))
    db.session.commit()

    url = "https://api.groupme.com/v3/bots/post"
    
    data = {
            "text": lunch_message,
            "bot_id": "037354844906b998b0ae3d2fe4",
    }
    data["attachments"] = [
        {
            "type": "mentions",
            "user_ids": ["8655406"],
            "loci": [[0, 1]]
        }
    ]
    headers = {
        "Content-Type": "application/json",
        "X-Access-Token": "JkI3aAERgvJtCe9ePajw9YkNZu6KFwrpNgL628YZ"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200 or response.status_code == 202:
        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "Failed to send DM", "error": response.content.decode(), "status": response.status_code}), response.status_code
    
@app.route('/lateplate_dinner', methods=['GET'])
def lateplate_dinner():
    dinner_items = [dinner.name for dinner in Dinner.query.all()]
    if dinner_items:
        dinner_message = "@g Dinner late plates: " + ", ".join(dinner_items)
    else:
        dinner_message = "@g No dinner late plates"

    db.session.execute(text("DELETE FROM dinner"))
    db.session.commit()

    url = "https://api.groupme.com/v3/bots/post"
    
    data = {
            "text": dinner_message,
            "bot_id": "037354844906b998b0ae3d2fe4",
    }
    data["attachments"] = [
        {
            "type": "mentions",
            "user_ids": ["8655406"],
            "loci": [[0, 1]]
        }
    ]
    headers = {
        "Content-Type": "application/json",
        "X-Access-Token": "JkI3aAERgvJtCe9ePajw9YkNZu6KFwrpNgL628YZ"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200 or response.status_code == 202:
        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "Failed to send DM", "error": response.content.decode(), "status": response.status_code}), response.status_code
    
@app.route('/lunchlp', methods=['GET'])
def lunchlp():
    init(False)
    lunch_rows = db.session.execute(text("SELECT * FROM lunch"))
    if not any(row[0] == person.name for row in lunch_rows):
        db.session.execute(
            text(f"INSERT INTO lunch VALUES ('{person.name}')")
        )
        db.session.commit()
    return redirect(url_for('client'))

@app.route('/dinnerlp', methods=['GET'])
def dinnerlp():
    init(False)
    dinner_rows = db.session.execute(text("SELECT * FROM dinner"))
    if  not any(row[0] == person.name for row in dinner_rows):
        db.session.execute(
            text(f"INSERT INTO dinner VALUES ('{person.name}')")
        )
        db.session.commit()
    return redirect(url_for('client'))

def calculate_total_points():
    total_points = 0
    current_date = start_date

    while current_date <= end_date:
        day_of_week = current_date.strftime("%A")

        if day_of_week == "Saturday":
            total_points += 0
        elif day_of_week == "Sunday":
            total_points += 4
        else:
            total_points += 5

        current_date += datetime.timedelta(days=1)

    return total_points