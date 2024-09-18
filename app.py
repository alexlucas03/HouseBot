from flask import Flask, render_template, request, jsonify
import datetime
from collections import defaultdict
from dish import Dish
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Initial Data Setup
dishes = []
start_date_str = "2024-09-17"
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
i = 0
while current_date <= end_date:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1

        owner = ownersArray[i]  # Get the owner from the ownersArray
        
        dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner=owner, type=types[type_index])
        dishes.append(dish)
        i += 1
        
        if types[type_index] == 'x1':
            current_date += delta
        
        type_index = (type_index + 1) % len(types)
 
    else:
        current_date += delta

# Group dishes by month
grouped_dishes = defaultdict(lambda: defaultdict(list))
for dish in dishes:
    month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
    day = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%d")
    grouped_dishes[month][day].append(dish)

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

    # Mention formatting
    lunch_owner = f"{today_lunch.owner}" if today_lunch else 'None'
    dinner_owner = f"{today_dinner.owner}" if today_dinner else 'None'
    x1_owner = f"{today_x1.owner}" if today_x1 else 'None'

    message = f"Lunch: @{lunch_owner}\nDinner: @{dinner_owner}\nx1: @{x1_owner}"

    url = "https://api.groupme.com/v3/bots/post"

    # Data to send in the POST request
    data = {
        "text": message,
        "bot_id": "c9ed078f3de7c89547308a050a",
        "attachments": [
            {
            "type": "mentions",
            "user_ids": [f"{lunch_owner}", f"{dinner_owner}", f"{x1_owner}"],
            "loci": [
                [7, 7 + len(lunch_owner)],
                [17 + len(lunch_owner), 17 + len(lunch_owner) + len(dinner_owner)],
                [23 + len(lunch_owner) + len(dinner_owner), 23 + len(lunch_owner) + len(dinner_owner) + len(x1_owner)]
            ]
            }
        ]
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

    # Find the dish that matches the date and type
    for index, dish in enumerate(dishes):
        if dish.date == dish_date and dish.type == dish_type:
            dish.owner = new_owner  # Update the owner
            
            # Update the ownersArray
            ownersArray[index] = new_owner
            return jsonify({'success': True})  # Correct use of jsonify

    return jsonify({'success': False, 'message': 'Dish not found'}), 404

