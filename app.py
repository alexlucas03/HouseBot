from flask import Flask, render_template
import datetime
from dish import Dish
from groupy.client import Client

client = Client.from_token("JkI3aAERgvJtCe9ePajw9YkNZu6KFwrpNgL628YZ")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Initial Data Setup
dishes = []
startDate = "2024-09-15"
endDate = "2024-12-08"
start_date_obj = datetime.datetime.strptime(startDate, "%Y-%m-%d")
end_date_obj = datetime.datetime.strptime(endDate, "%Y-%m-%d")

types = ['lunch', 'dinner', 'x1']
typeIndex = 0

delta = datetime.timedelta(days=1)
current_date = start_date_obj

while current_date <= end_date_obj:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner="x", type=types[typeIndex])
        dishes.append(dish)
        typeIndex = (typeIndex + 1) % 3

    current_date += delta


@app.route('/')
def index():
    return render_template('index.html', dishes=dishes)


# Function to get today's dishes
def get_todays_dishes():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_dishes = [dish for dish in dishes if dish.date == today_str]
    return today_dishes


# GroupMe bot integration to send today's dishes
@app.route('/send-todays-dishes')
def send_todays_dishes():
    today_dishes = get_todays_dishes()

    if not today_dishes:
        message = "No dishes scheduled for today."
    else:
        message = "Today's dishes:\n" + "\n".join([f"{dish.type} on {dish.date}" for dish in today_dishes])

    # Send the message to GroupMe using groupyapi (assuming the bot setup is done)
    message = dishes.post(text=message)

    return f"Sent: {message}"


if __name__ == '__main__':
    app.run(debug=True)
