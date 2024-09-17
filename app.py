from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from collections import defaultdict
from dish import Dish
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@hostname/database'
db = SQLAlchemy(app)

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    dish_type = db.Column(db.String(10), nullable=False)
    owner_name = db.Column(db.String(100))

# Create the database tables
with app.app_context():
    db.create_all()

# Initial Data Setup
dishes = []
start_date_str = "2024-09-15"
end_date_str = "2024-12-08"
start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

types = ['lunch', 'dinner', 'x1']
type_index = 0

delta = datetime.timedelta(days=1)
current_date = start_date
today = datetime.date.today().strftime('%Y-%m-%d')
i = 0
while current_date <= end_date:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1

        # Fetch the owner from the database
        owner_record = Owner.query.filter_by(date=current_date.strftime("%Y-%m-%d"), dish_type=types[type_index]).first()
        owner = owner_record.owner_name if owner_record else None
        
        dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner=owner, type=types[type_index])
        dishes.append(dish)
        i += 1
        
        if types[type_index] == 'x1':
            current_date += delta
        
        type_index = (type_index + 1) % len(types)
 
    else:
        current_date += delta

# Group dishes by month
grouped_dishes = defaultdict(list)
for dish in dishes:
    month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
    grouped_dishes[month].append(dish)

@app.route('/')
def index():
    today_lunch = None
    today_dinner = None
    today_x1 = None
    today = datetime.date.today().strftime('%Y-%m-%d')

    for dish in dishes:
        if dish.date == today:
            if dish.type == "lunch":
                today_lunch = dish
            elif dish.type == "dinner":
                today_dinner = dish
            elif dish.type == "x1":
                today_x1 = dish

    message = f"Lunch: {today_lunch.owner if today_lunch else 'None'} \n" \
              f"Dinner: {today_dinner.owner if today_dinner else 'None'} \n" \
              f"x1: {today_x1.owner if today_x1 else 'None'}"

    url = "https://api.groupme.com/v3/bots/post"

    # Data to send in the POST request
    data = {
        "text": message,
        "bot_id": "c9ed078f3de7c89547308a050a"
    }  
    # Send the POST request
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

    # Print the response
    print(response.text)

    return render_template('index.html', grouped_dishes=grouped_dishes)

@app.route('/change-owner', methods=['POST'])
def change_owner():
    data = request.get_json()  # Get the JSON data from the request
    dish_date = data.get('date')
    dish_type = data.get('type')
    new_owner = data.get('owner')

    # Find the dish in the database and update the owner
    owner_record = Owner.query.filter_by(date=dish_date, dish_type=dish_type).first()

    if owner_record:
        owner_record.owner_name = new_owner
    else:
        owner_record = Owner(date=dish_date, dish_type=dish_type, owner_name=new_owner)
        db.session.add(owner_record)

    db.session.commit()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
