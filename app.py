from flask import Flask, render_template
import datetime
from collections import defaultdict
from dish import Dish
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

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
today = datetime.today().strftime('%Y-%m-%d')

while current_date <= end_date:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1

        dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner="x", type=types[type_index])
        dishes.append(dish)
        
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
    today = datetime.datetime.today().strftime('%Y-%m-%d')

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

# Function to get today's dishes
def get_todays_dishes():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_dishes = [dish for dish in dishes if dish.date == today_str]
    return today_dishes

if __name__ == '__main__':
    app.run(debug=True)
