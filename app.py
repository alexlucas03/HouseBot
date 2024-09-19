from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import datetime
from collections import defaultdict
from dish import Dish
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

dishes = []
total_points = 0
start_date_str = "2024-09-24"
end_date_str = "2024-12-13"
start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

types = ['lunch', 'dinner', 'x1']
type_index = 0

delta = datetime.timedelta(days=1)
current_date = start_date
today = datetime.date.today().strftime('%Y-%m-%d')
duration = (end_date - start_date).days
ownersArray = [None] * duration * 3
owner_to_userid = {
    'ted': '86703628',
    'dominic': '104427870',
    'truman': '106396551',
    'dimov': '104722123',
    'david': '68279200',
    'mat': '107719028',
    'christian': '93350644',
    'diego': '118125359',
    'az': '105887162',
    'leif': '89734509',
    'john': '71913836',
    'tony': '115601455',
    'arohan': '115802749',
    'stanley': '65365057',
    'eyen': '115945245',
    'brandon': '117008618',
    'jo': '125330287',
    'jase': '123732691',
    'sam': '119855908',
    'tanner': '125114421',
    'noah': '107162478',
    'aidan': '23716109',
    'kim': '123717364',
    'admin': '1'
}

pick_order = ['ted', 'dominic', 'truman', 'dimov', 'david', 'mat', 'christian', 'diego', 'az', 'leif', 'john', 'tony', 'arohan', 'stanley', 'eyen', 'brandon', 'jo', 'jase', 'sam', 'tanner', 'noah', 'aidan', 'kim']

i = 0
while current_date <= end_date:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1
            total_points += 1

        owner = ownersArray[i]
        
        dish = Dish(date=current_date, owner=owner, type=types[type_index])
        dishes.append(dish)
        i += 1
        
        if types[type_index] == 'x1':
            current_date += delta
        
        type_index = (type_index + 1) % len(types)
 
    else:
        current_date += delta

grouped_dishes = defaultdict(lambda: defaultdict(list))
for dish in dishes:
    if dish.type == 'dinner' or dish.type == 'lunch':
        total_points += 2
    elif dish.type == 'x1':
        total_points += 1
    month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
    day = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%d")
    grouped_dishes[month][day].append(dish)

points = total_points / len(owner_to_userid)
points_order = [int(points)] * len(pick_order)
original_points = [int(points)] * len(pick_order)
summed_points = int(points) * len(pick_order)

count = 0
while(summed_points < total_points):
    points_order[len(points_order) - 1 - count] += 1
    summed_points += 1
    count += 1

@app.route('/send-messages', methods=['POST'])
def send_groupme_messages():
    user = session.get('user')
    if not user or user != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    today = datetime.date.today().strftime('%Y-%m-%d')
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

    lunch_userid = owner_to_userid.get(lunch_owner, None)
    dinner_userid = owner_to_userid.get(dinner_owner, None)
    x1_userid = owner_to_userid.get(x1_owner, None)

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

    return jsonify({'success': True, 'message': 'Messages sent successfully'})

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    today = datetime.date.today().strftime('%Y-%m-%d')
    if start_date.strftime('%Y-%m-%d') <= today <= end_date.strftime('%Y-%m-%d'):
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

    recalculate_points()
    return render_template('index.html', grouped_dishes=grouped_dishes, user=user, points_order=points_order, pick_order=pick_order)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['user'] = username
        if username in pick_order or username == 'admin':
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/change-owner', methods=['POST'])
def change_owner():
    data = request.get_json()
    dish_date = data.get('date')
    dish_type = data.get('type')
    new_owner = data.get('owner')

    for index, dish in enumerate(dishes):
        if dish.date == dish_date and dish.type == dish_type:
            dish.owner = new_owner
            ownersArray[index] = new_owner
            return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Dish not found'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def recalculate_points():
    global total_points, points_order

    points_order = original_points.copy()
    for dish in dishes:
        if dish.owner:
            index = pick_order.index(dish.owner)
            if dish.weekday == 'Sunday' and dish.type == 'dinner':
                points_order[index] -= 3
            elif dish.weekday != 'Sunday' and dish.type == 'dinner' or dish.type == 'lunch':
                points_order[index] -= 2
            elif dish.type == 'x1':
                points_order[index] -= 1