from flask import Flask, render_template, send_file
import datetime
from collections import defaultdict
from dish import Dish
import requests
import json
import jsonify
import pandas as pd
import io


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
today = datetime.date.today().strftime('%Y-%m-%d')

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
    data = requests.get_json()
    dish_date = data.get('date')
    dish_type = data.get('type')
    new_owner = data.get('owner')

    # Find the dish that matches the date and type
    for dish in dishes:
        if dish.date == dish_date and dish.type == dish_type:
            dish.owner = new_owner
            break
    else:
        return jsonify({'success': False, 'message': 'Dish not found'}), 404

    return jsonify({'success': True})

@app.route('/download-spreadsheet')
def download_spreadsheet():
    # Create a DataFrame
    df = pd.DataFrame([{
        'Date': dish.date,
        'Type': dish.type,
        'Owner': dish.owner
    } for dish in dishes])
    
    # Save the DataFrame to a BytesIO object
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dishes')
    
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name='dishes.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)