from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import datetime
from collections import defaultdict
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Define the Person class
class Person:
    def __init__(self, name, user_id, points=0):
        self.name = name
        self.user_id = user_id
        self.points = points

    def to_dict(self):
        return {
            'name': self.name,
            'user_id': self.user_id,
            'points': self.points
        }

# Define the Dish class
class Dish:
    def __init__(self, date, owner, dish_type):
        self.date = date
        self.owner = owner  # This should be a Person object
        self.dish_type = dish_type

    def to_dict(self):
        return {
            'date': self.date,
            'type': self.dish_type,
            'owner': self.owner.to_dict() if self.owner else None
        }

# Initialize data
dishes = []
total_points = 0
start_date_str = "2024-09-19"
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

# Define the owners with Person objects
owners = {
    'ted': Person(name='ted', user_id='86703628', points=0),
    'dominic': Person(name='dominic', user_id='104427870', points=0),
    'truman': Person(name='truman', user_id='106396551', points=0),
    'dimov': Person(name='dimov', user_id='104722123', points=0),
    'david': Person(name='david', user_id='68279200', points=0),
    'mat': Person(name='mat', user_id='107719028', points=0),
    'christian': Person(name='christian', user_id='93350644', points=0),
    'diego': Person(name='diego', user_id='118125359', points=0),
    'az': Person(name='az', user_id='105887162', points=0),
    'leif': Person(name='leif', user_id='89734509', points=0),
    'john': Person(name='john', user_id='71913836', points=0),
    'tony': Person(name='tony', user_id='115601455', points=0),
    'arohan': Person(name='arohan', user_id='115802749', points=0),
    'stanley': Person(name='stanley', user_id='65365057', points=0),
    'eyen': Person(name='eyen', user_id='115945245', points=0),
    'brandon': Person(name='brandon', user_id='117008618', points=0),
    'jo': Person(name='jo', user_id='125330287', points=0),
    'jase': Person(name='jase', user_id='123732691', points=0),
    'sam': Person(name='sam', user_id='119855908', points=0),
    'tanner': Person(name='tanner', user_id='125114421', points=0),
    'noah': Person(name='noah', user_id='107162478', points=0),
    'aidan': Person(name='aidan', user_id='23716109', points=0),
    'kim': Person(name='kim', user_id='123717364', points=0),
}

i = 0
while current_date <= end_date:
    day_of_week = current_date.strftime("%A")

    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1
            total_points += 1

        owner_name = ownersArray[i]
        owner = owners.get(owner_name, None)

        dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner=owner, dish_type=types[type_index])
        dishes.append(dish)
        i += 1

        if types[type_index] == 'x1':
            current_date += delta

        type_index = (type_index + 1) % len(types)

    else:
        current_date += delta

grouped_dishes = defaultdict(lambda: defaultdict(list))
for dish in dishes:
    if dish.dish_type == 'dinner' or dish.dish_type == 'lunch':
        total_points += 2
    elif dish.dish_type == 'x1':
        total_points += 1
    month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
    day = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%d")
    grouped_dishes[month][day].append(dish)

points = total_points / len(owners)

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
                if dish.dish_type == "lunch":
                    today_lunch = dish
                elif dish.dish_type == "dinner":
                    today_dinner = dish
                elif dish.dish_type == "x1":
                    today_x1 = dish

        lunch_owner = today_lunch.owner if today_lunch and today_lunch.owner else 'Not Assigned'
        dinner_owner = today_dinner.owner if today_dinner and today_dinner.owner else 'Not Assigned'
        x1_owner = today_x1.owner if today_x1 and today_x1.owner else 'Not Assigned'

        lunch_message = f"Lunch: @{lunch_owner.name if lunch_owner != 'Not Assigned' else 'Not Assigned'}"
        dinner_message = f"Dinner: @{dinner_owner.name if dinner_owner != 'Not Assigned' else 'Not Assigned'}"
        x1_message = f"x1: @{x1_owner.name if x1_owner != 'Not Assigned' else 'Not Assigned'}"

        url = "https://api.groupme.com/v3/bots/post"

        def send_message(message, user_id=None):
            data = {
                "text": message,
                "bot_id": "c9ed078f3de7c89547308a050a"
            }
            if user_id:
                data["attachments"] = [{
                    "type": "mentions",
                    "user_ids": [user_id],
                    "loci": [[7, 7 + len(lunch_owner.name)]] if message == lunch_message else
                            [[8, 8 + len(dinner_owner.name)]] if message == dinner_message else
                            [[4, 4 + len(x1_owner.name)]]
                }]
            response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            return response

        lunch_user_id = lunch_owner.user_id if lunch_owner != 'Not Assigned' else None
        dinner_user_id = dinner_owner.user_id if dinner_owner != 'Not Assigned' else None
        x1_user_id = x1_owner.user_id if x1_owner != 'Not Assigned' else None

        send_message(lunch_message, lunch_user_id)
        send_message(dinner_message, dinner_user_id)
        send_message(x1_message, x1_user_id)

    return render_template('index.html', grouped_dishes=grouped_dishes, user=user, points=points)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['user'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/change-owner', methods=['POST'])
def change_owner():
    data = request.get_json()
    dish_date = data.get('date')
    dish_type = data.get('type')
    new_owner_name = data.get('owner')

    for index, dish in enumerate(dishes):
        if dish.date == dish_date and dish.dish_type == dish_type:
            new_owner = owners.get(new_owner_name, None)
            dish.owner = new_owner
            ownersArray[index] = new_owner_name
            return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Dish not found'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
